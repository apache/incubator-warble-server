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
# OPENAPI-URI: /api/node/list
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/NodeList'
#       description: List of nodes in registry
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Lists the nodes in the registry
# 
########################################################################





"""
This is the node modification handler for Apache Warble
"""

import json
import re
import time
import plugins.crypto
import plugins.registry
import base64

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Modifying a node?
    if method == "GET":
        # Super users only!
        if not session.user or session.user['userlevel'] != 'superuser':
            raise API.exception(403, "You need to be logged in as super user to perform this action")
        
        conn = session.DB.sqlite.open('nodes.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM `registry` WHERE 1")
        
        nodes = []
        for node in cursor.fetchall():
            xnode = {k:node[k] for k in node.keys()}
            xnode['verified'] = True if node['verified'] else False
            xnode['enabled'] = True if node['enabled'] else False
            xnode['fingerprint'] = plugins.crypto.fingerprint(node['pubkey'])
            nodes.append(xnode)
        
        
        yield json.dumps({"nodes": nodes}, indent = 2)
        return

    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
