import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'firebase_credentials.json'

# Define the scopes required for the access token
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

# Load the service account credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

# Refresh the credentials to get a new access token
credentials.refresh(Request())

# Print the access token
print('Access Token:', credentials.token)
