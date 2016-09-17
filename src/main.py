import time

from sqlalchemy import create_engine
from sqlalchemy.orm import create_session

from model import File, UpdateLog
from monitor import Monitor

DB_PATH = 'cockroachdb://root@104.196.166.206:26257/roachfs'

def connect_db():
	engine = create_engine(DB_PATH)
	File.metadata.create_all(engine)
	UpdateLog.metadata.create_all(engine)
	return engine

def start_monitor(engine):
    monitor = Monitor(engine)
    monitor.start()

def main():
    engine = None
    monitor = None
    try:
        engine = connect_db()
        monitor = start_monitor(engine)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    finally:
        if monitor:
            monitor.stop()
        if engine:
            engine.dispose()

if __name__ == '__main__':
	main()

