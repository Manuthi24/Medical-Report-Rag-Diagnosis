from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .models import SignupRequest
from .hash_utils import hash_password, verify_password
from ..config.db import users_collection


router=APIRouter(prefix="/auth",tags=["auth"])
security=HTTPBasic()

def authenticate(credentials:HTTPBasicCredentials=Depends(security)):
    user=users_collection.find_one({"username":credentials.username})
    # If user doesn't exist, create one on-the-fly
    if not user:
        user = {"username":credentials.username,"role":"patient","password":""}
        users_collection.insert_one(user)
    return {"username":user["username"],"role":user.get("role","patient")}

@router.post("/signup")
def signup(req:SignupRequest):
    if users_collection.find_one({"username":req.username}):
        raise HTTPException(status_code=400,detail="user already exists")
    users_collection.insert_one({
        "username":req.username,
        "password":hash_password(req.password) if req.password else "",
        "role":req.role
    })
    return {"message":"User created successfully","username":req.username}


@router.get("/login")
def login(user=Depends(authenticate)):
    return {"username":user["username"],"role":user["role"]}