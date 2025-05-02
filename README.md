# Word Definition Lookup

A web application that provides word definitions using OpenAI's GPT-3.5 API and stores them in MongoDB for quick retrieval.

## Features

- Look up definitions for any word
- Get part of speech and example sentences
- Cache definitions in MongoDB for faster retrieval
- View recent lookups
- Delete stored definitions
- Modern, responsive UI

## Tech Stack

- Backend: FastAPI (Python)
- Database: MongoDB Atlas
- AI: OpenAI GPT-3.5
- Frontend: HTML, JavaScript, Tailwind CSS

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd word-definition-lookup
```

2. Install dependencies:
```bash
pip install fastapi uvicorn openai pymongo python-dotenv python-multipart certifi
```

3. Create a `.env` file in the project root by copying `.env.example`:
```bash
cp .env.example .env
```

4. Update the `.env` file with your credentials:
```bash
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Credentials (required)
MONGO_USERNAME=your_mongodb_username
MONGO_PASSWORD=your_mongodb_password
MONGO_CLUSTER=your_mongodb_cluster
```

5. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

6. Open http://localhost:8001 in your browser.

## Project Structure

- `main.py`: FastAPI application and API endpoints
- `static/index.html`: Frontend interface
- `check_mongo.py`: Utility script to check MongoDB contents
- `.env.example`: Template for environment variables
- `.env`: Your actual environment variables (not committed to Git)

## API Endpoints

- `GET /`: Main application interface
- `POST /get_definition`: Get word definition
- `GET /recent_definitions`: Get recently looked up definitions
- `DELETE /definition/{word}`: Delete a stored definition
- `GET /health`: Health check endpoint

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGO_USERNAME`: Your MongoDB username
- `MONGO_PASSWORD`: Your MongoDB password
- `MONGO_CLUSTER`: Your MongoDB cluster address
- `PORT`: Server port (default: 8001)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 