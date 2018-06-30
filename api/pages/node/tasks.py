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
# OPENAPI-URI: /api/node/tasks
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/TaskList'
#       description: Node task list
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Returns a list of tasks assigned to a given node
# 
########################################################################





"""
This is the node task list handler for Apache Warble
"""

import json
import plugins.crypto
import plugins.registry
import plugins.tasks
import base64
import time

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Fetch list of tasks to perform
    if method == "GET":
        
        # Fetching tasks for a node?
        if session.client:
            if not session.client.verified:
                raise API.exception(403, "This client node has not been verified on master yet.")
            if not session.client.enabled:
                raise API.exception(444, "This client node has been disabled, no tasks will be sent.")
            # Get all tasks that are enabled
            tasks = plugins.tasks.all(session)
            tasklist = []
            for task in tasks:
                if task.enabled:
                    # Don't show tests that are not assigned to this node
                    if 'nodes' in task.payload and session.client.id not in task.payload['nodes']:
                        continue
                    tasklist.append({
                        'id': task.id,
                        'name': task.name,
                        'payload': task.payload
                    })
            # Register that the node contacted us - that counts as being alive
            session.client.lastping = int(time.time())
            session.client.save()
            
            # This is the fun part! Because $design, we have to encrypt using the client's public key!
            # This way, only the _true_ client can decrypt it, and no snooping.
            plain = json.dumps({
                'tasks': tasklist
                }, indent = 2)
            crypted = plugins.crypto.encrypt(session.client.key, plain)
            cryptbase = base64.b64encode(crypted)
            yield cryptbase
            return
        
        # Or are we fetching tasks for a user?
        elif session.user:
            tasks = plugins.tasks.all(session)
            acl = plugins.tasks.cataccess(session)
            tasklist = []
            for task in tasks:
                # Only show task if super user or ACL allows access
                canwrite = True if session.user['userlevel'] == 'superuser' or (task.category in acl and acl[task.id] > 1) else False
                canread = True if task.category in acl or session.user['userlevel'] == 'superuser' else False
                if canread:
                    tasklist.append({
                        'id': task.id,
                        'category': task.category,
                        'enabled': task.enabled,
                        'muted': task.muted,
                        'name': task.name,
                        'payload': task.payload if canwrite else None
                    })
                        
            yield json.dumps({
                'tasks': tasklist
                }, indent = 2)
            return
        else:
            raise API.exception(499, "Unknown API Key passed by client")

    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
