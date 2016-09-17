import sys
import os
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import watchdog.events as e

from sqlalchemy.orm import create_session

from model import File, UpdateLog

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Handler(FileSystemEventHandler):
    def __init__(self, engine):
        self.engine = engine
        self.session = create_session(bind=engine)

    def __del__(self):
        self.session.close()

    def upload_file(self, path):
        with open(path, 'rb') as file:
            data = file.read()
        md = int(os.path.getmtime(path))

        self.session.begin()
        fobj = self.session.query(File).filter_by(path=path).first()
        if fobj:
            fobj.last_updated = md
            fobj.blob = data
        else:
            fobj = File(path=path, last_updated=md, blob=data)
            self.session.add(fobj)

        self.session.add(UpdateLog(path=path, last_updated=md, deleted=False))

        self.session.commit()

    def remove_file(self, path):
        self.session.begin()
        fobj = self.session.query(File).filter_by(path=path).first()
        if fobj:
            self.session.delete(fobj)
        md = int(time.time())
        self.session.add(UpdateLog(path=path, last_updated=md, deleted=True))
        self.session.commit()

    """File system handler."""
    def on_any_event(self, event):
        print >> sys.stderr, "%s" % event
        if isinstance(event, (e.FileCreatedEvent, e.FileModifiedEvent)):
            self.upload_file(event.src_path)
        if isinstance(event, e.FileDeletedEvent):
            self.remove_file(event.src_path)

class Monitor(object):
    dir_path = None
    def __init__(self, engine=None, dir_path='.'):
        self.dir_path = dir_path
        self.engine = engine

    def start(self):
        logging.info('Starting filesystem watcher.')
        event_handler = Handler(self.engine)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.dir_path, recursive=True)
        self.observer.start()
        logging.info('Started filesystem watcher.')

    def stop(self):
        logging.info('Stopping filesystem watcher...')
        self.observer.stop()
        self.observer.join()
        logging.info('Stopped filesystem watcher.')

if __name__ == '__main__':
    
    monitor = Monitor()
    monitor.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
