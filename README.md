     _____ _   _  _____   _____ _____ _       ___   _   _______ 
    |_   _| | | ||  ___| |_   _/  ___| |     / _ \ | \ | |  _  \
      | | | |_| || |__     | | \ `--.| |    / /_\ \|  \| | | | |
      | | |  _  ||  __|    | |  `--. \ |    |  _  || . ` | | | |
      | | | | | || |___   _| |_/\__/ / |____| | | || |\  | |/ / 
      \_/ \_| |_/\____/   \___/\____/\_____/\_| |_/\_| \_/___/  
                                                            
                                                            
- version  : 0
- author : Colin Merkel + Leo Hsu


## Setup and starting the server

You need to first install the project dependencies. We recommend using virtualenvwrapper: 

1. Install Python 3.3 and pip
1. Install virtualenvwrapper using pip:

        pip install virtualenvwrapper

1. Setup a virtualenv:

        mkvirtualenv the_island

1. Inside the virtualenv, install all project dependencies:

        pip install -r requirements.txt

To start the server using Foreman, follow [these instructions](https://github.com/iteloo/the_island/wiki/Developing-using-Heroku). If for some reason you do not want to use Foreman, simply run

    python runserver.py
    
to start the server on the default port 8888. If you would like the coffeescript to be compiled before the server starts, add a `-c` option. 

## Running the test suites

### Python/server-based test suites:

In the project directory, run

     python -m unittest
     
To produce verbose output, run

     python -m unittest discover -v

### JS/client-based test suite:

1. Start the server.
2. Access `http://localhost:PORT/test`.

## Compiling the coffeescript manually

If you would like to compile the coffeescript into javascript without running the server, you can manually do so using a coffeescript compiler (e.g. node.js). 

In the project directory, run

    coffee -wc --join assets/main.js js

which will compile all of the files together into the `main.js` Javascript file. Add a `-w` option to automatically recompile when the source is updated. 
