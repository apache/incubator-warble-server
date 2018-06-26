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
# OPENAPI-URI: /api/node/register
########################################################################
# post:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/NodeCredentials'
#     description: Node credentials
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/APIKeyResult'
#       description: Node successfully registered with server
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Registers a new node with the Warble server
# 
########################################################################





"""
This is the node registration handler for Apache Warble
"""

import json
import re
import time
import plugins.crypto
import plugins.registry
import base64

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Registering a new node?
    if method == "POST":
        hostname = indata['hostname']
        pubkey_pem = indata['pubkey']
        nodeversion = indata['version'] # TODO: Check for incompatibilities!
        
        # Try loading the PEM
        try:
            pubkey = plugins.crypto.loads(pubkey_pem)
        except:
            raise API.exception(400, "Bad PEM payload passed from client!")
        
        # Okay, we have what we need for now. Register potential node and gen an API key
        node = plugins.registry.node(session)
        node.hostname = hostname
        node.pem = pubkey_pem
        node.version = nodeversion
        node.ip = environ.get('HTTP_X_FORWARDED_FOR', environ.get('REMOTE_ADDR', '0.0.0.0'))
        
        # Encrypt API key with the pub key we just got. base64 encode the result
        apikey_crypt = str(base64.b64encode(plugins.crypto.encrypt(pubkey, node.apikey)), 'ascii')
        node.save()
        
        yield json.dumps({"encrypted": True, "key": apikey_crypt}, indent = 2)
        return

    
    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
