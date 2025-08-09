from fastapi import FastAPI, APIRouter, Query, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from enum import Enum
from passlib.context import CryptContext
from jose import JWTError, jwt
import bcrypt


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

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


# Authentication Models
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# AI Tool Models
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


# Review Models
class ReviewCreate(BaseModel):
    tool_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str
    content: str

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_id: str
    user_id: str
    username: str
    rating: int
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CommentCreate(BaseModel):
    review_id: str
    content: str
    parent_id: Optional[str] = None

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str
    user_id: str
    username: str
    content: str
    parent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Response Models
class ToolsResponse(BaseModel):
    tools: List[AITool]
    total: int
    page: int
    per_page: int

class ReviewsResponse(BaseModel):
    reviews: List[Review]
    total: int
    page: int
    per_page: int

class CommentsResponse(BaseModel):
    comments: List[Comment]
    total: int


# Authentication Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_user(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return User(**user)

async def authenticate_user(username: str, password: str):
    user_data = await db.users.find_one({"username": username})
    if not user_data:
        return False
    if not verify_password(password, user_data["hashed_password"]):
        return False
    return User(**user_data)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Legacy status models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# Routes
@api_router.get("/")
async def root():
    return {"message": "AI Tools Aggregator API with Authentication"}

# Authentication Routes
@api_router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    user_data = User(username=user.username, email=user.email)
    user_dict = user_data.dict()
    user_dict["hashed_password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    return user_data

@api_router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    user = await authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/me", response_model=User)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

# AI Tools Routes
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

# Review Routes
@api_router.post("/reviews", response_model=Review)
async def create_review(review: ReviewCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new review for a tool"""
    
    # Check if tool exists
    tool = await db.ai_tools.find_one({"id": review.tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Check if user already reviewed this tool
    existing_review = await db.reviews.find_one({"tool_id": review.tool_id, "user_id": current_user.id})
    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this tool")
    
    # Create review
    review_data = Review(
        **review.dict(),
        user_id=current_user.id,
        username=current_user.username
    )
    
    await db.reviews.insert_one(review_data.dict())
    
    # Update tool rating
    await update_tool_rating(review.tool_id)
    
    return review_data

@api_router.put("/reviews/{review_id}", response_model=Review)
async def update_review(review_id: str, review_update: ReviewCreate, current_user: User = Depends(get_current_active_user)):
    """Update an existing review (only by the review author)"""
    
    # Get existing review
    existing_review = await db.reviews.find_one({"id": review_id})
    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user owns this review
    if existing_review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own reviews")
    
    # Check if tool exists
    tool = await db.ai_tools.find_one({"id": review_update.tool_id})
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # Update review
    updated_review = Review(
        id=review_id,
        **review_update.dict(),
        user_id=current_user.id,
        username=current_user.username,
        created_at=existing_review["created_at"],
        updated_at=datetime.utcnow()
    )
    
    await db.reviews.update_one(
        {"id": review_id},
        {"$set": updated_review.dict()}
    )
    
    # Update tool rating
    await update_tool_rating(review_update.tool_id)
    
    return updated_review

@api_router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a review (only by the review author)"""
    
    # Get existing review
    existing_review = await db.reviews.find_one({"id": review_id})
    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check if user owns this review
    if existing_review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    
    # Delete review
    await db.reviews.delete_one({"id": review_id})
    
    # Delete associated comments
    await db.comments.delete_many({"review_id": review_id})
    
    # Update tool rating
    await update_tool_rating(existing_review["tool_id"])
    
    return {"message": "Review deleted successfully"}

@api_router.get("/reviews/{tool_id}", response_model=ReviewsResponse)
async def get_tool_reviews(
    tool_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50)
):
    """Get reviews for a specific tool"""
    
    # Calculate skip for pagination
    skip = (page - 1) * per_page
    
    # Get total count
    total = await db.reviews.count_documents({"tool_id": tool_id})
    
    # Get reviews with pagination
    reviews_cursor = db.reviews.find({"tool_id": tool_id}).skip(skip).limit(per_page).sort("created_at", -1)
    reviews = await reviews_cursor.to_list(per_page)
    
    # Convert to models
    review_objects = [Review(**review) for review in reviews]
    
    return ReviewsResponse(
        reviews=review_objects,
        total=total,
        page=page,
        per_page=per_page
    )

@api_router.post("/comments", response_model=Comment)
async def create_comment(comment: CommentCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new comment on a review"""
    
    # Check if review exists
    review = await db.reviews.find_one({"id": comment.review_id})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Create comment
    comment_data = Comment(
        **comment.dict(),
        user_id=current_user.id,
        username=current_user.username
    )
    
    await db.comments.insert_one(comment_data.dict())
    return comment_data

@api_router.get("/comments/{review_id}", response_model=CommentsResponse)
async def get_review_comments(review_id: str):
    """Get comments for a specific review"""
    
    # Get comments
    comments_cursor = db.comments.find({"review_id": review_id}).sort("created_at", 1)
    comments = await comments_cursor.to_list(1000)
    
    # Get total count
    total = len(comments)
    
    # Convert to models
    comment_objects = [Comment(**comment) for comment in comments]
    
    return CommentsResponse(
        comments=comment_objects,
        total=total
    )

async def update_tool_rating(tool_id: str):
    """Update the average rating for a tool"""
    
    # Get all reviews for the tool
    reviews_cursor = db.reviews.find({"tool_id": tool_id})
    reviews = await reviews_cursor.to_list(1000)
    
    if reviews:
        # Calculate average rating
        total_rating = sum(review["rating"] for review in reviews)
        average_rating = total_rating / len(reviews)
        
        # Update tool
        await db.ai_tools.update_one(
            {"id": tool_id},
            {
                "$set": {
                    "rating": round(average_rating, 1),
                    "review_count": len(reviews),
                    "updated_at": datetime.utcnow()
                }
            }
        )

# Filter Options Routes
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

# Seed Data Route
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