import logging
from fastapi import FastAPI
import uvicorn
from api.handlers.torrent_handler import router as torrent_router
from api.utils.database_utils import init_database, close_database
from api.utils.torrent_utils import scan_and_process_torrents, torrent_detector

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("Torrent Searcher")

logger.info("Starting FastAPI application...")

init_database()

logger.info("Starting torrent scanning...")

app = FastAPI()

app.include_router(torrent_router)

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
    scan_and_process_torrents()
