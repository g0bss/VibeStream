import os
from pathlib import Path
from neo4j import GraphDatabase


class Neo4jService:
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "vibestream123")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def aplicar_seed(self, caminho_arquivo="seed_neo4j.cypher"):
        conteudo = Path(caminho_arquivo).read_text(encoding="utf-8")
        # Remove linhas de comentário e separa comandos por ponto e vírgula
        linhas = [l for l in conteudo.splitlines() if not l.strip().startswith("//")]
        comandos = [c.strip() for c in "\n".join(linhas).split(";") if c.strip()]

        with self.driver.session() as session:
            for cmd in comandos:
                session.run(cmd)

    def recomendar_por_usuarios_similares(self, usuario_id: int, limite: int = 5):
        query = """
        MATCH (u:Usuario {usuario_id: $uid})-[:OUVIU]->(:Musica)<-[:OUVIU]-(outro:Usuario)-[:OUVIU]->(rec:Musica)
        WHERE u <> outro AND NOT (u)-[:OUVIU]->(rec)
        OPTIONAL MATCH (a:Artista)-[:CRIOU]->(rec)
        RETURN rec.musica_id AS musica_id,
               rec.titulo AS titulo,
               a.nome AS artista,
               count(DISTINCT outro) AS relevancia
        ORDER BY relevancia DESC, rec.musica_id ASC
        LIMIT $limite
        """
        with self.driver.session() as session:
            result = session.run(query, uid=usuario_id, limite=limite)
            return [record.data() for record in result]

    def recomendar_por_genero(self, usuario_id: int, limite: int = 5):
        query = """
        MATCH (u:Usuario {usuario_id: $uid})-[:OUVIU]->(:Musica)-[:PERTENCE_A]->(g:Genero)<-[:PERTENCE_A]-(rec:Musica)
        WHERE NOT (u)-[:OUVIU]->(rec)
        OPTIONAL MATCH (a:Artista)-[:CRIOU]->(rec)
        RETURN rec.musica_id AS musica_id,
               rec.titulo AS titulo,
               a.nome AS artista,
               g.nome AS genero,
               count(*) AS score
        ORDER BY score DESC, rec.musica_id ASC
        LIMIT $limite
        """
        with self.driver.session() as session:
            result = session.run(query, uid=usuario_id, limite=limite)
            return [record.data() for record in result]

    def registrar_reproducao(self, usuario_id: int, musica_id: int):
        query = """
        MATCH (u:Usuario {usuario_id: $uid}), (m:Musica {musica_id: $mid})
        MERGE (u)-[r:OUVIU]->(m)
        ON CREATE SET r.vezes = 1, r.ultima_vez = datetime()
        ON MATCH SET r.vezes = r.vezes + 1, r.ultima_vez = datetime()
        RETURN u.usuario_id AS usuario_id, m.musica_id AS musica_id, r.vezes AS vezes
        """
        with self.driver.session() as session:
            result = session.run(query, uid=usuario_id, mid=musica_id)
            registro = result.single()
            return registro.data() if registro else None


if __name__ == "__main__":
    service = Neo4jService()
    try:
        service.aplicar_seed()
        print("=== Recomendações Colaborativas (Usuário 9921) ===")
        for item in service.recomendar_por_usuarios_similares(9921):
            print(item)

        print("\n=== Recomendações por Gênero (Usuário 9921) ===")
        for item in service.recomendar_por_genero(9921):
            print(item)
    finally:
        service.close()
