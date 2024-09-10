# app/api/keywords_api.py
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

KEYWORDS_FILE_PATH = "app/keywords.json"

class KeywordUpdate(BaseModel):
    queries: list[str]

@router.get("/keywords", response_model=list[str])
async def get_keywords():
    """Fetch current search keywords."""
    if os.path.exists(KEYWORDS_FILE_PATH):
        with open(KEYWORDS_FILE_PATH, 'r') as f:
            data = json.load(f)
            return data['queries']
    else:
        raise HTTPException(status_code=404, detail="Keywords file not found.")

@router.put("/keywords", response_model=list[str])
async def update_keywords(keywords: KeywordUpdate):
    """Update the search keywords."""
    try:
        with open(KEYWORDS_FILE_PATH, 'w') as f:
            json.dump({"queries": keywords.queries}, f)
        return keywords.queries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating keywords: {str(e)}")
