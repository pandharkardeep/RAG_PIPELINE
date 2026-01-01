# RAG Pipeline Project

A full-stack application for news ingestion and retrieval using Angular frontend and FastAPI backend.

## Project Structure

```
RAG_PIPELINE/
├── Backend/          # FastAPI backend server
├── Frontend_RAG/     # Angular frontend application
└── SYSTEM_DESIGN.md  # System design documentation
```

## Setup Instructions

### Backend Setup

1. Navigate to the Backend directory:
   ```bash
   cd Backend
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install fastapi uvicorn requests pydantic
   ```

5. Configure your API keys:
   - Copy `config.example.py` to `config.py`
   - Edit `config.py` and add your RapidAPI key
   - Get your API key from: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-news-data

6. Run the backend server:
   ```bash
   python main.py
   ```
   Server will start at `http://localhost:8000`

### Frontend Setup

1. Navigate to the Frontend_RAG directory:
   ```bash
   cd Frontend_RAG
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   ng serve
   ```
   Application will be available at `http://localhost:4200`

## Configuration

### Backend Configuration (`Backend/config.py`)
- `BASE_URL`: Backend API base URL
- `RAPIDAPI_KEY`: Your RapidAPI key for news data
- `ALLOWED_ORIGINS`: CORS allowed origins
- `HOST` and `PORT`: Server host and port settings

### Frontend Configuration (`Frontend_RAG/src/environments/`)
- `environment.ts`: Development environment settings
- `environment.prod.ts`: Production environment settings

## API Endpoints

### GET `/news_ingestion`
Fetch news articles based on query and limit.

**Query Parameters:**
- `query` (string): Search query for news articles
- `limit` (int): Number of articles to retrieve

**Example:**
```
GET http://localhost:8000/news_ingestion?query=Transport&limit=10
```

## Important Notes

- **Never commit `config.py`** - It contains your API keys
- Always use `config.example.py` as a template
- The backend virtual environment (`venv/`) is excluded from git
- Node modules are excluded from git

## Technologies Used

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: Angular, TypeScript, RxJS
- **API**: RapidAPI Real-Time News Data
