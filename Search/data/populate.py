#!/usr/bin/env python
from __future__ import print_function
import locale
import multiprocessing
import os
import random
import sys
import signal
import time
import uuid
import gzip
import traceback
from itertools import chain
from datetime import date, timedelta, datetime
import Queue

from cassandra.io.libevreactor import LibevConnection
from cassandra.cluster import Cluster

KEYSPACE = "amazon3"
META_COLUMN_FAMILY = "metadata"
RANK_COLUMN_FAMILY = "rank"

"""
{'asin': '0007148089',
 'title': "Blood and Roses: One Family's Struggle and Triumph During the Tumultuous Wars of the Roses",
 'price': 5.98,
 'imUrl': 'http://ecx.images-amazon.com/images/I/518p8d64F8L.jpg',
 'related': {
      'also_bought': ['0061430765', '0061430773', 'B00A4E8E78'],
      'buy_after_viewing': ['0061430773', '0345404335', 'B00A4E8E78', '0975126407']
 },
 'salesRank': {'Books': 326205},
 'categories': [['Books']]
}
"""

KS_CREATION_STATEMENT = """
CREATE KEYSPACE IF NOT EXISTS %s WITH replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
"""  % (KEYSPACE)

META_CF_CREATION_STATEMENT = """
CREATE TABLE IF NOT EXISTS %s.%s (
    asin text,
    title text,
    imurl text,
    price double,
    categories set<text>,
    also_bought set<text>,
    buy_after_viewing set<text>,
    PRIMARY KEY(asin));
"""  % (KEYSPACE, META_COLUMN_FAMILY)

META_CF_DROP_STATEMENT = """DROP TABLE IF EXISTS %s.%s;"""  % (KEYSPACE, META_COLUMN_FAMILY)

RANK_CF_CREATION_STATEMENT = """
CREATE TABLE IF NOT EXISTS %s.%s (
    asin text,
    category text,
    rank int,
    PRIMARY KEY(asin, category));
"""  % (KEYSPACE, RANK_COLUMN_FAMILY)

RANK_CF_DROP_STATEMENT = """DROP TABLE IF EXISTS %s.%s;"""  % (KEYSPACE, RANK_COLUMN_FAMILY)

META_INSERT_STATEMENT = "INSERT INTO %s.%s(asin, title, imurl, price, categories, also_bought, buy_after_viewing) VALUES(?, ?, ?, ?, ?, ?, ?)" \
                        % (KEYSPACE, META_COLUMN_FAMILY)

RANK_INSERT_STATEMENT = "INSERT INTO %s.%s(asin, category, rank) VALUES(?, ?, ?)" \
                        % (KEYSPACE, RANK_COLUMN_FAMILY)

"""
{!join fromIndex=amazon.rank}rank:1605773
http://localhost:8983/solr/amazon.metadata/select?q=*%3A*&fq=%7B!join+fromIndex%3Damazon.rank%7Drank%3A1605773&wt=json&indent=true&echoParams=all

SELECT * FROM amazon.metadata WHERE solr_query='{"q":"{!join fromIndex=amazon.rank}rank:1605773"}';
"""

"""
CREATE KEYSPACE IF NOT EXISTS amazon WITH replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

CREATE TABLE IF NOT EXISTS amazon.metadata (
    asin text,
    title text,
    imurl text,
    price double,
    categories set<text>,
    also_bought set<text>,
    buy_after_viewing set<text>,
    PRIMARY KEY(asin));


CREATE TABLE IF NOT EXISTS amazon.rank (
    asin text,
    category text,
    rank int,
    PRIMARY KEY(asin, category));


~/dse/bin/dsetool create_core amazon.metadata generateResources=true

~/dse/bin/dsetool create_core amazon.rank generateResources=true


CREATE TYPE amazon.category_rank (
      category text,
      rank int
  );

ALTER TABLE amazon.metadata ADD ranks set<frozen<category_rank>>;


UPDATE amazon.metadata SET ranks = ranks + { { category:'Movies', rank:1 } } WHERE asin='0007321198';

SELECT * FROM amazon.metadata WHERE asin='0007321198';

SELECT * FROM amazon.metadata WHERE solr_query='asin:0007321198';

SELECT * FROM amazon.metadata WHERE solr_query='asin:000732119~';

SELECT * FROM amazon.metadata WHERE solr_query='{"q":"asin:0007321198", "route.partition" :["0007321198"]}';

SELECT * FROM amazon.metadata WHERE solr_query='{"q":"*:*", "facet":{"field":"also_bought"}}';

SELECT * FROM amazon.metadata WHERE solr_query='{"q":"*:*", "facet":{"field":"also_bought"}, "query.name":"test"}';

SELECT * FROM amazon.metadata WHERE solr_query='{"q":"*:*", "facet":{"facet.pivot":["name","surname"]}}';

SELECT asin FROM amazon.rank WHERE solr_query='{"q":"asin:0007321198"}';
SELECT asin FROM amazon.rank WHERE solr_query='{"q":"asin:0007321198", "distrib.singlePass":true}';



"""

def parse(path):
    g = open(path, 'r')
    for l in g:
        yield eval(l)

if __name__ == '__main__':
    f = open('config.txt', 'r')
    contact_points = f.readline()
    meta_path = sys.argv[1]
    geo_path = sys.argv[2]
    input_path = sys.argv[1]
    cluster = Cluster([contact_points])
    cluster.connection_class = LibevConnection
    session = cluster.connect()
    # session.execute(META_CF_DROP_STATEMENT)
    # session.execute(RANK_CF_DROP_STATEMENT)
    session.execute(KS_CREATION_STATEMENT)
    session.execute(META_CF_CREATION_STATEMENT)
    session.execute(RANK_CF_CREATION_STATEMENT)

    meta_prepared = session.prepare(META_INSERT_STATEMENT)
    rank_prepared = session.prepare(RANK_INSERT_STATEMENT)

    for data in parse(input_path):
        asin = data['asin']
        title = data.get('title', "")
        imurl = data.get('imUrl', "")
        price = data.get('price', 0.0)
        categories = list(chain.from_iterable(data.get('categories', [])))
        related = data.get('related', {})
        also_bought = related.get('also_bought', [])
        buy_after_viewing = related.get('buy_after_viewing', [])
        meta_bound = meta_prepared.bind([asin, title, imurl, price, categories, also_bought, buy_after_viewing])
        session.execute(meta_bound)

        for (category, rank) in data.get('salesRank', {}).items():
            rank_bound = rank_prepared.bind([asin, category, rank])
            session.execute(rank_bound)
