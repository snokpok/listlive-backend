import bson
from pprint import pprint
import pymongo
from mongo import mongo_client, user_col, todo_col
from bson.objectid import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
import bcrypt
from fastapi import FastAPI, Body, Request, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from auth_repo import AuthRepository
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
auth_repo = AuthRepository()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
user_col = mongo_client["main"]["users"]


async def verify_token_dependency(authorization: str = Header(...)):
    auth_repo.verify_decode_auth_header({"Authorization": authorization})
    return


class CreateUserBody(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str


@app.get("/user")
async def get_user(email: str):
    user = user_col.find_one({"email": email}, {"password": 0, "todos": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User with email not found")
    user["_id"] = str(user.get("_id"))
    return user


@app.post("/user")
async def create_user(body: CreateUserBody):
    try:
        user = {
            "first_name": body.first_name,
            "last_name": body.last_name,
            "email": body.email,
            "password": bcrypt.hashpw(
                body.password.encode(encoding="UTF-8"), bcrypt.gensalt()
            ),
            "todos": [],
        }
        insert_res = user_col.insert_one(user)
        id, ack = insert_res.inserted_id, insert_res.acknowledged
        response = {
            "id": str(id),
            "token": auth_repo.create_access_token(str(id)),
            "ack": ack,
        }
        return dict(response)
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=400, detail="Associated account with given email already exists"
        )


class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/login")
async def login_get_access_token(body: LoginBody):
    found_user = user_col.find_one({"email": body.email})
    if not found_user:
        raise HTTPException(status_code=404, detail="Incorrect email")
    if not bcrypt.checkpw(body.password.encode("UTF-8"), found_user.get("password")):
        raise HTTPException(status_code=400, detail="Incorrect password")
    return {
        "token": auth_repo.create_access_token(str(found_user.get("_id"))),
        "id": str(found_user.get("_id")),
    }


class CreateTodoItemBody(BaseModel):
    title: str
    description: Optional[str] = ""


@app.post("/todo", dependencies=[Depends(verify_token_dependency)])
async def create_todo_item(body: CreateTodoItemBody = Body(...)):
    # find the user
    user_id = auth_repo.get_current_user_id()
    new_todo_id = str(ObjectId())
    new_todo_item = {
        "id": new_todo_id,
        "title": body.title,
        "description": body.description,
    }

    insert_res = user_col.update_one(
        filter={"_id": ObjectId(user_id)},
        update={"$push": {"todos": new_todo_item}},
    )

    response = {
        "id": new_todo_id,
        "ack": insert_res.acknowledged,
        "raw": insert_res.raw_result,
        "item": body,
    }
    return response


@app.delete("/todo", dependencies=[Depends(verify_token_dependency)])
async def delete_todo_item(id: str):
    delete_todo_res = user_col.update_one(
        {"_id": ObjectId(auth_repo.get_current_user_id())},
        update={"$pull": {"todos": {"id": id}}},
    )
    response = {
        "ack": delete_todo_res.acknowledged,
        "id": delete_todo_res.upserted_id,
        "raw": delete_todo_res.raw_result,
    }
    return response


@app.get("/todos", dependencies=[Depends(verify_token_dependency)])
async def get_user_todo_list():
    user_todos = mongo_client["main"]["users"].find_one(
        {"_id": ObjectId(auth_repo.get_current_user_id())}
    )
    return user_todos.get("todos")


class UpdateItemBody(BaseModel):
    title: str
    description: Optional[str] = ""


@app.put("/todo", dependencies=[Depends(verify_token_dependency)])
async def edit_todo(id: str, body: UpdateItemBody = Body(...)):
    if len(body.title) == 0:
        raise HTTPException(status_code=400, detail="Todo must have a non-empty title")
    update_todo_res = user_col.update_one(
        {"_id": ObjectId(auth_repo.get_current_user_id()), "todos.id": id},
        update={
            "$set": {
                "todos.$.title": body.title,
                "todos.$.description": body.description,
            }
        },
    )
    response = {
        "ack": update_todo_res.acknowledged,
        "id": update_todo_res.upserted_id,
        "raw": update_todo_res.raw_result,
        "item": body,
    }
    return response


@app.get("/decode-token")
async def decode_token(token: str):
    return auth_repo.decode_access_token(token)


class ChangeOrderItemBody(BaseModel):
    item_id: str
    new_order: int


@app.put("/todo/change-order", dependencies=[Depends(verify_token_dependency)])
async def change_order_todo(body: ChangeOrderItemBody):
    todos = user_col.find_one({"_id": ObjectId(auth_repo.get_current_user_id())}).get(
        "todos"
    )
    [todo] = [t for t in todos if t.get("id") == body.item_id]
    pull_res = user_col.update_one(
        {"_id": ObjectId(auth_repo.get_current_user_id())},
        update={
            "$pull": {"todos": {"id": todo.get("id")}},
        },
    )
    change_order_res = user_col.update_one(
        {"_id": ObjectId(auth_repo.get_current_user_id())},
        update={
            "$push": {"todos": {"$each": [todo], "$position": body.new_order}},
        },
    )
    return {
        "ack": change_order_res.acknowledged,
        "raw": {"co": change_order_res.raw_result, "p": pull_res.raw_result},
        "edit": todo,
    }


@app.get("/me", dependencies=[Depends(verify_token_dependency)])
async def get_me():
    me_res = user_col.find_one(
        {"_id": ObjectId(auth_repo.get_current_user_id())}, {"password": 0, "todos": 0}
    )
    me_res["_id"] = str(me_res.get("_id"))
    return me_res
