-- VibeStream — Marco 1 — Cassandra: keyspace e tabela de histórico
--
-- AMBIENTE LOCAL (Docker, 1 nó): SimpleStrategy com replication_factor 1.
-- Com um único nó não existe onde guardar 3 cópias; RF 3 com 1 nó faria
-- qualquer consulta com consistência QUORUM falhar.
--
-- PRODUÇÃO (arquitetura proposta no relatório): fator de replicação 3 por
-- datacenter, por exemplo:
--   CREATE KEYSPACE vibestream
--     WITH replication = {'class': 'NetworkTopologyStrategy', 'dc1': 3};

CREATE KEYSPACE IF NOT EXISTS vibestream
  WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE vibestream;

-- Query-first: "quais foram as últimas 50 músicas que o usuário X ouviu?"
--   Partition Key  -> usuario_id        (localiza a partição / o nó do usuário)
--   Clustering Col -> data_reproducao   (ordem física DESC dentro da partição)
CREATE TABLE IF NOT EXISTS historico_usuario (
    usuario_id        INT,
    data_reproducao   TIMESTAMP,
    musica_id         INT,
    duracao_segundos  INT,
    PRIMARY KEY (usuario_id, data_reproducao)
) WITH CLUSTERING ORDER BY (data_reproducao DESC);
