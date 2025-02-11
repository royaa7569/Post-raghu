import requests
import time

# Load Token & Comment
with open("token.txt", "r") as f:
    ACCESS_TOKEN = f.read().strip()
with open("comments.txt", "r") as f:
    COMMENT_TEXT = f.read().strip()

# Function to Extract Post ID from URL
def extract_post_id(post_url):
    parts = post_url.split("/")
    for part in parts:
        if part.isdigit():
            return part
    return None

# User Inputs
POST_URL = input("Enter Facebook Post URL: ").strip()
DELAY = int(input("Enter Delay in Seconds (0 for no delay): ").strip())

# Extract Post ID
POST_ID = extract_post_id(POST_URL)
if not POST_ID:
    print("❌ Invalid Post URL!")
    exit()

# Facebook API Endpoint
url = f"https://graph.facebook.com/{POST_ID}/comments"
params = {"message": COMMENT_TEXT, "access_token": ACCESS_TOKEN}

# Wait if delay is set
if DELAY > 0:
    time.sleep(DELAY)

# Send Comment Request
response = requests.post(url, data=params)

# Handle Response
if response.status_code == 200:
    print("✅ Comment Posted Successfully!")
else:
    print(f"❌ Failed to Post Comment: {response.text}")
