#!/usr/bin/env python

from backend import server
from backend import helpers

import argparse
import os


# parse command arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', help="Compile the coffee script", action='store_true')
parser.add_argument('-p', help="Port to run the server on")
args = parser.parse_args()

# compile coffeescript
if args.c:
    helpers.compile_coffeescript('js', 'assets/main.js')

# get port from args, otherwise from environ vars
port = int(args.p if args.p else os.environ['PORT'])

# run server
server.run(port)