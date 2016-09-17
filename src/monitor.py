import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Handler(FileSystemEventHandler):
    """File system handler."""
    def on_any_event(self, event):
        logging.info('Received %s', event)


class Monitor(object):
    dir_path = None
    def __init__(self, dir_path='.'):
        self.dir_path = dir_path

    def start(self):
        logging.info('Starting filesystem watcher.')
        event_handler = Handler()
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
