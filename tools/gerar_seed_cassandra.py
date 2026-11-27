"""Gera cassandra/02_seed.cql a partir do contrato de dados do grupo.

A quantidade de reproduções de cada (usuário, música) é a MESMA do peso
`vezes` da aresta :OUVIU no seed_neo4j.cypher, para que os 4 bancos batam:
o histórico do Cassandra é a fonte dos eventos e o grafo é o consolidado.

Uso:  python tools/gerar_seed_cassandra.py
"""
from datetime import datetime, timedelta
from pathlib import Path

# Duração de cada faixa (segundos) — mesmo valor deve ser usado no MongoDB
DURACAO = {401: 213, 872: 198, 122: 245, 553: 201,
           610: 227, 611: 189, 612: 176, 613: 204}

TITULO = {401: "Midnight Drive", 872: "Static Waves", 122: "City Lights",
          553: "Paper Planes", 610: "Solar Flare", 611: "Electric Rain",
          612: "Quiet Horizon", 613: "Night Bus"}

USUARIOS = {9921: "Ana", 9922: "Bruno", 9923: "Carla", 9924: "Diego"}

# (usuario_id) -> {musica_id: vezes}  — idêntico ao seed_neo4j.cypher
OUVIU = {
    9921: {401: 5, 872: 3, 122: 2, 553: 1},
    9922: {401: 4, 872: 6, 610: 7, 611: 3},
    9923: {122: 5, 553: 2, 610: 8, 612: 4},
    9924: {612: 6, 613: 5},
}

# As 4 reproduções mais recentes da Ana são exatamente as do relatório (3.2.1)
ANA_RECENTES = [
    (datetime(2026, 9, 19, 18, 0, 0), 401),
    (datetime(2026, 9, 19, 17, 55, 0), 872),
    (datetime(2026, 9, 19, 17, 51, 0), 122),
    (datetime(2026, 9, 19, 17, 47, 0), 553),
]


def eventos_do_usuario(uid):
    restantes = dict(OUVIU[uid])
    eventos = []
    if uid == 9921:
        for ts, mid in ANA_RECENTES:
            eventos.append((ts, mid))
            restantes[mid] -= 1
    # Demais reproduções: espalhadas nos dias anteriores, no pico 17h-19h
    fila = []
    while any(v > 0 for v in restantes.values()):
        for mid in sorted(restantes):
            if restantes[mid] > 0:
                fila.append(mid)
                restantes[mid] -= 1
    inicio = datetime(2026, 9, 18, 18, 30, 0) - timedelta(minutes=(uid - 9921) * 7)
    for i, mid in enumerate(fila):
        dia = i // 4                     # 4 faixas por dia
        ts = inicio - timedelta(days=dia, minutes=(i % 4) * 5)
        eventos.append((ts, mid))
    return sorted(eventos, reverse=True)


def main():
    linhas = [
        "-- VibeStream — Marco 1 — Cassandra: massa de dados inicial (seed)",
        "-- GERADO por tools/gerar_seed_cassandra.py — não editar à mão.",
        "-- Contagens por (usuário, música) = peso 'vezes' das arestas :OUVIU do Neo4j.",
        "-- Horários gravados em UTC (+0000).",
        "",
        "USE vibestream;",
        "",
    ]
    total = 0
    for uid, nome in USUARIOS.items():
        evs = eventos_do_usuario(uid)
        linhas.append(f"-- {uid} — {nome} ({len(evs)} reproduções)")
        for ts, mid in evs:
            linhas.append(
                "INSERT INTO historico_usuario (usuario_id, data_reproducao, musica_id, duracao_segundos) "
                f"VALUES ({uid}, '{ts:%Y-%m-%d %H:%M:%S}+0000', {mid}, {DURACAO[mid]});"
                f"  -- {TITULO[mid]}"
            )
        linhas.append("")
        total += len(evs)
    destino = Path(__file__).resolve().parent.parent / "cassandra" / "02_seed.cql"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"{total} registros gravados em {destino}")


if __name__ == "__main__":
    main()
