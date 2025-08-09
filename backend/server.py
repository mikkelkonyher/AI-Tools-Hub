from fastapi import FastAPI, APIRouter, Query, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Enums for AI Tools
class Category(str, Enum):
    MUSIC_GENERATION = "music_generation"
    IMAGE_CREATION = "image_creation"
    VIDEO_EDITING = "video_editing"
    TEXT_GENERATION = "text_generation"
    AUTOMATION = "automation"
    DATA_ANALYSIS = "data_analysis"
    GAMING = "gaming"
    CODE_GENERATION = "code_generation"

class PriceModel(str, Enum):
    FREE = "free"
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    FREEMIUM = "freemium"

class Platform(str, Enum):
    WEB = "web"
    API = "api"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    BROWSER_EXTENSION = "browser_extension"


# Models
class AITool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: Category
    price_model: PriceModel
    platform: Platform
    price_details: str
    website_url: str
    image_url: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AIToolCreate(BaseModel):
    name: str
    description: str
    category: Category
    price_model: PriceModel
    platform: Platform
    price_details: str
    website_url: str
    image_url: Optional[str] = None

class ToolsResponse(BaseModel):
    tools: List[AITool]
    total: int
    page: int
    per_page: int

# Legacy status check models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# Routes
@api_router.get("/")
async def root():
    return {"message": "AI Tools Aggregator API"}

@api_router.get("/tools", response_model=ToolsResponse)
async def get_tools(
    category: Optional[Category] = None,
    price_model: Optional[PriceModel] = None,
    platform: Optional[Platform] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """Get AI tools with optional filtering and search"""
    
    # Build filter query
    filter_query = {}
    
    if category:
        filter_query["category"] = category
    if price_model:
        filter_query["price_model"] = price_model
    if platform:
        filter_query["platform"] = platform
    
    # Add search functionality
    if search:
        filter_query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get total count
    total = await db.ai_tools.count_documents(filter_query)
    
    # Get tools with pagination
    tools_cursor = db.ai_tools.find(filter_query).skip(skip).limit(per_page).sort("created_at", -1)
    tools = await tools_cursor.to_list(per_page)
    
    # Convert to models
    ai_tools = [AITool(**tool) for tool in tools]
    
    return ToolsResponse(
        tools=ai_tools,
        total=total,
        page=page,
        per_page=per_page
    )

@api_router.get("/tools/{tool_id}", response_model=AITool)
async def get_tool(tool_id: str):
    """Get a specific AI tool by ID"""
    tool = await db.ai_tools.find_one({"id": tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return AITool(**tool)

@api_router.post("/tools", response_model=AITool)
async def create_tool(tool_data: AIToolCreate):
    """Create a new AI tool"""
    tool = AITool(**tool_data.dict())
    await db.ai_tools.insert_one(tool.dict())
    return tool

@api_router.get("/categories")
async def get_categories():
    """Get all available categories"""
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} for cat in Category]

@api_router.get("/price-models")
async def get_price_models():
    """Get all available price models"""
    return [{"value": pm.value, "label": pm.value.replace("_", " ").title()} for pm in PriceModel]

@api_router.get("/platforms")
async def get_platforms():
    """Get all available platforms"""
    return [{"value": p.value, "label": p.value.replace("_", " ").title()} for p in Platform]

@api_router.post("/seed-data")
async def seed_sample_data():
    """Seed database with sample AI tools data"""
    
    # Check if data already exists
    existing_count = await db.ai_tools.count_documents({})
    if existing_count > 0:
        return {"message": f"Database already has {existing_count} tools"}
    
    sample_tools = [
        {
            "name": "ChatGPT",
            "description": "Advanced conversational AI for text generation, coding assistance, and creative writing",
            "category": "text_generation",
            "price_model": "freemium",
            "platform": "web",
            "price_details": "Free tier available, Plus at $20/month",
            "website_url": "https://chat.openai.com",
            "rating": 4.8,
            "review_count": 15420
        },
        {
            "name": "Midjourney",
            "description": "AI-powered image generation tool creating stunning artwork from text prompts",
            "category": "image_creation",
            "price_model": "subscription",
            "platform": "web",
            "price_details": "Starting at $10/month",
            "website_url": "https://midjourney.com",
            "rating": 4.7,
            "review_count": 8930
        },
        {
            "name": "GitHub Copilot",
            "description": "AI pair programmer that helps you write code faster with intelligent suggestions",
            "category": "code_generation",
            "price_model": "subscription",
            "platform": "desktop",
            "price_details": "$10/month for individuals",
            "website_url": "https://github.com/features/copilot",
            "rating": 4.6,
            "review_count": 12500
        },
        {
            "name": "Runway ML",
            "description": "Creative suite of AI tools for video editing, generation, and visual effects",
            "category": "video_editing",
            "price_model": "freemium",
            "platform": "web",
            "price_details": "Free tier, Pro at $15/month",
            "website_url": "https://runwayml.com",
            "rating": 4.5,
            "review_count": 5670
        },
        {
            "name": "Mubert",
            "description": "AI music generator creating royalty-free tracks for content creators",
            "category": "music_generation",
            "price_model": "freemium",
            "platform": "web",
            "price_details": "Free tier, Pro at $11.69/month",
            "website_url": "https://mubert.com",
            "rating": 4.3,
            "review_count": 3420
        },
        {
            "name": "Zapier",
            "description": "Automation platform connecting apps and services with AI-powered workflows",
            "category": "automation",
            "price_model": "freemium",
            "platform": "web",
            "price_details": "Free tier, Starter at $19.99/month",
            "website_url": "https://zapier.com",
            "rating": 4.4,
            "review_count": 18900
        },
        {
            "name": "DataRobot",
            "description": "Enterprise AI platform for automated machine learning and predictive analytics",
            "category": "data_analysis",
            "price_model": "subscription",
            "platform": "web",
            "price_details": "Enterprise pricing on request",
            "website_url": "https://datarobot.com",
            "rating": 4.2,
            "review_count": 980
        },
        {
            "name": "Leonardo AI",
            "description": "Advanced AI image generator with fine-tuned models for game assets and art",
            "category": "gaming",
            "price_model": "freemium",
            "platform": "web",
            "price_details": "Free tier, Artisan at $10/month",
            "website_url": "https://leonardo.ai",
            "rating": 4.6,
            "review_count": 7250
        },
        {
            "name": "DALL-E 3",
            "description": "OpenAI's latest image generation model with improved prompt adherence",
            "category": "image_creation",
            "price_model": "subscription",
            "platform": "web",
            "price_details": "Available with ChatGPT Plus",
            "website_url": "https://openai.com/dall-e-3",
            "rating": 4.7,
            "review_count": 11200
        },
        {
            "name": "Jasper AI",
            "description": "AI writing assistant for marketing copy, blog posts, and business content",
            "category": "text_generation",
            "price_model": "subscription",
            "platform": "web",
            "price_details": "Creator at $39/month",
            "website_url": "https://jasper.ai",
            "rating": 4.4,
            "review_count": 9870
        }
    ]
    
    # Insert sample tools
    tools_to_insert = []
    for tool_data in sample_tools:
        tool = AITool(**tool_data)
        tools_to_insert.append(tool.dict())
    
    result = await db.ai_tools.insert_many(tools_to_insert)
    
    return {"message": f"Successfully seeded {len(result.inserted_ids)} AI tools"}

# Legacy endpoints
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()