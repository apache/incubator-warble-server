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
This is the node task registry class for Apache Warble
"""

import uuid
import re
import time
import json

""" Warble task class """
class task(object):
    
    def __init__(self, session, taskid = None, taskrow = None):
        """ Loads a task from the registry or inits a new one """
        self._data = {}
        self.session = session
        self.conn = session.DB.sqlite.open('nodetasks.db')
        
        # task variables
        self.id = None
        self.type = None
        self.category = 0
        self.enabled = True
        self.muted = False
        self.payload = {}
        self.name = None
        
        # Load a task by ID
        if taskid:
            doc = None
            nc = self.conn.cursor()
            # Load by Task ID?
            if re.match(r"^[0-9]+$", str(taskid)):
                self.id = int(taskid)
                nc.execute("SELECT * FROM `tasks` WHERE `id` = ? LIMIT 1", (taskid,))
                doc = nc.fetchone()
                
            if doc:
                self.id = doc['id']
                self.type = doc['type']
                self.category = doc['category']
                self.enabled = True if doc['enabled'] == 1 else False
                self.muted = True if doc['muted'] == 1 else False
                self.payload = json.loads(doc['payload'])
                self.ipv6 = False # TODO!
                self.name = doc['name']
            else:
                raise Exception("No such task found in registry")
        
        # Or load a task by data row?
        elif taskrow:
            doc = taskrow
            self.id = doc['id']
            self.type = doc['type']
            self.category = doc['category']
            self.enabled = True if doc['enabled'] == 1 else False
            self.muted = True if doc['muted'] == 1 else False
            self.payload = json.loads(doc['payload'])
            self.ipv6 = False # TODO!
            self.name = doc['name']
        
        
    def save(self):
        """ Saves or updates a task in the registry """
        nc = self.conn.cursor()
        # Save a new task?
        if not self.id:
            nc.execute("INSERT INTO `tasks` (`type`, `category`, `enabled`, `muted`, `payload`, `name`) VALUES (?, ?, ?, ?, ?, ?)",
                    (self.type, self.category, 1 if self.enabled else 0, 1 if self.muted else 0, json.dumps(self.payload), self.name, )
                )
        # Update existing task?
        else:
            nc.execute("UPDATE `tasks` SET `type` = ?, `category` = ?, `enabled` = ?, `muted` = ?, `payload` = ?, `name` = ? WHERE `id` = ? LIMIT 1",
                    (self.type, self.category, 1 if self.enabled else 0, 1 if self.muted else 0, json.dumps(self.payload), self.name, self.id, )
                )
        self.conn.commit()
    
    def remove(self):
        """ Removes a task from the registry """
        nc = self.conn.cursor()
        if self.id:
            nc.execute("DELETE FROM `tasks` WHERE `id` = ? LIMIT 1", (self.id, ))
            self.conn.commit()
            
    def accesslevel(self, user):
        """ Determines if a user can view/edit a task or not """
        aclcon = session.DB.sqlite.open('nodeacl.db')
        cur = aclcon.cursor()
        cur.execute("SELECT * FROM `nodeacl` WHERE `catid` = ? AND `userid` = ? LIMIT 1", (self.category, user['userid'], ))
        acl = cur.fetchone()
        if acl:
            return ['none', 'read', 'write', 'admin'][acl['access']]
        else:
            return 'none'
        aclcon.close()
        
    def __del__(self):
        # shut off sqlite connection
        if self.conn:
            self.conn.close()

    def __enter__(self):
        pass
    def __exit__(self, exception_type, exception_value, traceback):
        del self
        
        
"""
  id:           integer primary key   # ID of category
    name:         text                  # Name of category
    description:  text                  # Short description of category
    settings:     text                  # Notification settings (JSON blob to allow for customizations)
"""
    
""" Warble task category class """
class category(object):
    
    def __init__(self, session, catid = None):
        """ Loads a category from the registry or inits a new one """
        self._data = {}
        self.session = session
        self.conn = session.DB.sqlite.open('nodecats.db')
        
        # category variables
        self.id = None
        self.name = None
        self.description = None
        self.settings = {}
        self.tasks = []
        
        # Load existing category?
        if catid:
            doc = None
            nc = self.conn.cursor()
            # Load by Cat ID?
            if re.match(r"^[0-9]+$", str(catid)):
                self.id = int(catid)
                nc.execute("SELECT * FROM `nodecats` WHERE `id` = ? LIMIT 1", (catid,))
                doc = nc.fetchone()
            if doc:
                self.id = doc['id']
                self.name = doc['name']
                self.description = doc['description']
                self.settings = json.loads(doc['settings'])
                
                # Load tasks in category
                taskcon = session.DB.sqlite.open('nodetasks.db')
                cur = taskcon.cursor()
                cur.execute("SELECT * FROM `nodetasks` WHERE `category` = ?", (self.id, ))
                for row in cur.fetchall():
                    t = task(session, taskrow = row)
                    self.tasks.append(t)
                taskcon.close()
            else:
                raise Exception("No such category found in registry")
        
        
    def save(self):
        """ Saves or updates a category in the registry """
        nc = self.conn.cursor()
        # Save a new category?
        if not self.id:
            nc.execute("INSERT INTO `nodecats` (`name`, `description`, `settings`) VALUES (?, ?, ?)",
                    (self.name, self.description, json.dumps(self.settings), )
                )
        # Update existing category?
        else:
            nc.execute("UPDATE `nodecats` SET `name` = ?, `description` = ?, `settings` = ? WHERE `id` = ? LIMIT 1",
                    (self.name, self.description, json.dumps(self.settings), self.id, )
                )
        self.conn.commit()
    
    def remove(self):
        """ Removes a category from the registry """
        nc = self.conn.cursor()
        if self.id:
            nc.execute("DELETE FROM `nodecats` WHERE `id` = ? LIMIT 1", (self.id, ))
            self.conn.commit()
            
    def accesslevel(self, user):
        """ Determines if a user can view/edit a category or not """
        aclcon = session.DB.sqlite.open('nodeacl.db')
        cur = aclcon.cursor()
        cur.execute("SELECT * FROM `nodeacl` WHERE `catid` = ? AND `userid` = ? LIMIT 1", (self.id, user['userid'], ))
        acl = cur.fetchone()
        if acl:
            return ['none', 'read', 'write', 'admin'][acl['access']]
        else:
            return 'none'
        aclcon.close()
        
    def __del__(self):
        # shut off sqlite connection
        if self.conn:
            self.conn.close()

    def __enter__(self):
        pass
    def __exit__(self, exception_type, exception_value, traceback):
        del self
    
# Wrapper for getting all tasks:
def all(session):
    tlist = []
    taskcon = session.DB.sqlite.open('nodetasks.db')
    cur = taskcon.cursor()
    cur.execute("SELECT * FROM `nodetasks` WHERE 1")
    for row in cur.fetchall():
        t = task(session, taskrow = row)
        tlist.append(t)
    taskcon.close()
    return tlist

# Wrapper for getting ACL for a user
def cataccess(session):
    aclcon = session.DB.sqlite.open('nodeacl.db')
    cur = aclcon.cursor()
    cur.execute("SELECT * FROM `nodeacl` WHERE `userid` = ? LIMIT 1", (session.user['userid'], ))
    acl = {}
    for row in cur.fetchall():
        acl[row['catid']] = ['none', 'read', 'write', 'admin'][row['access']]
    aclcon.close()
    return acl
