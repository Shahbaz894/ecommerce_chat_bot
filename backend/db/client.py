import os
from astrapy import DataAPIClient
from dotenv import load_dotenv
load_dotenv()

def connect_to_database():
    ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_TOKEN")
    ASTRA_DB_API_ENDPOINT = "https://39077156-05eb-46f5-80c3-55be2964c72b-us-east-2.apps.astra.datastax.com"

    if not ASTRA_DB_TOKEN:
        raise ValueError("❌ Missing Astra DB Token — please set ASTRA_DB_TOKEN environment variable")

    client = DataAPIClient(ASTRA_DB_TOKEN)
    db = client.get_database_by_api_endpoint(ASTRA_DB_API_ENDPOINT)
    return db
