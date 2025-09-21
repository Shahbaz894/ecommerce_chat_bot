from astrapy import DataAPIClient
import os

# Load token from environment variable
ASTRA_TOKEN = os.getenv("ASTRA_DB_TOKEN")
ASTRA_DB_URL = "https://39077156-05eb-46f5-80c3-55be2964c72b-us-east-2.apps.astra.datastax.com"

# Initialize client
client = DataAPIClient(ASTRA_TOKEN)
db = client.get_database_by_api_endpoint(ASTRA_DB_URL)

def get_collection(name: str):
    """Return a collection object by name"""
    return db.get_collection(name)
