import base64
import logging
import os
import sys
import threading
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import create_session, load_only

from model import File, UpdateLog

DB_PATH = 'cockroachdb://root@104.196.166.206:26257/roachfs'

def connect_db():
    engine = create_engine(DB_PATH)
    File.metadata.create_all(engine)
    return engine

def get_session():
    return create_session(bind=connect_db())

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Handler(object):
    """Handler for when the external database has stuff we don't."""
    def on_any_event(self, event):
        logging.info('Received %s', event)


class Puller(object):
    """Periodically queries the external CockroachDB for recent files."""
    dir_path = None
    def __init__(self, dir_path='.'):
        self.dir_path = dir_path
        self.last_id = 0 # TODO: FIX
        self.terminate = threading.Event()

    def start(self):
        logging.info('Starting puller.')
        self.sess = get_session()
        event_handler = Handler()
        self.thread = threading.Thread(None, self.run)
        self.thread.start()
        logging.info('Started puller.')

    def run(self):
        while not self.terminate.wait(1):
            seen_files = set()
            for update_log in self.get_new_update_logs()[::-1]:
                self.last_id = max(self.last_id, update_log.id)
                if update_log.path not in seen_files:
                    seen_files.add(update_log.path)
                    if update_log.deleted:
                        logging.info('deleting %s', update_log.path)
                        try:
                            os.remove(update_log.path)
                        except OSError:
                            pass
                    else: # New file
                        dirname, file_name = os.path.split(update_log.path)
                        if not os.path.exists(dirname):
                            logging.info('making new dir: %s', dirname)
                            os.makedirs(dirname)
                        with open(update_log.path, 'wb') as f:
                            data = self.pull_latest_file(update_log.path)
                            logging.info('writing to %s: %s', update_log.path,
                                data)
                            f.write(base64.b64decode(data.blob))

    def get_new_update_logs(self):
        return (self.sess.query(UpdateLog).order_by('last_updated')
                .filter(UpdateLog.id>self.last_id).all())

    def pull_latest_file(self, file_name):
        return self.sess.query(File).filter_by(path=file_name).first()

    def stop(self):
        logging.info('Stopping puller...')
        self.terminate.set()
        self.thread.join()
        self.sess.close()
        logging.info('Stopped puller.')

if __name__ == '__main__':

    puller = Puller()
    puller.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        puller.stop()
        puller.stop()
