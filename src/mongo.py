from pymongo import MongoClient

mongo_client = MongoClient("mongodb://vincent:fkusam2212@mongo:27017/?authSource=admin")

db = mongo_client["main"]
user_col = db["users"]
user_col.create_index("email", unique=True, background=True)
todo_col = db["todos"]
