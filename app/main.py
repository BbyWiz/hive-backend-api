"""Server routes definitions."""

from typing import Any, Dict, List
from app.core.database.database import Database

import json

from pprint import pprint

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.core.fastapi_config import Settings
#from app.core.logs.logs import Logs
from app.core.utility.logger_setup import get_logger
from app.core.utility.timing_middleware import TimingMiddleware

from app.core.utility.utils import read_json_file
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI


class ai_bot:

    # ================= ATTRIBUTES ===============

    api_key = None
    mood = None
    tone = None
    description = None
    textPrompt = None
    imagePrompt=None,

    # ================= CONSTRUCTORS ===============

    def __init__(self, api_key, mood, tone, description):
        self.api_key = api_key
        self.mood = mood
        self.tone = tone
        self.description = description
        self.textPrompt = f"""Create an Instagram post given the following information. Use the description as a general guideline about the topic. The post should have the goal of becoming as viral as possible. Aim to avoid extreme views and or activism.
    Mood: {mood} Tone: {tone} Description: {description}"""
        self.imagePrompt = f"""Create an image for an Instagram post given the following information. Use the description as a general guideline about the topic. The post should have the goal of becoming as viral as possible. Aim to avoid extreme views and or activism.
    Mood: {mood} Tone: {tone} Description: {description}"""

    # ================= METHODS ===============

    # generate post content
    def generate_post_content(self):
        client = self.get_connected_client()
        result = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": self.textPrompt}]
        )
        return result.choices[0].message.content

    # generate post image
    def generate_post_image(self):
        client = self.get_connected_client()
        response = client.images.generate(
            model="dall-e-2",
            prompt="a white siamese cat",
            size="256x256",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    
    # ================= HELPER METHODS ===============
    
    def get_connected_client(self):
        return OpenAI(api_key=self.api_key)








log = get_logger()

load_dotenv()
######################################################################
#|
#|              OpenAI API Key Info
#|
######################################################################

#Retrieving API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
#Ensure API key is loaded right
if not OPENAI_API_KEY:
    raise ValueError("No OpenAI key found;. Make sure your .env file is set up correctly")

#   Headers for authentication with the OpenAI API
headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

######################################################################
#|
#|
#|
######################################################################
def get_app():
    """Get application handle and add any middleware.

    Returns:
        Application object
    """
    settings = Settings()

    # Create FastAPI application
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
    )
    # Add CORS Middleware
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add Timing Middleware to log request times
    _app.add_middleware(TimingMiddleware)

    # Define static file location
    _app.mount("/static", StaticFiles(directory="app/front-end/static"), name="static")

    # Add route rate limiter
    limiter = Limiter(key_func=get_remote_address)
    _app.state.limiter = limiter
    _app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return _app


app = get_app()
database = Database("app/core/database/database.json")
templates = Jinja2Templates(directory="app/front-end/templates")


#################################################################################
#                                index.html
#################################################################################
@app.get("/", response_class=HTMLResponse)
def index_info_html_page(request: Request) -> Any:
    """Front info page."""
    return templates.TemplateResponse("index.html", {"request": request})


#################################################################################
#                                 Default
#################################################################################
@app.get("/health")
def app_health_check() -> Dict[str, str]:
    """Application health check status."""
    return {"status": "healthy"}


#################################################################################
#                                 Image Generator
#################################################################################
# Assuming the rest of your initial setup remains the same

class ImagePrompt(BaseModel):
    prompt: str
    n: int = 1  # Number of images to generate
    size: str = "1024x1024"  # Pixels

image_gen_api_router = APIRouter(tags=["openai_api"])

@image_gen_api_router.post("/generate-image")
async def generate_image(request: ImagePrompt):
    """
    Receives an image generation prompt from the front-end, sends it to OpenAI's API,
    and returns the generated image(s) to the front-end.
    """
    # OpenAI API Settings
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": request.prompt,
        "n": request.n,
        "size": request.size,
        "model": "dall-e-3",
        "quality": "hd"
    }

    # Make the API request
    response = requests.post(url, json=payload, headers=headers)
    
    # Check for errors
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"API request failed: {response.text}")
    
    # Return the response data
    return response.json()
