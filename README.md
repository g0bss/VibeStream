# VibeStream

Arquitetura de persistência poliglota NoSQL para uma plataforma de streaming de música, distribuindo responsabilidades entre diferentes famílias de bancos de dados conforme o padrão de acesso de cada operação.

## Arquitetura

| Família | Tecnologia | Responsabilidade |
| :--- | :--- | :--- |
| Chave-Valor | Redis | Estado atual da reprodução (Hash + TTL) |
| Wide-Column | Cassandra | Histórico de reproduções (*query-first*, *append-only*) |
| Documentos | MongoDB | Catálogo de músicas, artistas, álbuns e playlists |
| Grafos | Neo4j | Motor de recomendações baseado em relacionamentos |

## Motor de Recomendações (Neo4j)

O grafo armazena apenas identificadores leves e conexões relevantes para travessia, integrando-se aos demais bancos por meio de `usuario_id`, `musica_id` e `artista_id`:

- **Nós:** `:Usuario`, `:Musica`, `:Artista`, `:Genero`
- **Relacionamentos:** `:OUVIU`, `:SEGUE`, `:CRIOU`, `:PERTENCE_A`

## Ambiente local (Docker)

Pré-requisitos: Docker Desktop (ou Docker Engine + Compose v2) e Python 3.10+.

```bash
docker compose up -d          # sobe Redis, Cassandra, MongoDB e Neo4j na rede vibestream-net
docker compose ps             # cassandra leva ~1-2 min para ficar "healthy"
pip install -r requirements.txt
```

| Serviço | Porta(s) | Acesso | Carga inicial |
| :--- | :--- | :--- | :--- |
| Redis 7 | 6379 | sem senha | `redis-seed` aplica `redis/seed_redis.redis` |
| Cassandra 4.1 | 9042 | sem senha | `cassandra-seed` aplica `cassandra/01_schema.cql` e `02_seed.cql` |
| MongoDB 7 | 27017 | sem senha, banco `vibestream` | scripts em `mongo/init/` (só na 1ª subida) |
| Neo4j 5 | 7474 (browser), 7687 (bolt) | `neo4j` / `vibestream123` | `neo4j_service.py` → `aplicar_seed()` |

Os containers `redis-seed` e `cassandra-seed` rodam uma vez e terminam com `exited (0)` — isso é esperado.
Para zerar tudo: `docker compose down -v && docker compose up -d`.

## Marco 1 — Redis + Cassandra

**Redis — `sessao:usuario:<usuario_id>` (Hash, TTL 1800 s)**

```
HSET sessao:usuario:9921 musica_atual 401 tempo_reproducao 01:45 estado playing
EXPIRE sessao:usuario:9921 1800
HGETALL sessao:usuario:9921
TTL sessao:usuario:9921
```

**Cassandra — `vibestream.historico_usuario`**

```sql
SELECT * FROM vibestream.historico_usuario WHERE usuario_id = 9921 LIMIT 50;
```

Testar direto nos containers:

```bash
docker exec -it vibestream-redis redis-cli HGETALL sessao:usuario:9921
docker exec -it vibestream-cassandra cqlsh -e "SELECT * FROM vibestream.historico_usuario WHERE usuario_id = 9921 LIMIT 50;"
```

Funções para a integração (Membro 4):

| Módulo | Função | Uso no fluxo |
| :--- | :--- | :--- |
| `redis_service.py` | `iniciar_reproducao(uid, mid)` | play em uma faixa |
| | `atualizar_tempo(uid, segundos_ou_"MM:SS")` | heartbeat do player (renova TTL) |
| | `pausar(uid)` / `retomar(uid)` | pause / play |
| | `obter_sessao(uid)` | tela "tocando agora" (`None` se expirou) |
| | `encerrar_sessao(uid)` | logout |
| `cassandra_service.py` | `registrar_reproducao(uid, mid, duracao)` | faixa concluída → histórico |
| | `ultimas_musicas(uid, limite=50)` | tela de histórico |
| | `musicas_ouvidas_ids(uid)` | IDs para cruzar com MongoDB / Neo4j |
| `neo4j_service.py` | `aplicar_seed()` | aplica constraints e `seed_neo4j.cypher` |
| | `recomendar_por_usuarios_similares(uid, limite=5)` | filtragem colaborativa (3 saltos) |
| | `recomendar_por_genero(uid, limite=5)` | recomendação por afinidade de gênero |
| | `registrar_reproducao(uid, mid)` | incrementa `r.vezes` na aresta `:OUVIU` |

Demo ponta a ponta do Marco 1: `python demo_marco1.py`.

### Contrato de dados (igual nos 4 bancos)

- `usuario_id`: 9921 Ana, 9922 Bruno, 9923 Carla, 9924 Diego
- `artista_id`: 10 Neon Pulse, 11 Velvet Echo, 12 Solar Drift
- `musica_id` é **inteiro** em todos os bancos (401, não `id_401`)

| musica_id | Título | Artista | Gênero | Duração (s) |
| :--- | :--- | :--- | :--- | :--- |
| 401 | Midnight Drive | Neon Pulse | Indie Rock | 213 |
| 872 | Static Waves | Neon Pulse | Indie Rock | 198 |
| 122 | City Lights | Velvet Echo | Synthpop | 245 |
| 553 | Paper Planes | Velvet Echo | Indie Rock | 201 |
| 610 | Solar Flare | Velvet Echo | Indie Rock | 227 |
| 611 | Electric Rain | Neon Pulse | Synthpop | 189 |
| 612 | Quiet Horizon | Solar Drift | Lo-Fi | 176 |
| 613 | Night Bus | Solar Drift | Lo-Fi | 204 |

O histórico do Cassandra tem, para cada par (usuário, música), o mesmo número de linhas que o peso `vezes` da aresta `:OUVIU` no Neo4j (Ana: 401×5, 872×3, 122×2, 553×1). O seed é gerado por `tools/gerar_seed_cassandra.py`.
