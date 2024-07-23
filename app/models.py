from sqlalchemy import Column, Integer, String
from app import db, app

class User(db.Model):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
    #enddef

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
    #enddef

    def save(self):
        db.session.add(self)
        db.session.commit()
    #enddef

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    #enddef

    @staticmethod
    def get_all():
        return User.query.all()
    #enddef

    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
    #enddef

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()
    #enddef

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()
    #enddef

    @staticmethod
    def get_by_username_or_email(username, email):
        return User.query.filter_by(username=username).filter_by(email=email).first()
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
