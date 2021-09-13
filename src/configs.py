import dotenv
import os
from pprint import pprint

_env_vals = os.environ

pprint(_env_vals)

jwt_secret_key = str(_env_vals.get("JWT_SECRET_KEY"))
