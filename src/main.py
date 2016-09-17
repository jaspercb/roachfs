from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from model import File

DB_PATH = 'cockroachdb://root@104.196.166.206:26257/roachfs'

def connect_db():
	engine = create_engine(DB_PATH)
	File.metadata.create_all(engine)
	return engine

def main():
	engine = connect_db()

	sess = create_session(bind=engine)
	print sess.query(File).all()
	sess.close()

if __name__ == '__main__':
	main()

