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
# OPENAPI-URI: /api/session
########################################################################
# delete:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/Empty'
#     description: Nada
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/ActionCompleted'
#       description: Logout successful
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Log out (remove session)
# get:
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/UserData'
#       description: 200 response
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   security:
#   - cookieAuth: []
#   summary: Display your login details
# put:
#   requestBody:
#     content:
#       application/json:
#         schema:
#           $ref: '#/components/schemas/UserCredentials'
#     description: User credentials
#     required: true
#   responses:
#     '200':
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/ActionCompleted'
#       description: Login successful
#       headers:
#         Set-Cookie:
#           schema:
#             example: 77488a26-23c2-4e29-94a1-6a0738f6a3ff
#             type: string
#     default:
#       content:
#         application/json:
#           schema:
#             $ref: '#/components/schemas/Error'
#       description: unexpected error
#   summary: Log in
# 
########################################################################





"""
This is the user session handler for Warble
"""

import json
import re
import time
import bcrypt
import hashlib

def run(API, environ, indata, session):
    
    method = environ['REQUEST_METHOD']
    
    # Logging in?
    if method == "PUT":
        u = indata['username']
        p = indata['password']
        if session.DB.dbtype == 'sqlite':
            session_conn = session.DB.sqlite.open('sessions.db')
            account_conn = session.DB.sqlite.open('accounts.db')
            sc = session_conn.cursor()
            ac = account_conn.cursor()
            ac.execute("SELECT * FROM `accounts` WHERE `userid` = ? LIMIT 1", (u,))
            sdoc = ac.fetchone()
            if sdoc:
                mypass = sdoc['password']
                theirpass = bcrypt.hashpw(p.encode('utf-8'), mypass.encode('utf-8')).decode('ascii')
                if mypass == theirpass:
                    sc.execute("INSERT INTO `sessions` (`userid`, `cookie`, `timestamp`) VALUES (?, ?, ?)",
                               (u, session.cookie, int(time.time())))
                    session_conn.commit()
                    session_conn.close()
                    account_conn.close()
                    yield json.dumps({"message": "Logged in OK!"}, indent = 2)
                    return
            # Fall back to a 403 if username and password did not match
            raise API.exception(403, "Wrong username or password supplied!")
        
        elif session.DB.dbtype == 'elasticsearch':
            if session.DB.ES.exists(index=session.DB.dbname, doc_type='useraccount', id = u):
                doc = session.DB.ES.get(index=session.DB.dbname, doc_type='useraccount', id = u)
                hp = doc['_source']['password']
                if bcrypt.hashpw(p.encode('utf-8'), hp.encode('utf-8')).decode('ascii') == hp:
                    # If verification is enabled, make sure account is verified
                    if session.config['accounts'].get('verify'):
                        if doc['_source']['verified'] == False:
                            raise API.exception(403, "Your account needs to be verified first. Check your inbox!")
                    sessionDoc = {
                        'cid': u,
                        'id': session.cookie,
                        'timestamp': int(time.time())
                    }
                    session.DB.ES.index(index=session.DB.dbname, doc_type='uisession', id = session.cookie, body = sessionDoc)
                    yield json.dumps({"message": "Logged in OK!"})
                    return
            
            # Fall back to a 403 if username and password did not match
            raise API.exception(403, "Wrong username or password supplied!")
    
    
    # We need to be logged in for the rest of this!
    if not session.user:
        raise API.exception(403, "You must be logged in to use this API endpoint!")
    
    # Delete a session (log out)
    if method == "DELETE":
        if session.DB.dbtype == 'sqlite':
            c = session.DB.sqlite.open('sessions.db')
            cur = c.cursor()
            cur.execute("DELETE FROM `sessions` WHERE `cookie` = ? LIMIT 1", (session.cookie,))
            c.commit()
            c.close()
        elif session.DB.dbtype == 'elasticsearch':
            session.DB.ES.delete(index=session.DB.dbname, doc_type='uisession', id = session.cookie)
        session.newCookie()
        yield json.dumps({"message": "Logged out, bye bye!"})
    
    # Display the user data for this session
    if method == "GET":
        
        JSON_OUT = {
            'userid': session.user['userid'],
            'userlevel': session.user['userlevel']
        }
        yield json.dumps(JSON_OUT, indent = 2)
        return
    
    # Finally, if we hit a method we don't know, balk!
    yield API.exception(400, "I don't know this request method!!")
    
