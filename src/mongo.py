from pymongo import MongoClient
import dotenv
import configs
import argparse
import os


mongo_client = MongoClient(
    configs._env_vals.get("ME_CONFIG_MONGODB_URL") + "main?authSource=admin"
)

db = mongo_client["main"]
user_col = db["users"]
user_col.create_index("email", unique=True, background=True)
