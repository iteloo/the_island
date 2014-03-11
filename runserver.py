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
    helpers.compile_coffeescript('js', 'main.js')

# Convention over configuration dictates that we 
# choose a default port in the case that the user 
# doesn't have one specified. The default port is 8888
if args.p:
    port = int(args.p)
elif 'PORT' in os.environ:
    port = int(os.environ['PORT'])
else:
    port = 8888

# run server
server.run(port)