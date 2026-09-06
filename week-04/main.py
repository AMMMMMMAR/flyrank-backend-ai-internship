import os
from fastapi import FastAPI, HTTPException, Header
from supabase import create_client, Client
from dotenv import load_dotenv
from pydantic import BaseModel

class AuthRequest(BaseModel):
    email: str
    password: str

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Auth API",
    description="Authentication API using Supabase + FastAPI",
    version="1.0"
)

@app.get("/")
async def root():
    return {"message": "Server running and connected to Supabase"}

@app.post("/auth/signup", status_code=201)
async def signup(auth_request: AuthRequest):
    email = auth_request.email
    password = auth_request.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return {"user": response.user}
    except Exception as e:
        return {"error": str(e)}

@app.post("/auth/login")
async def login(auth_request: AuthRequest):
    email = auth_request.email
    password = auth_request.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {
    "access_token": response.session.access_token,
    "refresh_token": response.session.refresh_token
    }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid login credentials")  # ← raise not return


@app.get("/public/info")
async def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
async def protected_profile(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")
    
    token = authorization.split(" ")[1]
    
    try:
        user = supabase.auth.get_user(token)
        return {
            "id": user.user.id,
            "email": user.user.email,
            "created_at": user.user.created_at
        } 
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")