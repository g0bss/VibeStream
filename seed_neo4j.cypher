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

MERGE (u1)-[o1:OUVIU]->(m1) SET o1.vezes = 5
MERGE (u1)-[o2:OUVIU]->(m2) SET o2.vezes = 3
MERGE (u1)-[o3:OUVIU]->(m3) SET o3.vezes = 2
MERGE (u1)-[o4:OUVIU]->(m4) SET o4.vezes = 1

MERGE (u2)-[o5:OUVIU]->(m1) SET o5.vezes = 4
MERGE (u2)-[o6:OUVIU]->(m2) SET o6.vezes = 6
MERGE (u2)-[o7:OUVIU]->(m5) SET o7.vezes = 7
MERGE (u2)-[o8:OUVIU]->(m6) SET o8.vezes = 3

MERGE (u3)-[o9:OUVIU]->(m3) SET o9.vezes = 5
MERGE (u3)-[o10:OUVIU]->(m4) SET o10.vezes = 2
MERGE (u3)-[o11:OUVIU]->(m5) SET o11.vezes = 8
MERGE (u3)-[o12:OUVIU]->(m7) SET o12.vezes = 4

MERGE (u4)-[o13:OUVIU]->(m7) SET o13.vezes = 6
MERGE (u4)-[o14:OUVIU]->(m8) SET o14.vezes = 5;
