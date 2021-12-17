import enum
from typing import Any, Dict
import bson
from bson.objectid import ObjectId
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from pydantic.main import BaseModel
from pymongo.message import update
from mongo import post_col, user_col
from fastapi.routing import APIRouter
from dependencies import verify_token_dependency

pr = APIRouter(
    prefix="/posts"
)


@pr.get("/recs")
async def get_recommended_posts(claims: Dict[str, Any] = Depends(verify_token_dependency)):
    '''
    Get all recommended posts to the user
    '''
    return


class CreatePostBody(BaseModel):
    text_content: str


@pr.post("/")
async def create_post(body: CreatePostBody, claims: Dict[str, Any] = Depends(verify_token_dependency)):
    '''
    Create post by current user
    '''
    try:
        post = {
            "text_content": body.text_content,
            "writer_id": claims.get("id")
        }
        res = post_col.insert_one(post)
        update_user_posts_res = user_col.update_one(
            filter={"_id": ObjectId(claims.get("id"))},
            update={"$push": {"posts": str(res.inserted_id)}}
        )
        return {
            "_id": str(res.inserted_id),
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail={
                "message": "Oops something went wrong with creating the post",
                "details": str(e)
            })


@pr.get("/me")
async def get_user_posts(claims: Dict[str, Any] = Depends(verify_token_dependency)):
    '''
    Get my posts
    '''
    res = user_col.find_one({"_id": ObjectId(claims.get("id"))}, {
        "posts": 1, "_id": 0})
    for idx, pid in enumerate(res.get("posts")):
        post = post_col.find_one(filter={"_id": ObjectId(pid)})
        post['_id'] = str(post.get('_id'))
        res['posts'][idx] = post
    return res["posts"]


@pr.get("/{user_id}")
async def get_user_posts(user_id: str, claims: Dict[str, Any] = Depends(verify_token_dependency)):
    '''
    Get posts by user ID
    '''
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    res = user_col.find_one({"_id": ObjectId(user_id)}, {
                            "posts": 1, "_id": 0})
    if not res:
        raise HTTPException(status_code=404, detail="User not found under ID")
    for idx, pid in enumerate(res.get("posts")):
        post = post_col.find_one(filter={"_id": ObjectId(pid)})
        post['_id'] = str(post.get('_id'))
        res['posts'][idx] = post
    return res["posts"]
