from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import user_router, list_router, auth_router, post_router

app = FastAPI()
allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, tags=["user"])
app.include_router(list_router, tags=["list"], deprecated=True)
app.include_router(auth_router, tags=["auth"])
app.include_router(post_router, tags=["post"])
