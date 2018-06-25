#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

WARBLE_VERSION = '0.1.0' # ABI/API compat demarcation.
WARBLE_DB_VERSION = 1 # First DB version evah!

import sys

if sys.version_info <= (3, 3):
    print("This script requires Python 3.4 or higher")
    sys.exit(-1)

import os
import sys

# Test for additional imports, bork if not found
try:
    import yaml
    import bcrypt
    import sqlite3
except:
    print("Looks like you are missing a few python 3 libraries")
    print("Warble needs the following py3 libs to work: yaml, bcrypt, sqlite3")
    print("Please install these libraries before continuing")
    sys.exit(-1)
    
# Figure out absolute setup and api paths
setup_path = os.path.dirname(os.path.realpath(__file__))
api_path = os.path.realpath("%s/../api" % setup_path)
db_path = os.path.realpath("%s/../db" % setup_path)

# Open the DB setup instructions and sample warble server config
dbsetup = yaml.load(open("%s/dbs.yaml" % setup_path))
myyaml = yaml.load(open("%s/warble.yaml.sample" % setup_path))

# Set up database path
datapath = input("Where would you like to put the Warble databases?: [%s]" % db_path).strip()
if not datapath:
    datapath = db_path
print("Creating databases...")
if not os.path.isdir(datapath):
    print("Creating directory %s" % datapath)
    try:
        os.mkdir(datapath)
    except Exception as err:
        print("Could not create database directory: %s" % err)
        sys.exit(-1)

# Set up individual databases (sqlite only for now!!)
for name, settings in dbsetup.items():
    if settings['driver'] == 'sqlite':
        db_filepath = os.path.join(datapath, settings['path'])
        if os.path.exists(db_filepath):
            print("Database %s already exists, skipping!" % db_filepath)
            continue
        else:
            print("Creating database file %s" % db_filepath)
            conn = sqlite3.connect(db_filepath)
            cursor = conn.cursor()
            # create a CREATE statement from the yaml layout
            cstate = "CREATE TABLE %s (%s)" % (
                name,
                ", ".join( ["%s %s" % (k, v) for k, v in settings['layout'].items()] )
                )
            cursor.execute(cstate)
            conn.commit()
            conn.close()

# Generate a super user
supername = input("Please enter the username of the primary super user to create [admin]: ").strip()
if not supername:
    supername = 'admin'
superpass = input("Please enter the password for the super user account: ").strip()

# Digest pass with bcrypt
salt = bcrypt.gensalt()
pwd = bcrypt.hashpw(superpass.encode('utf-8'), salt).decode('ascii')

# Save user to new DB
db_filepath = os.path.join(datapath, 'accounts.db')
conn = sqlite3.connect(db_filepath)
c = conn.cursor()
try:
    c.execute("INSERT INTO `accounts` (`userid`, `password`, `superuser`) VALUES (?, ?, 1)", (supername, pwd))
    conn.commit()
    print("Saved new super user account %s in %s" % (supername, db_filepath))
except sqlite3.IntegrityError:
    print("WARNING: Could not add super user - is the user already in the DB?!")
conn.close()


# Write new warble yaml config
warble_yaml_path = '%s/yaml/warble.yaml' % api_path
print("Writing API server config to %s" % warble_yaml_path)
if os.path.exists(warble_yaml_path):
    print("WARNING: Warble YAML already exists on disk, skipping this step!!")
else:
    myconfig = {
        'database': {
            'version': WARBLE_DB_VERSION,
            'driver': 'sqlite',
            'path': datapath
        },
        'mail': {
            'host': 'localhost',
            'port': 25,
            'sender': 'Apache Warble<warble@demo.warble.xyz>'
        }
    }
    with open(warble_yaml_path, "w") as f:
        f.write(yaml.dump(myconfig, default_flow_style = False))
        f.close()

    
print("All done, Warble should...work now :)")
print("If needed, you can fine tune %s to suit your needs." % warble_yaml_path)

