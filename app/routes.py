from flask import Blueprint

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return "<h1>Hello from routes!</h>"
#enddef
