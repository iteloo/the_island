from backend import message
from backend import player
from backend import helpers

import tornado.ioloop
import tornado.web
import time


# Configurable parameters for the server:
VERSION = '0'
PORT = None
RUN_DATE = None


class DebugStaticFileHandler(tornado.web.StaticFileHandler):
    """Static file handler override class is used to force caching to be turned off for all static files, which is a debugging measure."""

    def set_extra_headers(self, path):
        # This is necessary to prevent Chrome from caching everything. Can be safely removed when debugging is over.
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


def run(port):
    # set server vars
    global PORT
    global RUN_DATE
    PORT = port
    RUN_DATE = time.strftime("%H:%M:%S on %B %d %Y")

    # start application
    application = tornado.web.Application([
        (r"/json", message.MessageHandler, {'delegate_class': player.Player}),
        (r"/()", DebugStaticFileHandler, {'path': 'web.html'}),
        (r"/(.*)", DebugStaticFileHandler, {'path': '.'})
    ])
    application.listen(PORT)
    helpers.print_header("==> Starting server on port %d" % PORT)

    # start main event loop
    tornado.ioloop.IOLoop.instance().start()
