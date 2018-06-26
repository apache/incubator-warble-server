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
# OPENAPI-URI: /api/node/status
########################################################################
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/NodeDetails'
#       description: Node status
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Displays the current status of a node
# 
########################################################################





"""
This is the node status handler for Apache Warble
"""

import json
import plugins.crypto
import plugins.registry

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Modifying a node?
    if method == "GET":
        if session.client: 
            yield json.dumps({
                'id': session.client.id,
                'enabled': session.client.enabled,
                'verified': session.client.verified
                }, indent = 2)
            return
        else:
            raise API.exception(404, "Unknown API Key passed by client")

    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
