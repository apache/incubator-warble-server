# Apache Warble (incubating) Server Package
This is going to be the master server for Apache Warble (incubating).


## Setup instructions:

* download Warble Server (or clone if you dare!)
* run `python3 setup/setup.py` and follow the instructions
* fire up the main application as WSGI, for instance via gunicorn: 
* * `cd /path/to/warble/api`
* * `gunicorn -w 10 -b 127.0.0.1:8000 handler:application -t 120 -D`


