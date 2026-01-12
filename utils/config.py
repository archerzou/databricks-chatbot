import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Constants
SERVING_ENDPOINT_NAME = os.getenv("SERVING_ENDPOINT_NAME")
# SERVING_ENDPOINT_NAME is now optional - can be selected dynamically via UI

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST")
CLIENT_ID = os.environ.get("DATABRICKS_CLIENT_ID")
CLIENT_SECRET = os.environ.get("DATABRICKS_CLIENT_SECRET")

# API Configuration
API_TIMEOUT = 30.0
STREAMING_TIMEOUT = 30.0
MAX_CONCURRENT_STREAMS = 10
MAX_QUEUE_SIZE = 100

# Cache Configuration
CACHE_MAX_MESSAGES = 10
CACHE_UPDATE_INTERVAL = 24 * 60 * 60  # 24 hours in seconds

# Error Messages
ERROR_MESSAGES = {
    "rate_limit": "The service is currently experiencing high demand. Please wait a moment and try again.",
    "timeout": "Request timed out. Please try again later.",
    "not_found": "{resource_id} not found. Please ensure you're using a valid session ID.",
    "general": "An error occurred while processing your request."
} 

# Legacy URL for backward compatibility (uses default endpoint if set)
URL = f"https://{DATABRICKS_HOST}/serving-endpoints/{SERVING_ENDPOINT_NAME}/invocations" if SERVING_ENDPOINT_NAME else None


def get_serving_endpoint_url(endpoint_name: str) -> str:
    """Construct the serving endpoint URL dynamically based on the endpoint name."""
    return f"https://{DATABRICKS_HOST}/serving-endpoints/{endpoint_name}/invocations"
