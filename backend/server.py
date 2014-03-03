from backend import message
from backend import player

import tornado.ioloop
import tornado.web
import time


# Configurable parameters for the server:
# todo: load from config file
# -------------------------------------- #
PORT = 8888
RUN_DATE = time.strftime("%H:%M:%S on %B %d %Y")
VERSION = '0'
# -------------------------------------- #


class DebugStaticFileHandler(tornado.web.StaticFileHandler):
    """Static file handler override class is used to force caching to be turned off for all static files, which is a debugging measure."""

    def set_extra_headers(self, path):
        # This is necessary to prevent Chrome from caching everything. Can be safely removed when debugging is over.
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


application = tornado.web.Application([
    (r"/json", message.MessageHandler, {'delegate_class': player.Player}),
    (r"/()", DebugStaticFileHandler, {'path': 'web.html'}),
    (r"/(.*)", DebugStaticFileHandler, {'path': '.'})
])
# This starts the application
application.listen(PORT)
# start main event loop
tornado.ioloop.IOLoop.instance().start()
