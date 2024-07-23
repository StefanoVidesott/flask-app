from flask import Blueprint
from models import User

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return "<h1>Hello from routes!</h1><p>Check out the <a href='/users'>users</a>!</p>"
#enddef

@app.route('/users')
def users():
    _template = "<h1>User list</h1>"
    _template += "<ul>"
    for user in User.get_all():
        _template += f"<li>{user.username}</li>"
    #endfor
    _template += "</ul>"
    return _template
#enddef
