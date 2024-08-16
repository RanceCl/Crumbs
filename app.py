from flask import Flask
app = Flask(__name__)

# Returns content
@app.route("/")
def home():
    return "That's the way the cookie crumbles!"