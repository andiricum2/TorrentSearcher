import os
import sqlite3
import logging
import bencodepy
import hashlib
import base64
import time

# Create a logger for the module
logger = logging.getLogger(__name__)

DATABASE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'torrents.db'))
TORRENTS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'torrents'))

def add_magnet_to_database(magnet_url, name):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Create the Magnets table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Magnets (
                id INTEGER PRIMARY KEY,
                magnet_url TEXT,
                name TEXT
            )
        ''')

        # Check if the b32hash of the magnet URL exists in the database
        cursor.execute("SELECT magnet_url FROM Magnets WHERE magnet_url LIKE ?", (f"%{magnet_url}%",))
        existing_magnet = cursor.fetchone()

        if not existing_magnet:
            # Insert the magnet URL and other metadata into the database
            cursor.execute("INSERT INTO Magnets (magnet_url, name) VALUES (?, ?)", (magnet_url, name))
            conn.commit()
            logger.debug(f"Added link: {magnet_url}, Name: {name}")
        else:
            logger.debug(f"Skipped existing link: {magnet_url}, Name: {name}")

        conn.close()
    except Exception as e:
        logger.error(f"Error adding magnet to the database: {str(e)}")

# Function to scan and process torrents
def torrent_detector():
    time.sleep(10)
    logger.debug("Scanning Torrents")
    scan_and_process_torrents()

def scan_and_process_torrents():
    for filename in os.listdir(TORRENTS_DIRECTORY):
        if filename.endswith(".torrent"):
            logger.debug(f"Processing torrent file: {filename}")
            torrent_file_path = os.path.join(TORRENTS_DIRECTORY, filename)
            magnet_url, name = make_magnet_data_from_file(torrent_file_path)
            if magnet_url:
                add_magnet_to_database(magnet_url, name)
                # Optionally, remove the torrent file after processing
                os.remove(torrent_file_path)
        else:
            logger.debug(f"Ignoring non-torrent file: {filename}")
    torrent_detector()

def make_magnet_data_from_file(torrent_file_path):
    try:
        with open(torrent_file_path, 'rb') as torrent_file:
            torrent_data = torrent_file.read()
            decoded_data = bencodepy.decode(torrent_data)

            info_data = decoded_data.get(b'info')
            if info_data:
                info_hash = hashlib.sha1(bencodepy.encode(info_data)).digest()
                b32hash = base64.b32encode(info_hash).decode()

                magnet_url = 'magnet:?xt=urn:btih:' + b32hash

                name = os.path.splitext(os.path.basename(torrent_file_path))[0]

                logger.debug(f"Created magnet link from torrent: {magnet_url}")
                return magnet_url, name
            else:
                logger.error("Error: 'info' dictionary not found in the torrent file.")
                return None, None, None

    except Exception as e:
        logger.error(f"Error creating magnet link from torrent: {str(e)} file: {str(torrent_file_path)}")
        return None, None, None