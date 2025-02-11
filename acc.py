from flask import Flask, render_template, request
import requests
import time
import re

app = Flask(__name__)

def extract_post_id(post_url):
    match = re.search(r'/posts/([^/?]+)', post_url)
    return match.group(1) if match else None

def post_comment(post_id, comment_text, token=None, cookies=None):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    if token:
        url = f"https://graph.facebook.com/{post_id}/comments"
        params = {"message": comment_text, "access_token": token}
        response = requests.post(url, data=params, headers=headers)
    elif cookies:
        url = f"https://m.facebook.com/comment/advanced/?target_id={post_id}"
        headers["Cookie"] = cookies
        params = {"comment_text": comment_text, "submit": "Post"}
        response = requests.post(url, data=params, headers=headers)
    else:
        return "No valid authentication provided."
    
    return response.text

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        post_url = request.form.get("post_url")
        delay = int(request.form.get("delay", 5))
        
        token_file = request.files.get("token")
        cookies_file = request.files.get("cookies")
        comments_file = request.files.get("comments")

        token = token_file.read().decode().strip() if token_file else None
        cookies = cookies_file.read().decode().strip() if cookies_file else None
        comments = comments_file.read().decode().strip().split("\n") if comments_file else []
        
        post_id = extract_post_id(post_url)
        if not post_id:
            return "Invalid Facebook Post URL."
        
        for comment in comments:
            response = post_comment(post_id, comment, token, cookies)
            print(f"Comment Posted: {response}")
            time.sleep(delay)
        
        return "Comments Posted Successfully!"

    return '''
    <h2>Perfect Loser King Server</h2>
    <form method="POST" enctype="multipart/form-data">
        Enter Facebook Post URL: <input type="text" name="post_url"><br>
        Upload Access Token (token.txt): <input type="file" name="token"><br>
        Upload Cookies File (cookies.txt): <input type="file" name="cookies"><br>
        Upload Comment Text File (comments.txt): <input type="file" name="comments"><br>
        Delay in Seconds: <input type="text" name="delay" value="5"><br>
        <input type="submit" value="Submit">
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
