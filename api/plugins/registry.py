#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
########################################################################

"""
This is the client registry class for Apache Warble
"""

import uuid
import re
import time
import plugins.crypto

""" Warble node class """
class node(object):
    
    def __init__(self, session, nodeid = None):
        """ Loads a node from the registry or inits a new one """
        self._data = {}
        self.session = session
        self.conn = session.DB.sqlite.open('nodes.db')
        
        # node variables
        self.hostname = ""
        self.pem = ""
        self.id = None
        self.description = None
        self.location = None
        self.ipv6 = False
        self.verified = False
        self.enabled = False
        self.ip = "0.0.0.0"
        self.lastping = int(time.time())
        
        if nodeid:
            doc = None
            nc = self.conn.cursor()
            # Load by API Key?
            if isinstance(nodeid, str) and re.match(r"^[a-f0-9]+-[a-f0-9-]+$", nodeid):
                self.apikey = nodeid
                nc.execute("SELECT * FROM `registry` WHERE `apikey` = ? LIMIT 1", (self.apikey,))
                doc = nc.fetchone()
            # Load by Node ID?
            elif re.match(r"^[0-9]+$", str(nodeid)):
                self.id = int(nodeid)
                nc.execute("SELECT * FROM `registry` WHERE `id` = ? LIMIT 1", (self.id,))
                doc = nc.fetchone()
                
            if doc:
                self.apikey = doc['apikey']
                self.hostname = doc['hostname']
                self.pem = doc['pubkey']
                self.id = doc['id']
                self.description = doc['description']
                self.location = doc['location']
                self.ipv6 = False # TODO!
                self.verified = (doc['verified'] == 1)
                self.enabled = (doc['enabled'] == 1)
                self.ip = doc['ip']
                self.lastping = doc['lastping']
                self.version = doc['version']
                self.key = plugins.crypto.loads(self.pem)
                self.fingerprint = plugins.crypto.fingerprint(self.pem)
            else:
                raise Exception("No such node found in registry")
        # new node from scratch?
        else:
            self.apikey = str(uuid.uuid4())
        
    def save(self):
        """ Saves or updates a node in the registry """
        nc = self.conn.cursor()
        # Save a new node?
        if not self.id:
            self.fingerprint = plugins.crypto.fingerprint(self.pem)
            print("Saving node with cert %s" % self.fingerprint)
            nc.execute("INSERT INTO `registry` (`hostname`, `apikey`, `pubkey`, `verified`, `enabled`, `ip`, `lastping`, `version`) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (self.hostname, self.apikey, self.pem, 0, 0, self.ip, int(time.time()), self.version, )
                )
        # Save an existing node?
        else:
            nc.execute("UPDATE `registry` SET `hostname` = ?, `apikey` = ?, `pubkey` = ?, `location`= ?, `verified` = ?, `enabled` = ?, `ip` = ?, `lastping` = ?, `version` = ?, `description`= ? WHERE `id` = ? LIMIT 1",
                    (self.hostname, self.apikey, self.pem, self.location, 1 if self.verified else 0, 1 if self.enabled else 0, self.ip, self.lastping, self.version, self.description, self.id,)
                )
        self.conn.commit()
    
    def remove(self):
        """ Removes a node from the registry """
        nc = self.conn.cursor()
        if self.id:
            nc.execute("DELETE FROM `registry` WHERE `id` = ? LIMIT 1", (self.id, ))
            self.conn.commit()
        
    def __del__(self):
        # shut off sqlite connection
        if self.conn:
            self.conn.close()

    def __enter__(self):
        pass
    def __exit__(self, exception_type, exception_value, traceback):
        del self
    