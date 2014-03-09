 _____ _   _  _____   _____ _____ _       ___   _   _______  
|_   _| | | ||  ___| |_   _/  ___| |     / _ \ | \ | |  _  \ 
  | | | |_| || |__     | | \ `--.| |    / /_\ \|  \| | | | | 
  | | |  _  ||  __|    | |  `--. \ |    |  _  || . ` | | | | 
  | | | | | || |___   _| |_/\__/ / |____| | | || |\  | |/ /  
  \_/ \_| |_/\____/   \___/\____/\_____/\_| |_/\_| \_/___/   

- 			 version  	:	0
-			 author 	:	Colin Merkel + Leo Hsu

----------------------------------------------------
WHAT IS THIS THING?
----------------------------------------------------

I do not know.

----------------------------------------------------
SETUP AND CONFIGURATION BEFORE RUNNING
----------------------------------------------------

You need to first the project dependencies. We recommend using `virtualenvwrapper`

1. Install `python 3.3` and `pip`
2. Install `virtualenvwrapper` using `pip`:
    `pip install virtualenvwrapper`
3. Setup a virtualenv:
    `mkvirtualenv the_island`
3. Inside the virtualenv, install all project dependencies:
    `pip install -r requirements.txt`

Finally, edit the configurations:

4. Edit the configuration parameters in `configuration.json`
5. Edit the configuration parameters in `backend/server.py`

----------------------------------------------------
ADDING GIT ATTRIBUTE FILTER
----------------------------------------------------

To automate the editing of configuration.json when pushing to and pulling from the server, add the following code to your .git/config file, replacing <<host>> and <<port>> with the appropriate values:

[filter "config"]
	clean = sed -e 's/<<host>>:<<port>>/HOST_IP_HERE/'
	smudge = sed -e 's/HOST_IP_HERE/<<host>>:<<port>>/'
	required

For this to work, you must also keep the .gitattributes file in the top level of this repo. 

----------------------------------------------------
COMPILING THE COFFEESCRIPT
you need a coffeescript compiler (e.g. node.js) to 
turn coffeescript into Javascript.
----------------------------------------------------

The preferred coffeescript compile routing is to move into the code directory, then run

coffee -wc --join assets/main.js js

which will compile all of the files together into the main.js Javascript file.