from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from openai import OpenAI
from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import certifi
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set API keys and configuration
api_key = os.getenv("OPENAI_API_KEY")
# Log the first few characters of the API key for debugging (safely)
if api_key:
    logger.info("API Key found (starts with): %s...", api_key[:6])
    logger.info("API Key length: %d", len(api_key))
else:
    logger.error("API key is not set")
    raise RuntimeError("OPENAI_API_KEY is not set")

# MongoDB setup
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER", "word-definitions.e6nmtti.mongodb.net")

if not all([mongo_username, mongo_password]):
    logger.error("MongoDB credentials are not set")
    raise RuntimeError("MongoDB credentials are not set. Please check your .env file")

# Construct MongoDB URI
MONGO_URI = f"mongodb+srv://{quote_plus(mongo_username)}:{quote_plus(mongo_password)}@{mongo_cluster}/?retryWrites=true&w=majority"

try:
    # Initialize MongoDB client with SSL certificate verification
    mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = mongo_client.word_definitions
    definitions_collection = db.definitions
    
    # Create indexes for better performance
    definitions_collection.create_index([("word", ASCENDING)], unique=True)
    definitions_collection.create_index([("created_at", ASCENDING)])
    
    # Test connection
    mongo_client.admin.command('ping')
    logger.info("Successfully connected to MongoDB!")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise RuntimeError(f"MongoDB connection failed: {str(e)}")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read(), media_type="text/html")

@app.get("/health")
async def health_check():
    try:
        # Check MongoDB connection
        mongo_client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/get_definition")
async def get_definition(word: str = Form(...)):
    try:
        word = word.lower().strip()
        logger.info(f"Received request for word: {word}")
        
        # Check if definition exists in database
        existing_definition = definitions_collection.find_one({"word": word})
        
        if existing_definition:
            logger.info(f"Found cached definition for {word}")
            return {"definition": existing_definition["definition"]}
        
        # If not in database, get from OpenAI
        logger.info(f"Fetching definition from OpenAI for {word}")
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": f"Please provide a clear and concise definition of the word '{word}'. Include part of speech and an example sentence."}
                ]
            )
            
            definition = response.choices[0].message.content
            logger.info(f"Successfully received definition from OpenAI for {word}")
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        
        # Store in database
        try:
            definitions_collection.insert_one({
                "word": word,
                "definition": definition,
                "created_at": datetime.utcnow()
            })
            logger.info(f"Stored new definition for {word}")
        except Exception as e:
            logger.error(f"Failed to store definition in database: {str(e)}")
            # Continue even if storage fails - we can still return the definition
        
        return {"definition": definition}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recent_definitions")
async def get_recent_definitions(limit: int = 10):
    try:
        recent = list(definitions_collection.find(
            {}, 
            {"_id": 0, "word": 1, "definition": 1, "created_at": 1}
        ).sort("created_at", -1).limit(limit))
        
        return {
            "definitions": recent,
            "count": len(recent)
        }
    except Exception as e:
        logger.error(f"Error fetching recent definitions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/definition/{word}")
async def delete_definition(word: str):
    try:
        word = word.lower().strip()
        result = definitions_collection.delete_one({"word": word})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Definition for '{word}' not found")
            
        return {"message": f"Definition for '{word}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting definition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port) 