#################################################################################
#                                 Network
#################################################################################

network_api_router = APIRouter(tags=["Testing"])



@network_api_router.get("/TODO")
def get_network_internet_connectivity() -> Dict[str, bool]:
    """TODO."""
    return {"todo": "todo"}


@network_api_router.get("/yoyo")
def get_general_network_state() -> Dict[str, Any]:
    """TODO."""
    return {"todo": "todo"}


@network_api_router.get("/MYTEST")
def get_my_test_info() -> Dict[str, Any]:
    #"""TODO."""
    return {"todo": "todo"}



app.include_router(network_api_router, prefix="/network")


app.include_router(image_gen_api_router, prefix="/openai_api")



#################################################################################
#                                 BUSINESS
#################################################################################
business_api_router = APIRouter(tags=["business"])

@business_api_router.get("/create")
def create_a_business(name: str, description: str, specifics: str) -> dict:
    """Create a business."""
    success = database.create_business(name, description, specifics)
    return {"success": success}

@business_api_router.get("/get_business_info_with_id")
def get_business_info_with_id(id: str) -> dict:
    """Get business info with id."""
    info = database.get_business_info(int(id))
    return {
        "info": info
    }

@business_api_router.get("/get_business_info_with_name")
def get_business_info_with_name(name: str) -> dict:
    """Get business info with name."""
    info = database.get_business_info(name=name)
    return {
        "info": info
    }

@business_api_router.get("/get_all_Business_info")
def get_all_Business_info() -> dict:
    """Get all business info."""
    info = database.get_all_business_info()
    return {
        "ids": info
    }

@business_api_router.get("/get_all_business_ids")
def get_all_business_ids() -> dict:
    """Get all business ids."""
    info = database.get_all_business_ids()
    return {
        "ids": info
    }

@business_api_router.post("/remove_all_businesses")
def remove_all_businesses() -> dict:
    """Get all business ids."""
    success = database.remove_all_businesses()
    return {
        "success": success
    }


@business_api_router.post("/send_business_post_request")
def send_business_post_request() -> bool:
    """Send a post request to OpenAPI."""
    pass


app.include_router(business_api_router, prefix="/business")



#################################################################################
#                                 AI API
#################################################################################
ai_api_router = APIRouter(tags=["ai_api"])

@ai_api_router.post("/send_post_request")
def send_post_request(jsonInput) -> bool:
    """Send a post request to OpenAPI."""
    # input:     
    # api_key = None
    # mood = None
    # tone = None
    # description = None


    with open('core/database/database.json') as f:
        d = json.load(f)
        print(d)

    userInput = json.loads(jsonInput)

    our_ai_bot = ai_bot(api_key=OPENAI_API_KEY,
                        mood=userInput["mood"],
                        tone=userInput["tone"],
                        description=userInput["description"])

    # send post request
    generated_content = our_ai_bot.generate_post_content()
    generated_image = our_ai_bot.generate_post_image()

    print(generated_content)
    print(generated_image)

    # add post info to database
    # respond success

    return True

@ai_api_router.post("/check_post_status")
def check_post_status() -> bool:
    """Check status of OpenAPI request."""
    return True

@ai_api_router.get("/get_post_data")
def get_post_data() -> dict:
    """Get the data returened from OpenAPI if ready."""
    return {}

app.include_router(ai_api_router, prefix="/ai_api")



#################################################################################
#                                 Social Media
#################################################################################
social_api_router = APIRouter(tags=["social"])

@social_api_router.post("/post_to_instagram")
def post_to_instagram() -> bool:
    """Post to Instagram."""
    return True

@social_api_router.post("/post_to_twitter")
def post_to_twitter() -> bool:
    """Post to Twitter/x."""
    return True

app.include_router(social_api_router, prefix="/social")
