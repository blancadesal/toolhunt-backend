from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from starlette.middleware.sessions import SessionMiddleware
import secrets
from jose import JWTError, jwt
from datetime import datetime, timedelta
from urllib.parse import urlencode
from pydantic import BaseModel
import logging
import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="your-session-secret-key")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
TOOLHUB_AUTH_URL = "https://toolhub-demo.wmcloud.org/o/authorize/"
TOOLHUB_TOKEN_URL = "https://toolhub-demo.wmcloud.org/o/token/"
CLIENT_ID = "7hNuRLxSPJ9Q8S3LZnpDv9WinufE04s5vK2RkexX"
CLIENT_SECRET = "vc5WIJYyWnPHUCK4sSQmrtVaiZWTIgSQPsnTPR5FrSIg7GsAIVfxgnazjuUsg4fSRTYe1FKNRMPIdPWt53trkRytJQVSlqVbtxpn4vQG3RxNxekw7N9lj8zwCaTQmEYO"
REDIRECT_URI = "http://localhost:3000/profile"  # Update this to your frontend callback URL
SECRET_KEY = "your-secret-key"  # Change this to a secure random string
ALGORITHM = "HS256"

# In-memory user storage
users = {}

class User(BaseModel):
    id: str
    username: str
    email: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for states (in production, use a proper database)
state_storage = {}

@app.get("/api/auth/login")
async def login():
    state = secrets.token_urlsafe(32)
    state_id = secrets.token_urlsafe(16)
    state_storage[state_id] = state
    logger.info(f"Storing state {state} with ID {state_id}")
    
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": f"{state_id}:{state}",
        "response_type": "code",
    }
    auth_url = f"{TOOLHUB_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Generated login URL: {auth_url}")
    
    return JSONResponse(content={"login_url": auth_url})

@app.post("/api/auth/callback")
async def oauth_callback(request: Request):
    body = await request.json()
    code = body.get("code")
    received_state = body.get("state")
    
    logger.info(f"Received callback with code: {code} and state: {received_state}")
    
    if not received_state or ':' not in received_state:
        raise HTTPException(status_code=400, detail="Invalid state format")
    
    state_id, state = received_state.split(':', 1)
    stored_state = state_storage.get(state_id)
    logger.info(f"Stored state for ID {state_id}: {stored_state}")
    
    if not stored_state or state != stored_state:
        logger.error(f"Invalid state. Received: {state}, Stored: {stored_state}")
        raise HTTPException(status_code=400, detail="Invalid state")
    
    # Remove the used state
    del state_storage[state_id]
    
    token_response = await exchange_code_for_token(code)
    logger.info("Successfully exchanged code for token")
    
    user_data = await fetch_user_data(token_response["access_token"])
    logger.info(f"Fetched user data: {user_data}")
    
    db_user = create_or_update_user(user_data)
    access_token = create_access_token(data={"sub": db_user.id})
    
    logger.info(f"Created access token for user: {db_user.id}")
    return JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user.dict()
    })

async def exchange_code_for_token(code):
    async with httpx.AsyncClient() as client:
        response = await client.post(TOOLHUB_TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
    return response.json()

async def fetch_user_data(access_token):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://toolhub-demo.wmcloud.org/api/user/", headers={
            "Authorization": f"Bearer {access_token}"
        })
    return response.json()

def create_or_update_user(user_data):
    user_id = str(user_data["id"])
    user = User(
        id=user_id,
        username=user_data["username"],
        email=user_data["email"]
    )
    users[user_id] = user
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = users.get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/api/user")
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/debug/session")
async def debug_session(request: Request):
    return JSONResponse(content={
        "session": dict(request.session),
        "cookies": request.cookies
    })
