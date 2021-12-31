from abc import abstractproperty
from pymongo import MongoClient
from utils_repo import UtilsRepository
import os

# mongo_configs = {
#     "username": configs._env_vals.get("ME_CONFIG_MONGODB_ADMINUSERNAME"),
#     "password": configs._env_vals.get("ME_CONFIG_MONGODB_ADMINPASSWORD"),
# }

# ## local instance
# mongo_client = MongoClient(
#     UtilsRepository.parse_configs_to_dburl(
#         username=mongo_configs.get("username"),
#         password=mongo_configs.get("password"),
#         host="localhost",
#         port=27017,
#         db="main",
#     )
#     + "?authSource=admin"
# )


mongo_client = MongoClient(
    UtilsRepository.parse_configs_to_dburi_cloud(db="main"),
    tls=True,
    tlsCertificateKeyFile=os.path.join(os.getcwd(), "keys/read-write.pem"),
)

db = mongo_client["main"]
user_col = db["users"]
user_col.create_index("email", unique=True, background=True)
user_col.create_index([("first_name", "text"), ("last_name", "text")])
list_col = db["lists"]
post_col = db["posts"]
