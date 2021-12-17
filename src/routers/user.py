from typing import Any, Dict
from bson.json_util import dumps
from fastapi.routing import APIRouter
from pydantic.main import BaseModel
from mongo import user_col, list_col
from auth_repo import ar
from dependencies import verify_token_dependency
from bson.objectid import ObjectId
from fastapi import Depends
from fastapi.routing import APIRouter
import json

user_router = APIRouter(
    prefix="/users"
)

common_find_options_user = {"password": 0, "lists": 0}


@user_router.get("/")
async def get_all_users(claims: Dict[str, Any] = Depends(verify_token_dependency)):
    search_res = user_col.find(
        {"_id": {"$ne": ObjectId(claims.get("id"))}}, {"password": 0}
    )
    result_list = []
    for user in search_res:
        user["_id"] = str(user["_id"])
        result_list.append(user)
    return result_list


@user_router.get("/me")
async def get_me(claims: Dict[str, Any] = Depends(verify_token_dependency)):
    me_res = user_col.find_one(
        {"_id": ObjectId(claims.get("id"))}, common_find_options_user
    )
    me_res["_id"] = str(me_res.get("_id"))
    return me_res


class EditMeBody(BaseModel):
    profile_emoji: str


@user_router.put("/me")
async def edit_my_attribs(body: EditMeBody, claims: Dict[str, Any] = Depends(verify_token_dependency)):
    edit_res = user_col.update_one(
        {"_id": ObjectId(claims.get("id"))},
        {"$set": {"profile_emoji": body.profile_emoji}},
    )
    return {
        "raw": json.loads(dumps(edit_res.raw_result)),
        "metas": {
            "matched": edit_res.matched_count,
            "modified": edit_res.modified_count,
        },
    }


@user_router.get("/{user_id}/lists", dependencies=[Depends(verify_token_dependency)], deprecated=True)
async def get_lists_by_user(user_id: str):
    res = user_col.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    for idx, list_id in enumerate(res.get("lists")):
        list_res = list_col.find_one(filter={"_id": ObjectId(list_id)})
        list_res["_id"] = str(list_res.get("_id"))
        res["lists"][idx] = list_res
    res["_id"] = str(res.get("_id"))
    return res


@user_router.get("/search", dependencies=[Depends(verify_token_dependency)])
async def search_user_by_full_name(q: str):
    search_res = user_col.find(
        {"$text": {"$search": q}}, common_find_options_user)
    result_list = []
    for user in search_res:
        user["_id"] = str(user.get("_id"))
        result_list.append(user)
    return result_list


@user_router.get("/{user_id}", dependencies=[Depends(verify_token_dependency)])
async def get_user_by_id(user_id: str):
    res = user_col.find_one({"_id": ObjectId(user_id)},
                            common_find_options_user)
    res["_id"] = str(res.get("_id"))
    return res
