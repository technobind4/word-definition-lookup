from pymongo import MongoClient
from urllib.parse import quote_plus
import certifi

# Encode username and password
username = quote_plus("singaworks")
password = quote_plus("9zwRAo8ufwa8fKjR")

# Build the connection string
MONGO_URI = f"mongodb+srv://{username}:{password}@word-definitions.e6nmtti.mongodb.net/?retryWrites=true&w=majority"

print("Attempting to connect to MongoDB...")
try:
    # Create a MongoDB client
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    
    # Test the connection
    print("Testing connection...")
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Get database and collection
    print("Accessing database...")
    db = client.word_definitions
    definitions = db.definitions
    
    # Insert a test document
    print("Inserting test document...")
    result = definitions.insert_one({
        "word": "test",
        "definition": "A test entry to verify database connection",
        "test": True
    })
    print(f"Successfully inserted test document with ID: {result.inserted_id}")
    
    # Find and print the test document
    print("\nRetrieving test document...")
    test_doc = definitions.find_one({"test": True})
    print("Retrieved test document:", test_doc)
    
    # Clean up
    print("\nCleaning up test document...")
    definitions.delete_one({"test": True})
    print("Test document deleted")
    
except Exception as e:
    print(f"\nAn error occurred: {str(e)}")
    print(f"Error type: {type(e).__name__}")
    if 'client' in locals():
        client.close() 