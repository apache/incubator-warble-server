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

"""
This is the ES/sqlite library for Apache Warble.
It stores the elasticsearch handler and config options.
"""


# Main imports
import os
import sqlite3

class WarbleESWrapper(object):
    """
       Class for rewriting old-style queries to the new ones,
       where doc_type is an integral part of the DB name
    """
    def __init__(self, ES):
        self.ES = ES

    def get(self, index, doc_type, id):
        return self.ES.get(index = index+'_'+doc_type, doc_type = '_doc', id = id)
    def exists(self, index, doc_type, id):
        return self.ES.exists(index = index+'_'+doc_type, doc_type = '_doc', id = id)
    def delete(self, index, doc_type, id):
        return self.ES.delete(index = index+'_'+doc_type, doc_type = '_doc', id = id)
    def index(self, index, doc_type, id, body):
        return self.ES.index(index = index+'_'+doc_type, doc_type = '_doc', id = id, body = body)
    def update(self, index, doc_type, id, body):
        return self.ES.update(index = index+'_'+doc_type, doc_type = '_doc', id = id, body = body)
    def search(self, index, doc_type, size = 100, _source_include = None, body = None):
        return self.ES.search(
            index = index+'_'+doc_type,
            doc_type = '_doc',
            size = size,
            _source_include = _source_include,
            body = body
            )
    def count(self, index, doc_type, body = None):
        return self.ES.count(
            index = index+'_'+doc_type,
            doc_type = '_doc',
            body = body
            )

class WarbleSqlite(object):
    
    def __init__(self, path):
        self.path = path
        
    def open(self, file):
        c = sqlite3.connect(os.path.join(self.path, file))
        c.row_factory = sqlite3.Row
        return c


class WarbleDatabase(object):
    def __init__(self, config):
        self.config = config
        
        # sqlite driver?
        if self.config['database']['driver'] == 'sqlite':
            self.dbtype = 'sqlite'
            self.sqlite = WarbleSqlite(self.config['database']['path'])
            
        # ES driver?
        if self.config['database']['driver'] == 'elasticsearch':
            import elasticsearch
            self.dbtype = 'elasticsearch'
            self.dbname = config['elasticsearch']['dbname']
            self.ES = elasticsearch.Elasticsearch([{
                    'host': config['elasticsearch']['host'],
                    'port': int(config['elasticsearch']['port']),
                    'use_ssl': config['elasticsearch']['ssl'],
                    'verify_certs': False,
                    'url_prefix': config['elasticsearch']['uri'] if 'uri' in config['elasticsearch'] else '',
                    'http_auth': config['elasticsearch']['auth'] if 'auth' in config['elasticsearch'] else None
                }],
                    max_retries=5,
                    retry_on_timeout=True
                )
    
            # IMPORTANT BIT: Figure out if this is ES 6.x or newer.
            # If so, we're using the new ES DB mappings, and need to adjust ALL
            # ES calls to match this.
            es6 = True if int(self.ES.info()['version']['number'].split('.')[0]) >= 6 else False
            if es6:
                self.ES = WarbleESWrapper(self.ES)
