from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
import httpx
import secrets
import logging
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

SESSION_SECRET_KEY = secrets.token_urlsafe(32)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOOLHUB_AUTH_URL = "https://toolhub-demo.wmcloud.org/o/authorize/"
TOOLHUB_TOKEN_URL = "https://toolhub-demo.wmcloud.org/o/token/"
CLIENT_ID = "7hNuRLxSPJ9Q8S3LZnpDv9WinufE04s5vK2RkexX"
CLIENT_SECRET = "vc5WIJYyWnPHUCK4sSQmrtVaiZWTIgSQPsnTPR5FrSIg7GsAIVfxgnazjuUsg4fSRTYe1FKNRMPIdPWt53trkRytJQVSlqVbtxpn4vQG3RxNxekw7N9lj8zwCaTQmEYO"
REDIRECT_URI = "http://localhost:8082/oauth/callback"

@app.get("/login")
async def login(request: Request):
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    logger.info(f"Generated and stored OAuth state: {state}")
    
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "state": state,
        "scope": "read write"
    }
    auth_url = f"{TOOLHUB_AUTH_URL}?{urlencode(params)}"
    logger.info(f"Redirecting to auth URL: {auth_url}")
    return RedirectResponse(url=auth_url)

@app.get("/oauth/callback")
async def oauth_callback(request: Request, code: str, state: str):
    logger.info(f"Received OAuth callback with state: {state}")
    stored_state = request.session.get("oauth_state")
    logger.info(f"Retrieved stored state: {stored_state}")
    
    if not stored_state or state != stored_state:
        logger.error(f"State mismatch. Received: {state}, Stored: {stored_state}")
        raise HTTPException(status_code=400, detail="Invalid state")
    
    logger.info("State validated successfully")
    token_response = await exchange_code_for_token(code)
    logger.info(f"Received token response: {token_response}")
    
    request.session["access_token"] = token_response["access_token"]
    request.session["token_type"] = token_response["token_type"]
    request.session["expires_in"] = token_response.get("expires_in")
    request.session["refresh_token"] = token_response.get("refresh_token")
    request.session["scope"] = token_response.get("scope")
    
    logger.info("Token information stored in session")
    return token_response

async def exchange_code_for_token(code):
    logger.info(f"Exchanging code for token. Code: {code}")
    async with httpx.AsyncClient() as client:
        response = await client.post(TOOLHUB_TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
    return response.json()

@app.get("/api/user")
async def get_user(request: Request):
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    async with httpx.AsyncClient() as client:
        response = await client.get("https://toolhub-demo.wmcloud.org/api/user/", headers={
            "Authorization": f"Bearer {token}"
        })
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch user data")
    
    return response.json()

@app.get("/debug/session")
async def debug_session(request: Request):
    return JSONResponse(content={"session": dict(request.session)})
