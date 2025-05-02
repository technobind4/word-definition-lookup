from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys
import re

# Print Python version and encoding
print(f"Python version: {sys.version}")
print(f"File system encoding: {sys.getfilesystemencoding()}")

# Load environment variables
print("Current working directory:", os.getcwd())

# Try loading from both files
print("\nTrying .env file:")
load_dotenv('.env')

# Get MongoDB URI from environment variable or use direct string for testing
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://singaworks:9zwRAo8ufwa8fKjR@word-definitions.e6nmtti.mongodb.net/?retryWrites=true&w=majority&appName=word-definitions")
print("\nEnvironment variables loaded")
print("MONGO_URI exists:", bool(MONGO_URI))

if MONGO_URI:
    # Mask sensitive information but show the structure
    masked_uri = re.sub(r'://[^@]+@', '://***:***@', MONGO_URI)
    print("MONGO_URI structure:", masked_uri)

# List all .env* files in current directory
print("\nListing all .env* files:")
os.system('ls -la .env*')

if not MONGO_URI:
    print("\nError: MONGO_URI environment variable is not set")
    print("Available environment variables:", sorted(list(os.environ.keys())))
    exit(1)

try:
    print("\nAttempting to connect to MongoDB...")
    # Create a MongoDB client
    client = MongoClient(MONGO_URI)
    
    # Test the connection
    print("Testing connection...")
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Get database and collection
    db = client.word_definitions
    definitions = db.definitions
    
    # Insert a test document
    result = definitions.insert_one({
        "word": "test",
        "definition": "A test entry to verify database connection",
        "test": True
    })
    print("Successfully inserted test document!")
    
    # Find and print the test document
    test_doc = definitions.find_one({"test": True})
    print("Retrieved test document:", test_doc)
    
    # Clean up - remove test document
    definitions.delete_one({"test": True})
    print("Cleaned up test document")
    
except Exception as e:
    print(f"\nAn error occurred: {str(e)}")
    print("Exception type:", type(e).__name__)
    exit(1) 