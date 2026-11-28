db = db.getSiblingDB('vibestream');

// Índices de unicidade e busca rápida no catálogo
db.artistas.createIndex({ artista_id: 1 }, { unique: true });
db.musicas.createIndex({ musica_id: 1 }, { unique: true });
db.musicas.createIndex({ genero: 1 });
db.musicas.createIndex({ "artista.artista_id": 1 });
db.playlists.createIndex({ playlist_id: 1 }, { unique: true });
db.playlists.createIndex({ usuario_id: 1 });

// 1. Coleção de Artistas (com documentos embutidos de álbuns e metadados flexíveis)
db.artistas.insertMany([
  {
    artista_id: 10,
    nome: "Neon Pulse",
    pais: "Brasil",
    generos: ["Indie Rock", "Synthpop"],
    verificado: true,
    albuns: [
      {
        album_id: 101,
        titulo: "Nocturnal Frequencies",
        ano: 2025,
        capa_url: "https://cdn.vibestream.io/covers/101.jpg",
        faixas: [
          { musica_id: 401, titulo: "Midnight Drive", duracao_segundos: 213 },
          { musica_id: 872, titulo: "Static Waves", duracao_segundos: 198 },
          { musica_id: 611, titulo: "Electric Rain", duracao_segundos: 224 }
        ]
      }
    ]
  },
  {
    artista_id: 11,
    nome: "Velvet Echo",
    pais: "Reino Unido",
    generos: ["Indie Rock", "Synthpop"],
    verificado: true,
    albuns: [
      {
        album_id: 102,
        titulo: "Mirrors & Silhouettes",
        ano: 2026,
        capa_url: "https://cdn.vibestream.io/covers/102.jpg",
        faixas: [
          { musica_id: 122, titulo: "City Lights", duracao_segundos: 245 },
          { musica_id: 553, titulo: "Paper Planes", duracao_segundos: 201 },
          { musica_id: 610, titulo: "Solar Flare", duracao_segundos: 230 }
        ]
      }
    ]
  },
  {
    artista_id: 12,
    nome: "Solar Drift",
    pais: "Japão",
    generos: ["Lo-Fi"],
    verificado: true,
    albuns: [
      {
        album_id: 103,
        titulo: "Tokyo Rain 3AM",
        ano: 2026,
        capa_url: "https://cdn.vibestream.io/covers/103.jpg",
        faixas: [
          { musica_id: 612, titulo: "Quiet Horizon", duracao_segundos: 185 },
          { musica_id: 613, titulo: "Night Bus", duracao_segundos: 192 }
        ]
      }
    ]
  }
]);

// 2. Coleção de Músicas (Extended Reference + Esquema Polimórfico Flexível)
db.musicas.insertMany([
  {
    musica_id: 401,
    titulo: "Midnight Drive",
    genero: "Indie Rock",
    duracao_segundos: 213,
    artista: { artista_id: 10, nome: "Neon Pulse" },
    album: { album_id: 101, titulo: "Nocturnal Frequencies", ano: 2025 },
    qualidades_disponiveis: ["128kbps", "320kbps", "FLAC"],
    tags: ["noturna", "estrada", "guitarra"],
    letra: "Driving past the neon signs until the morning fades..."
  },
  {
    musica_id: 872,
    titulo: "Static Waves",
    genero: "Indie Rock",
    duracao_segundos: 198,
    artista: { artista_id: 10, nome: "Neon Pulse" },
    album: { album_id: 101, titulo: "Nocturnal Frequencies", ano: 2025 },
    qualidades_disponiveis: ["128kbps", "320kbps"],
    tags: ["energética", "treino"]
  },
  {
    musica_id: 122,
    titulo: "City Lights",
    genero: "Synthpop",
    duracao_segundos: 245,
    artista: { artista_id: 11, nome: "Velvet Echo" },
    album: { album_id: 102, titulo: "Mirrors & Silhouettes", ano: 2026 },
    qualidades_disponiveis: ["128kbps", "320kbps", "FLAC"],
    feats: [{ artista_id: 10, nome: "Neon Pulse" }],
    tags: ["sintetizador", "anos-80"]
  },
  {
    musica_id: 553,
    titulo: "Paper Planes",
    genero: "Indie Rock",
    duracao_segundos: 201,
    artista: { artista_id: 11, nome: "Velvet Echo" },
    album: { album_id: 102, titulo: "Mirrors & Silhouettes", ano: 2026 },
    qualidades_disponiveis: ["128kbps", "320kbps"],
    tags: ["acústica", "melancólica"]
  },
  {
    musica_id: 610,
    titulo: "Solar Flare",
    genero: "Indie Rock",
    duracao_segundos: 230,
    artista: { artista_id: 11, nome: "Velvet Echo" },
    album: { album_id: 102, titulo: "Mirrors & Silhouettes", ano: 2026 },
    qualidades_disponiveis: ["128kbps", "320kbps", "FLAC", "Dolby Atmos"],
    feats: [{ artista_id: 12, nome: "Solar Drift" }],
    tags: ["destaque", "verão", "indie"],
    letra: "Catching every spark before the horizon burns..."
  },
  {
    musica_id: 611,
    titulo: "Electric Rain",
    genero: "Synthpop",
    duracao_segundos: 224,
    artista: { artista_id: 10, nome: "Neon Pulse" },
    album: { album_id: 101, titulo: "Nocturnal Frequencies", ano: 2025 },
    qualidades_disponiveis: ["128kbps", "320kbps"],
    tags: ["eletrônica", "chuva"]
  },
  {
    musica_id: 612,
    titulo: "Quiet Horizon",
    genero: "Lo-Fi",
    duracao_segundos: 185,
    artista: { artista_id: 12, nome: "Solar Drift" },
    album: { album_id: 103, titulo: "Tokyo Rain 3AM", ano: 2026 },
    qualidades_disponiveis: ["128kbps", "320kbps", "FLAC"],
    instrumental: true,
    bpm: 78,
    tags: ["estudo", "foco", "relaxar"]
  },
  {
    musica_id: 613,
    titulo: "Night Bus",
    genero: "Lo-Fi",
    duracao_segundos: 192,
    artista: { artista_id: 12, nome: "Solar Drift" },
    album: { album_id: 103, titulo: "Tokyo Rain 3AM", ano: 2026 },
    qualidades_disponiveis: ["128kbps", "320kbps"],
    instrumental: true,
    bpm: 82,
    tags: ["madrugada", "chill"]
  }
]);

// 3. Coleção de Playlists Dinâmicas (Embedding com Snapshot de Faixas)
db.playlists.insertMany([
  {
    playlist_id: 5001,
    usuario_id: 9921,
    nome: "Descobertas Indie da Ana",
    publica: true,
    atualizada_em: new Date("2026-09-19T18:05:00Z"),
    faixas: [
      { musica_id: 401, titulo: "Midnight Drive", artista: "Neon Pulse", duracao_segundos: 213 },
      { musica_id: 122, titulo: "City Lights", artista: "Velvet Echo", duracao_segundos: 245 }
    ]
  }
]);