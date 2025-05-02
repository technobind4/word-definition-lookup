from pymongo import MongoClient
import certifi
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
mongo_username = os.getenv("MONGO_USERNAME")
mongo_password = os.getenv("MONGO_PASSWORD")
mongo_cluster = os.getenv("MONGO_CLUSTER", "word-definitions.e6nmtti.mongodb.net")

if not all([mongo_username, mongo_password]):
    raise RuntimeError("MongoDB credentials are not set. Please check your .env file")

# Construct MongoDB URI
MONGO_URI = f"mongodb+srv://{quote_plus(mongo_username)}:{quote_plus(mongo_password)}@{mongo_cluster}/?retryWrites=true&w=majority"

# Initialize MongoDB client with SSL certificate verification
mongo_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = mongo_client.word_definitions
definitions_collection = db.definitions

# Get all definitions
definitions = list(definitions_collection.find({}))

print(f"\nTotal definitions stored: {len(definitions)}\n")
print("Stored definitions:")
print("-" * 50)
for def_doc in definitions:
    print(f"Word: {def_doc['word']}")
    print(f"Definition: {def_doc['definition']}")
    print(f"Created at: {def_doc['created_at']}")
    print("-" * 50) 