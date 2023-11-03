from fastapi import APIRouter, Depends
import logging
from api.utils.database_utils import init_database, search_magnet, DatabaseConnection

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/search/{query}", response_model=dict)
async def search(query: str):
    try:
        logger.info("Searching")
        matching_magnets = search_magnet(f"%{query}%")  # Use "%" as wildcard before and after the query
        results = [{"magnet_url": magnet_url, "name": name} for magnet_url, name in matching_magnets]
        return {"magnets": results}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
