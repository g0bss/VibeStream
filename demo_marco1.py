"""VibeStream — Demo do Marco 1 (Redis + Cassandra) para o seminário.

Pré-requisito:  docker compose up -d   (e aguardar o Cassandra ficar healthy)
Rodar:          python demo_marco1.py

Fluxo (seção 3.7 do relatório), usuário 9921 (Ana):
  1. Lê a sessão atual no Redis (HGETALL + TTL)
  2. Simula heartbeats do player (HSET tempo_reproducao + renovação do TTL)
  3. Pausa e retoma (HSET estado)
  4. Conclusão da faixa -> append no histórico do Cassandra
  5. Consulta "últimas 50 músicas" (WHERE usuario_id = ? LIMIT 50)
"""
from cassandra_service import CassandraService
from redis_service import RedisService

USUARIO = 9921
DURACAO = {401: 213, 872: 198, 122: 245, 553: 201, 610: 227, 611: 189, 612: 176, 613: 204}


def titulo(texto):
    print(f"\n{'=' * 60}\n{texto}\n{'=' * 60}")


def main():
    rds = RedisService()
    cass = CassandraService()
    try:
        rds.aplicar_seed()
        cass.aplicar_schema_e_seed()

        titulo("1) REDIS — HGETALL sessao:usuario:9921")
        print(rds.obter_sessao(USUARIO))

        titulo("2) REDIS — heartbeats do player (HSET + EXPIRE 1800)")
        for seg in (106, 107, 108):
            rds.atualizar_tempo(USUARIO, seg)
            s = rds.obter_sessao(USUARIO)
            print(f"tempo_reproducao={s['tempo_reproducao']}  ttl={s['ttl_segundos']}s")

        titulo("3) REDIS — pause / play")
        rds.pausar(USUARIO)
        print("estado:", rds.obter_sessao(USUARIO)["estado"])
        rds.retomar(USUARIO)
        print("estado:", rds.obter_sessao(USUARIO)["estado"])

        titulo("4) Faixa concluída -> CASSANDRA (append no histórico)")
        sessao = rds.obter_sessao(USUARIO)
        mid = sessao["musica_atual"]
        evento = cass.registrar_reproducao(USUARIO, mid, DURACAO[mid])
        print(f"INSERT: usuario_id={evento['usuario_id']} musica_id={evento['musica_id']} "
              f"duracao={evento['duracao_segundos']}s data={evento['data_reproducao']:%Y-%m-%d %H:%M:%S} UTC")
        # Próxima faixa entra no lugar no Redis
        print("Nova sessão:", rds.iniciar_reproducao(USUARIO, 872))

        titulo("5) CASSANDRA — SELECT * FROM historico_usuario WHERE usuario_id = 9921 LIMIT 50")
        print(f"{'data_reproducao':<22}{'musica_id':>10}{'duracao':>10}")
        for r in cass.ultimas_musicas(USUARIO, 50):
            print(f"{r['data_reproducao']:%Y-%m-%d %H:%M:%S}  {r['musica_id']:>10}{r['duracao_segundos']:>9}s")
        print("\nIDs distintos (para MongoDB/Neo4j):", cass.musicas_ouvidas_ids(USUARIO))
    finally:
        rds.close()
        cass.close()


if __name__ == "__main__":
    main()
