import os
from fastapi import FastAPI, HTTPException, Header, Response, Depends
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


def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")
    token = authorization.split(" ")[1]
    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


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
async def protected_profile(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at
    }

@app.get("/protected/dashboard")
async def protected_dashboard(current_user = Depends(get_current_user)):
    return {"message": f"Welcome to your dashboard, {current_user.email}"}


@app.post("/auth/logout", status_code=204)
async def logout(current_user = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
        return Response(status_code=204)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to log out")