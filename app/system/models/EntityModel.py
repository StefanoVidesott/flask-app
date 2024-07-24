from system import app, db
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class EntityModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    updated = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'
    #enddef

    def save(self):
        with app.app_context():
            db.session.add(self)
            db.session.commit()
        #endwith
    #enddef

    def delete(self):
        with app.app_context():
            db.session.delete(self)
            db.session.commit()
        #endwith
    #enddef

    @classmethod
    def get_all(cls):
        with app.app_context():
            return cls.query.all()
        #endwith
    #enddef

    @classmethod
    def get_by_id(cls, id):
        with app.app_context():
            return cls.query.get(id)
        #endwith
    #enddef
#endclass
