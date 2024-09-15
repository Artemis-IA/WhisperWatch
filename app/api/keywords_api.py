# app/api/keywords_api.py
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from services.relevance_service import RelevanceDetectionService

router = APIRouter()

KEYWORDS_FILE_PATH = "keywords.json"

class KeywordUpdate(BaseModel):
    queries: list[str]

class AddKeywords(BaseModel):
    new_keywords: list[str]

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

@router.post("/add_keywords", response_model=dict)
async def add_keywords(add_keywords: AddKeywords):
    try:
        relevance_service = RelevanceDetectionService()

        # Load existing keywords
        if os.path.exists(KEYWORDS_FILE_PATH):
            with open(KEYWORDS_FILE_PATH, 'r') as f:
                existing_keywords = json.load(f)['queries']
        else:
            existing_keywords = []

        # Add new keywords and expand them using related terms
        updated_keywords = list(set(existing_keywords + add_keywords.new_keywords))

        for keyword in add_keywords.new_keywords:
            # Generate related keywords using embeddings
            related_keywords = relevance_service.generate_related_keywords(keyword, top_n=5)
            updated_keywords.extend(related_keywords)

        # Remove duplicates
        updated_keywords = list(set(updated_keywords))

        # Save the updated keywords
        with open(KEYWORDS_FILE_PATH, 'w') as f:
            json.dump({"queries": updated_keywords}, f)

        return {"status": "Keywords added successfully", "keywords": updated_keywords}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Keywords file not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON from the file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding keywords: {str(e)}")

@router.delete("/keyword", response_model=dict)
async def delete_keyword(keyword: str):
    try:
        if os.path.exists(KEYWORDS_FILE_PATH):
            with open(KEYWORDS_FILE_PATH, 'r') as f:
                existing_keywords = json.load(f)['queries']
        else:
            existing_keywords = []

        if keyword in existing_keywords:
            existing_keywords.remove(keyword)

            with open(KEYWORDS_FILE_PATH, 'w') as f:
                json.dump({"queries": existing_keywords}, f)

            return {"status": "Keyword deleted successfully", "keywords": existing_keywords}
        else:
            return {"status": "Keyword not found", "keywords": existing_keywords}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Keywords file not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding JSON from the file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting keyword: {str(e)}")