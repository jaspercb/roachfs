from sqlalchemy import String, LargeBinary, Integer, Column, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class File(Base):
    __tablename__ = 'file'

    path = Column(String(2048), primary_key=True)
    blob = Column(String)
    last_updated = Column(Integer)

    def __repr__(self):
        return ('<File: path:{0}, last_updated:{1}>'
                .format(self.path, self.last_updated))

class UpdateLog(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    path = Column(String(2048))
    last_updated = Column(Integer, index=True)
    deleted = Column(Boolean)

    def __repr__(self):
        return ('<UpdateLog: id:{0}, path:{1}, last_updated:{2}, deleted:{3}>'
                .format(self.id, self.path, self.last_updated, self.deleted))
