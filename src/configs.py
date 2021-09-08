import dotenv
import os

_env_vals = (
    dotenv.dotenv_values("../.development.env")
    if os.environ.get("NODE_ENV") in ["development", None]
    else os.environ
)

jwt_secret_key = str(_env_vals.get("JWT_SECRET_KEY"))
