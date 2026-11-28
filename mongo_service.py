import os
from datetime import datetime, timezone
from pymongo import MongoClient


class MongoService:
    def __init__(self):
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB", "vibestream")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def buscar_musica_por_id(self, musica_id: int) -> dict | None:
        """Recupera metadados completos da faixa (usado após recomendação do Neo4j)."""
        return self.db.musicas.find_one({"musica_id": musica_id}, {"_id": 0})

    def buscar_por_genero_ou_artista(self, termo: str) -> list[dict]:
        """Busca no catálogo por gênero, título ou nome do artista (case-insensitive)."""
        filtro = {
            "$or": [
                {"genero": {"$regex": termo, "$options": "i"}},
                {"artista.nome": {"$regex": termo, "$options": "i"}},
                {"titulo": {"$regex": termo, "$options": "i"}},
            ]
        }
        return list(self.db.musicas.find(filtro, {"_id": 0}))

    def obter_album_completo(self, artista_id: int, album_id: int) -> dict | None:
        """Exibe artista e álbum com todas as faixas embutidas em 1 leitura (zero joins)."""
        return self.db.artistas.find_one(
            {"artista_id": artista_id, "albuns.album_id": album_id},
            {"_id": 0, "nome": 1, "pais": 1, "albuns.$": 1},
        )

    def listar_playlists_usuario(self, usuario_id: int) -> list[dict]:
        """Retorna todas as playlists de um usuário."""
        return list(self.db.playlists.find({"usuario_id": usuario_id}, {"_id": 0}))

    def adicionar_musica_playlist(self, playlist_id: int, musica_id: int) -> bool:
        """Adiciona snapshot da música à playlist via $push atômico."""
        musica = self.buscar_musica_por_id(musica_id)
        if not musica:
            return False
        item = {
            "musica_id": musica["musica_id"],
            "titulo": musica["titulo"],
            "artista": musica["artista"]["nome"],
            "duracao_segundos": musica["duracao_segundos"],
        }
        res = self.db.playlists.update_one(
            {"playlist_id": playlist_id},
            {
                "$push": {"faixas": item},
                "$set": {"atualizada_em": datetime.now(timezone.utc)},
            },
        )
        return res.modified_count > 0

    def remover_musica_playlist(self, playlist_id: int, musica_id: int) -> bool:
        """Remove uma música da playlist via $pull atômico."""
        res = self.db.playlists.update_one(
            {"playlist_id": playlist_id},
            {
                "$pull": {"faixas": {"musica_id": musica_id}},
                "$set": {"atualizada_em": datetime.now(timezone.utc)},
            },
        )
        return res.modified_count > 0

    def estatisticas_por_genero(self) -> list[dict]:
        """Aggregation Pipeline: total de faixas e duração média por gênero."""
        pipeline = [
            {
                "$group": {
                    "_id": "$genero",
                    "total_musicas": {"$sum": 1},
                    "duracao_media_seg": {"$avg": "$duracao_segundos"},
                }
            },
            {"$sort": {"total_musicas": -1}},
        ]
        return list(self.db.musicas.aggregate(pipeline))