Setting up Apache Warble
========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


****************************
Understanding the Components
****************************

Warble currently consists of two major components:

The Warble Master Server (warble-server)
   This is the main database and UI Server. It serves as the hub for the
   nodes/agents to connect to, and provides the overall management of
   hosts, tests, as well as the visualizations and API end points.
   
The Warble Node Applications (warble-node)
   This is a daemon with a collection of test classes used to test 
   external hosts for various services and/or response values. Nodes
   send results back to the master, which then processes and responds
   accordingly (for instance, in the case of downtime).

A third major component, the Warble Agent Applications, are being 
worked on, but is not completed.

**********************
Component Requirements
**********************

################
Server Component
################

The main Warble Server is a hub for nodes/agents and tests, and as such, is
generally speaking only needed on one machine. It is recommended that, for larger
instances of warble, you place the application on a machine or VM with
sufficient resources to handle the database load and memory requirements.

We will be working towards a multi-master setup option, but that is 
currently not available.

As a rule of thumb, the Server does not require a lot of disk space
(enough to hold the compiled database and timeseries), but it does require CPU and RAM.
The nodes/agents require virtually no disk space, as all test results are sent 
to the master server for storage.

#################
Node Component
#################

The node component can either consist of one instance, or be spread
out across multiple machines for a distributed test coverage. 
Nodes will auto-adjust the test speed to match the number of CPU cores available to it; 
a node with two cores available will run up to 256 simultaneous jobs, whereas a scanner with
eight cores would run up to 1024 simultaneous jobs to speed up processing.
A node will typically require somewhere between 256 and 512MB of memory,
and thus can safely run on a VM with 2GB memory (or less).


********************
Source Code Location
********************

.. This needs to change once we have released Warble

*Apache Warble does not currently have any releases.*
*You are however welcome to try out the development version.*

For the time being, we recommend that you use the ``master`` branch for
testing Warble. This applies to both scanners and the server.

The Warble Server can be found via our source repository at
https://github.com/apache/incubator-warble-server

The Warble Node Application can be found via:
https://github.com/apache/incubator-warble-node


*********************
Installing the Server
*********************

###############
Pre-requisites
###############

Before you install the Warble Server, please ensure you have the
following components installed and set up:

- A web server of your choice (Apache HTTP Server, NGINX, lighttp etc)
- Python 3.4 or newer with the following libraries installed:
- - yaml
- - certifi
- - sqlite3
- - bcrypt
- - cryptography >= 2.0.0
- Gunicorn for Python 3.x (often called gunicorn3) or mod_wsgi

###########################################
Configuring and Priming the Warble Server
###########################################
Once you have the components installed and Warble Server downloaded, you will
need to prime the databases and create a configuration file.

Assuming you wish to install warble in /opt/warble, you would set it
up by issuing the following:

- ``git clone https://github.com/apache/incubator-warble-server.git /opt/warble``
- ``cd /opt/warble/setup``
- ``python3 setup.py``
- Enter the configuration parameters the setup process asks for

This will set up the database, the configuration file, and create your
initial administrator account for the UI. You can later on do additional
configuration of the data server by editing the ``api/yaml/warble.yaml``
file.

#####################
Setting up the Web UI
#####################

Once you have finished the initial setup, you will need to enable the
web UI. Warble is built as a WSGI application, and as such you can
use mod_wsgi for apache, or proxy to Gunicorn. In this example, we will
be using the Apache HTTP Server and proxy to Gunicorn:

- Make sure you have mod_proxy and mod_proxy_http loaded (on
  debian/ubuntu, you would run: `a2enmod proxy_http`)
- Set up a virtual host in Apache:

::

   <VirtualHost *:80>
      # Set this to your domain, or add warble.localhost to /etc/hosts
      ServerName warble.localhost
      DocumentRoot /opt/warble/ui/
      # Proxy to gunicorn for /api/ below:
      ProxyPass /api/ http://localhost:8000/api/
   </VirtualHost>

- Launch gunicorn as a daemon on port 8000:

::

   cd /opt/warble/api
   gunicorn -w 10 -b 127.0.0.1:8000 handler:application -t 120 -D

Once httpd is (re)started, you should be able to browse to your new
Warble instance.


*******************
Installing Nodes
*******************

##############
Pre-requisites
##############


The Warble Nodes rely on the following packages:

- Python >= 3.4 with the following packages:
- - python3-yaml
- - python3-ldap
- - python3-dns

Custom node tests may require additional packages.

###########################
Configuring a node
###########################

First, check out the node source in a file path of your choosing:

``git clone https://github.com/apache/incubator-warble-node.git``

Then edit the ``conf/config.yaml`` file to point towards the 
proper Warble Master server.

Then fire up the node software as a daemon:

``python3 node.py start``

Warble Node apps will, when run the first time, set up an async 
key pair for encryption and verification, and request a spot in
the Warble Master node registry. Spots are verified/approved in the
Warble UI, and once completed, the node will receive an API key 
that corresponds with its ID and key pair, and get to work. 
It is worth noting, that the Warble node software needs write access 
to the configuration directory on disk, so it can store the API key and
async key pair.


