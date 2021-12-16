from fastapi.param_functions import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from auth_repo import ar

security_dependency = HTTPBearer()


async def verify_token_dependency(
    creds: HTTPAuthorizationCredentials = Security(security_dependency),
):
    ar.verify_decode_auth_header(
        {"Authorization": f"{creds.scheme} {creds.credentials}"}
    )
    return
