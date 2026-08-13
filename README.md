# Mere Mood Meri Marzi (MMMM)

A production-ready, highly responsive web application that recommends movies based on your mood using the Gemini API and TMDB API. 

## Features
- Natural language mood parsing using Gemini AI.
- Movie discovery, posters, ratings from TMDB.
- Real-time OTT platform streaming availability.
- Beautiful, Bollywood-inspired UI with Framer Motion animations.

## Prerequisites
- Node.js (v18+)
- Python (3.9+)

## Setup Instructions

### 1. Backend (FastAPI)
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your API keys:
   - `GEMINI_API_KEY`: Get from Google AI Studio.
   - `TMDB_API_KEY`: Get from TMDB Developer portal.
6. Start the server: `uvicorn main:app --reload`
   - Runs on `http://localhost:8000`

### 2. Frontend (React + Vite)
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
   - Runs on `http://localhost:5173`
