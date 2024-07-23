from app import app, db
from routes import app as routes_blueprint
from models import create_app_context

app.register_blueprint(routes_blueprint)

if __name__ == '__main__':
    create_app_context()
    app.run(host='0.0.0.0')
#endif
