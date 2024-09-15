# app/api/etdqn_scraping_api.py
from fastapi import APIRouter, HTTPException
from services.etdqn import ETDQN

router = APIRouter()

@router.post("/scraping_decision/")
async def etdqn_scraping_decision(video_metadata: dict):
    try:
        # Convert video metadata to state representation
        state = [video_metadata['title'], video_metadata['description']]  # Simplified
        
        # Initialize ETDQN and make a decision
        etdqn = ETDQN(input_dim=2, output_dim=2)
        action = etdqn.choose_action(state)

        if action == 1:
            return {"decision": "scrape"}
        else:
            return {"decision": "skip"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in ETDQN scraping decision: {str(e)}")
