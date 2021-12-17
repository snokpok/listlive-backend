class UtilsRepository:
    @staticmethod
    def parse_configs_to_dburl(
        username: str, password: str, host: str, port: int, db: str
    ) -> str:
        return f"mongodb://{username}:{password}@{host}:{port}/{db}"

    def parse_configs_to_dburi_cloud(db: str) -> str:
        return f"mongodb+srv://listlive-v2.upc8b.mongodb.net/{db}?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
