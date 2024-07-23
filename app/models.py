from sqlalchemy import Column, Integer, String
from app import db, app
from system.models import EntityModel

class User(EntityModel):
    __tablename__ = 'Users'

    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    #enddef

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
    #enddef

    @staticmethod
    def get_by_username(username):
        with app.app_context():
            return User.query.filter_by(username=username).first()
        #endwith
    #enddef

    @staticmethod
    def get_by_email(email):
        with app.app_context():
            return User.query.filter_by(email=email).first()
        #endwith
    #enddef

    @staticmethod
    def get_by_username_or_email(username, email):
        with app.app_context():
            return User.query.filter_by(username=username, email=email).first()
        #endwith
    #enddef
#endclass

def create_app_context():
    with app.app_context():
        db.create_all()
    #endwith
#enddef

if __name__ == '__main__':
    create_app_context()
#endif
