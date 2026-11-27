"""VibeStream — Marco 1 — Estado atual da reprodução no Redis (Hash + TTL).

Chave:   sessao:usuario:<usuario_id>
Campos:  musica_atual (int, ex.: 401) | tempo_reproducao ("MM:SS") | estado (playing|paused)
TTL:     1800 s (30 min), renovado a cada atualização (heartbeat do player)

Variáveis de ambiente: REDIS_HOST (localhost), REDIS_PORT (6379)
"""
import os
from pathlib import Path

import redis

TTL_SESSAO = 1800  # 30 minutos
ESTADOS_VALIDOS = {"playing", "paused"}


def _chave(usuario_id: int) -> str:
    return f"sessao:usuario:{int(usuario_id)}"


def formatar_tempo(segundos: int) -> str:
    """125 -> '02:05'"""
    segundos = max(0, int(segundos))
    return f"{segundos // 60:02d}:{segundos % 60:02d}"


class RedisService:
    def __init__(self, host=None, port=None):
        self.client = redis.Redis(
            host=host or os.getenv("REDIS_HOST", "localhost"),
            port=int(port or os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
        )

    def close(self):
        self.client.close()

    # ---------------------------------------------------------------- seed
    def aplicar_seed(self, caminho_arquivo="redis/seed_redis.redis"):
        """Executa os comandos do arquivo de seed (um comando por linha)."""
        for linha in Path(caminho_arquivo).read_text(encoding="utf-8").splitlines():
            partes = linha.split()
            if partes and not partes[0].startswith("#"):
                self.client.execute_command(*partes)

    # ------------------------------------------------------------- escrita
    def iniciar_reproducao(self, usuario_id: int, musica_id: int, tempo: str = "00:00") -> dict:
        """Play em uma faixa: HSET dos 3 campos + EXPIRE, em uma transação (MULTI/EXEC)."""
        chave = _chave(usuario_id)
        pipe = self.client.pipeline(transaction=True)
        pipe.hset(chave, mapping={
            "musica_atual": int(musica_id),
            "tempo_reproducao": tempo,
            "estado": "playing",
        })
        pipe.expire(chave, TTL_SESSAO)
        pipe.execute()
        return self.obter_sessao(usuario_id)

    def atualizar_tempo(self, usuario_id: int, tempo) -> bool:
        """Heartbeat do player: altera só tempo_reproducao e renova o TTL.
        `tempo` pode ser 'MM:SS' ou segundos (int). Retorna False se não há sessão."""
        if isinstance(tempo, int):
            tempo = formatar_tempo(tempo)
        return self._atualizar_campo(usuario_id, "tempo_reproducao", tempo)

    def alterar_estado(self, usuario_id: int, estado: str) -> bool:
        if estado not in ESTADOS_VALIDOS:
            raise ValueError(f"estado deve ser um de {ESTADOS_VALIDOS}")
        return self._atualizar_campo(usuario_id, "estado", estado)

    def pausar(self, usuario_id: int) -> bool:
        return self.alterar_estado(usuario_id, "paused")

    def retomar(self, usuario_id: int) -> bool:
        return self.alterar_estado(usuario_id, "playing")

    def encerrar_sessao(self, usuario_id: int) -> bool:
        return self.client.delete(_chave(usuario_id)) == 1

    def _atualizar_campo(self, usuario_id, campo, valor) -> bool:
        chave = _chave(usuario_id)
        if not self.client.exists(chave):
            return False  # sessão expirou: o player deve chamar iniciar_reproducao de novo
        pipe = self.client.pipeline(transaction=True)
        pipe.hset(chave, campo, valor)
        pipe.expire(chave, TTL_SESSAO)
        pipe.execute()
        return True

    # ------------------------------------------------------------- leitura
    def obter_sessao(self, usuario_id: int):
        """HGETALL + TTL. Retorna None se a sessão não existe (ou expirou)."""
        chave = _chave(usuario_id)
        dados = self.client.hgetall(chave)
        if not dados:
            return None
        dados["musica_atual"] = int(dados["musica_atual"])
        dados["usuario_id"] = int(usuario_id)
        dados["ttl_segundos"] = self.client.ttl(chave)
        return dados


if __name__ == "__main__":
    svc = RedisService()
    try:
        svc.aplicar_seed()
        print("=== Sessão atual da Ana (9921) ===")
        print(svc.obter_sessao(9921))
    finally:
        svc.close()
