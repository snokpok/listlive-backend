import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv(".development.env"))

jwt_secret_key = str(os.environ.get("JWT_SECRET_KEY"))
root_user_db_pwd = str(os.environ.get("MYSQL_ROOT_PASSWORD"))
