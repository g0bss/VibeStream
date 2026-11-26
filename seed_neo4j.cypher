// Constraints de unicidade
CREATE CONSTRAINT usuario_id_unique IF NOT EXISTS FOR (u:Usuario) REQUIRE u.usuario_id IS UNIQUE;
CREATE CONSTRAINT musica_id_unique IF NOT EXISTS FOR (m:Musica) REQUIRE m.musica_id IS UNIQUE;
CREATE CONSTRAINT artista_id_unique IF NOT EXISTS FOR (a:Artista) REQUIRE a.artista_id IS UNIQUE;

// Carga de nós e relacionamentos (IDs alinhados com o Marco 1)
MERGE (u1:Usuario {usuario_id: 9921}) SET u1.nome = "Ana"
MERGE (u2:Usuario {usuario_id: 9922}) SET u2.nome = "Bruno"
MERGE (u3:Usuario {usuario_id: 9923}) SET u3.nome = "Carla"
MERGE (u4:Usuario {usuario_id: 9924}) SET u4.nome = "Diego"

MERGE (g1:Genero {nome: "Indie Rock"})
MERGE (g2:Genero {nome: "Synthpop"})
MERGE (g3:Genero {nome: "Lo-Fi"})

MERGE (a1:Artista {artista_id: 10}) SET a1.nome = "Neon Pulse"
MERGE (a2:Artista {artista_id: 11}) SET a2.nome = "Velvet Echo"
MERGE (a3:Artista {artista_id: 12}) SET a3.nome = "Solar Drift"

MERGE (m1:Musica {musica_id: 401}) SET m1.titulo = "Midnight Drive"
MERGE (m2:Musica {musica_id: 872}) SET m2.titulo = "Static Waves"
MERGE (m3:Musica {musica_id: 122}) SET m3.titulo = "City Lights"
MERGE (m4:Musica {musica_id: 553}) SET m4.titulo = "Paper Planes"
MERGE (m5:Musica {musica_id: 610}) SET m5.titulo = "Solar Flare"
MERGE (m6:Musica {musica_id: 611}) SET m6.titulo = "Electric Rain"
MERGE (m7:Musica {musica_id: 612}) SET m7.titulo = "Quiet Horizon"
MERGE (m8:Musica {musica_id: 613}) SET m8.titulo = "Night Bus"

MERGE (a1)-[:CRIOU]->(m1)
MERGE (a1)-[:CRIOU]->(m2)
MERGE (a1)-[:CRIOU]->(m6)
MERGE (a2)-[:CRIOU]->(m3)
MERGE (a2)-[:CRIOU]->(m4)
MERGE (a2)-[:CRIOU]->(m5)
MERGE (a3)-[:CRIOU]->(m7)
MERGE (a3)-[:CRIOU]->(m8)

MERGE (m1)-[:PERTENCE_A]->(g1)
MERGE (m2)-[:PERTENCE_A]->(g1)
MERGE (m3)-[:PERTENCE_A]->(g2)
MERGE (m4)-[:PERTENCE_A]->(g1)
MERGE (m5)-[:PERTENCE_A]->(g1)
MERGE (m6)-[:PERTENCE_A]->(g2)
MERGE (m7)-[:PERTENCE_A]->(g3)
MERGE (m8)-[:PERTENCE_A]->(g3)

MERGE (u1)-[:SEGUE]->(a1)
MERGE (u2)-[:SEGUE]->(a1)
MERGE (u2)-[:SEGUE]->(a2)
MERGE (u3)-[:SEGUE]->(a2)

MERGE (u1)-[:OUVIU {vezes: 5}]->(m1)
MERGE (u1)-[:OUVIU {vezes: 3}]->(m2)
MERGE (u1)-[:OUVIU {vezes: 2}]->(m3)
MERGE (u1)-[:OUVIU {vezes: 1}]->(m4)

MERGE (u2)-[:OUVIU {vezes: 4}]->(m1)
MERGE (u2)-[:OUVIU {vezes: 6}]->(m2)
MERGE (u2)-[:OUVIU {vezes: 7}]->(m5)
MERGE (u2)-[:OUVIU {vezes: 3}]->(m6)

MERGE (u3)-[:OUVIU {vezes: 5}]->(m3)
MERGE (u3)-[:OUVIU {vezes: 2}]->(m4)
MERGE (u3)-[:OUVIU {vezes: 8}]->(m5)
MERGE (u3)-[:OUVIU {vezes: 4}]->(m7)

MERGE (u4)-[:OUVIU {vezes: 6}]->(m7)
MERGE (u4)-[:OUVIU {vezes: 5}]->(m8);