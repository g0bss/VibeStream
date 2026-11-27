"""VibeStream — Marco 1 — Histórico de reprodução no Cassandra (query-first).

Tabela: vibestream.historico_usuario
  PRIMARY KEY (usuario_id, data_reproducao)  CLUSTERING ORDER BY (data_reproducao DESC)

Variáveis de ambiente: CASSANDRA_HOST (localhost), CASSANDRA_PORT (9042)
"""
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from cassandra.cluster import Cluster, NoHostAvailable

KEYSPACE = "vibestream"


def _comandos_cql(caminho: str):
    """Lê um arquivo .cql, remove comentários '--' e separa por ';'."""
    linhas = []
    for linha in Path(caminho).read_text(encoding="utf-8").splitlines():
        if "--" in linha:
            linha = linha[: linha.index("--")]
        linhas.append(linha)
    return [c.strip() for c in "\n".join(linhas).split(";") if c.strip()]


class CassandraService:
    def __init__(self, host=None, port=None, tentativas=20, espera=5):
        self.cluster = Cluster(
            [host or os.getenv("CASSANDRA_HOST", "localhost")],
            port=int(port or os.getenv("CASSANDRA_PORT", 9042)),
        )
        # O Cassandra demora para aceitar conexões na primeira subida do container
        for tentativa in range(1, tentativas + 1):
            try:
                self.session = self.cluster.connect()
                break
            except NoHostAvailable:
                if tentativa == tentativas:
                    raise
                print(f"[cassandra] aguardando o banco subir ({tentativa}/{tentativas})...")
                time.sleep(espera)
        self._insert = None
        self._select = None

    def close(self):
        self.cluster.shutdown()

    def _preparar(self):
        if self._insert is None:
            self.session.set_keyspace(KEYSPACE)
            self._insert = self.session.prepare(
                "INSERT INTO historico_usuario (usuario_id, data_reproducao, musica_id, duracao_segundos) "
                "VALUES (?, ?, ?, ?)"
            )
            self._select = self.session.prepare(
                "SELECT usuario_id, data_reproducao, musica_id, duracao_segundos "
                "FROM historico_usuario WHERE usuario_id = ? LIMIT ?"
            )

    # ---------------------------------------------------------------- seed
    def aplicar_schema_e_seed(self, pasta="cassandra"):
        """Cria keyspace/tabela e insere a massa inicial (idempotente: INSERT é upsert)."""
        for arquivo in ("01_schema.cql", "02_seed.cql"):
            for cmd in _comandos_cql(str(Path(pasta) / arquivo)):
                if cmd.upper().startswith("USE "):
                    self.session.set_keyspace(cmd.split()[1])
                else:
                    self.session.execute(cmd)
        self._insert = None  # força re-preparar após recriar a tabela

    # ------------------------------------------------------------- escrita
    def registrar_reproducao(self, usuario_id: int, musica_id: int, duracao_segundos: int,
                             data_reproducao: datetime = None) -> dict:
        """Append de um evento no histórico. Chamar quando a faixa é concluída/consumida."""
        self._preparar()
        data = data_reproducao or datetime.now(timezone.utc)
        self.session.execute(self._insert, (int(usuario_id), data, int(musica_id), int(duracao_segundos)))
        return {"usuario_id": int(usuario_id), "data_reproducao": data,
                "musica_id": int(musica_id), "duracao_segundos": int(duracao_segundos)}

    # ------------------------------------------------------------- leitura
    def ultimas_musicas(self, usuario_id: int, limite: int = 50) -> list:
        """'Quais foram as últimas N músicas que o usuário X ouviu?' (já vem em ordem DESC)."""
        self._preparar()
        linhas = self.session.execute(self._select, (int(usuario_id), int(limite)))
        return [
            {"usuario_id": r.usuario_id, "data_reproducao": r.data_reproducao,
             "musica_id": r.musica_id, "duracao_segundos": r.duracao_segundos}
            for r in linhas
        ]

    def musicas_ouvidas_ids(self, usuario_id: int, limite: int = 50) -> list:
        """IDs distintos (mais recentes primeiro) — útil para cruzar com MongoDB/Neo4j."""
        vistos = []
        for item in self.ultimas_musicas(usuario_id, limite):
            if item["musica_id"] not in vistos:
                vistos.append(item["musica_id"])
        return vistos


if __name__ == "__main__":
    svc = CassandraService()
    try:
        svc.aplicar_schema_e_seed()
        print("=== Últimas 50 músicas da Ana (9921) ===")
        for item in svc.ultimas_musicas(9921):
            print(item)
    finally:
        svc.close()
