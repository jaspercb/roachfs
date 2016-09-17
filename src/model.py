from sqlalchemy import String, LargeBinary, Integer, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class File(Base):
	__tablename__ = 'file'

	path = Column(String(2048), primary_key=True)
	blob = Column(LargeBinary)
	last_updated = Column(Integer)

	def __repr__(self):
		return '%s: last updated %s' % (self.path, self.last_updated)

