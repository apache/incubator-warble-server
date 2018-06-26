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
# OPENAPI-URI: /api/node/modify
########################################################################
# post:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/NodeDetails'
#     description: Node details to modify
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/ActionCompleted'
#       description: Node successfully modified on server
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Modifies base data of a node in the registry
# delete:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/NodeDetails'
#     description: Node to remove
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/ActionCompleted'
#       description: Node successfully removed from registry
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Deletes a registered node from the server
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
    if method == "POST":
        # Super users only!
        if not session.user or session.user['userlevel'] != 'superuser':
            raise API.exception(403, "You need to be logged in as super user to perform this action")
        
        
        # Try finding the node in the registry
        nodeid = indata['id']
        node = None
        try:
            node = plugins.registry.node(session, nodeid)
        except:
            raise API.exception(404, "Could not find a node by this ID to modify.")
        
        # Save any changes we get
        if 'verified' in indata:
            node.verified = indata['verified']
        if 'enabled' in indata:
            node.enabled = indata['enabled']
        if 'hostname' in indata and indata['hostname']:
            node.hostname = indata['hostname']
        if 'pubkey' in indata and indata['pubkey']:
            # Verify that PEM works:
            try:
                plugins.crypto.loads(indata['pubkey'])
            except:
                raise API.exception(400, "Could not save changes: Bad PEM payload passed!")
            node.pubkey = indata['pubkey']
        if 'description' in indata and indata['description']:
            node.description = indata['description']
        if 'location' in indata and indata['location']:
            node.location = indata['location']
        
        # All done, save node and exit
        node.save()
        del node # just to be sure
        
        yield json.dumps({"okay": True, "message": "Changes saved"}, indent = 2)
        return
    
    # Deleting a node?
    if method == "DELETE":
        # Super users only!
        if not session.user or session.user['userlevel'] != 'superuser':
            raise API.exception(403, "You need to be logged in as super user to perform this action")
        
        # Try finding the node in the registry
        nodeid = indata['id']
        node = None
        try:
            node = plugins.registry.node(session, nodeid)
        except:
            raise API.exception(404, "Could not find a node by this ID to modify.")
        
        # Remove node, say cheese!
        node.remove()
        yield json.dumps({"okay": True, "message": "Node removed from registry"}, indent = 2)
        return
        
    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
