#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 zhou <zhou@Macbook>
#
# Distributed under terms of the MIT license.

"""
Main script.
"""

import fanfou
from config import AUTH, DBFN, SEED, COMMIT_INTER, LOGFN
import json, pickle, os, datetime
import itertools
import time
import setproctitle

from db.db import FFDB, AssistDB
from logger.logger import setup_logger


def delay(t=0):
    if not t:
        time.sleep(round(1 / (1000/60/60)))
    else:
        time.sleep(round(t))


logger = setup_logger(logfile=LOGFN)

""" FF's fetcher, it can pull ff's data into python types var official API """
class Fetcher:
    def __init__(self):
        self.get_auth()
        self.client = self.get_client()

    def restart(self):
        self.__init__()
    
    def get_auth(self):
        self.consumer_key = AUTH['consumer_key']
        self.consumer_sec = AUTH['consumer_sec']
        self.username = AUTH['username']
        self.password = AUTH['password']
        self.consumer = {'key':  self.consumer_key, 'secret': self.consumer_sec}

    def get_client(self):
        client = fanfou.XAuth(self.consumer, self.username, self.password, fake_https=True)
        return client

    def resphandler(self, resp):
        if type(resp) == type(''):
            return json.loads(resp)
        else:
            return json.loads(resp.read().decode('utf8'))

    def get_followersid(self, user_id=None):
        if user_id == None:
            ids = self.client.request("/followers/ids", 'GET')
        else:
            ids = self.client.request("/followers/ids", 'GET', {"id": user_id})
        return self.resphandler(ids)

    def get_friendsid(self, user_id=None):
        if user_id == None:
            ids = self.client.request("/friends/ids", 'GET')
        else:
            ids = self.client.request("/friends/ids", 'GET', {"id": user_id})
        return self.resphandler(ids)

    """ Core member function, https://github.com/FanfouAPI/FanFouAPIDoc/wiki/followers.ids """
    def get_allfids(self, user_id=None):
        allids = set()
        folids = set(self.get_followersid(user_id))
        friids = set(self.get_friendsid(user_id))
        allids.update(folids)
        allids.update(friids)
        return allids

    """ Core member function, https://github.com/FanfouAPI/FanFouAPIDoc/wiki/users.show """
    def get_usershow(self, user_id=None):
        if user_id == None:
            userinfo = self.client.request("/users/show", 'GET')
        else:
            userinfo = self.client.request("/users/show", 'GET', {"id": user_id})
        userjson = self.resphandler(userinfo)
        return userjson

    """ Test member function for XAuth """
    def update(self, body):
        self.client.request("/statuses/update", 'POST', body)


""" A wide first searcher, it will handle only one node by `search` """
class WFSer:
    def __init__(self):
        self.setdb = AssistDB(DBFN['usersetdb'], DBFN['seedsetdb'])
        self.ffdb = FFDB(DBFN['ffdb'])
        self.seedset = self.setdb.seeddb
        self.userset = self.setdb.userdb
        self.fetcher = Fetcher()

    def search(self, seed):
        curr_seed_allids = self.fetcher.get_allfids(seed)
        curr_seed_allids.add(seed)
        curr_search_allids = curr_seed_allids - self.userset
        print ("seed is {}".format(seed))
        print ("curr_search_allids is {}".format(curr_search_allids))
        for i, i_id in enumerate(curr_search_allids):
            #print (i_id)
            usershow = self.fetcher.get_usershow(i_id)
            if usershow != ['']:
                self.dbinsert(i_id, usershow)
            else:
                assert(False), 'Error in fetching...'
            logger.info ("{} fetched...".format(i_id))
            self.userset.add(i_id)
            if i % COMMIT_INTER == 0 and i != 0:
                self.dbcommit()
            delay()
        self.seedset.add(seed)
        self.dbcommit()
        curr_search_seeds = curr_seed_allids - self.seedset
        return curr_search_seeds

    def dbexist(self, id_):
        return self.ffdb.checkexist(id_)

    def dbinsert(self, urlid, usershow):
        data = dict()
        if usershow == ['']:
            delay(60)
        data['urlid'] = urlid
        dbmap = {'unique_id': "id", 'name': "name", 'gender': "gender", 'location': "loc",
                 'statuses_count': "msgcnt", 'description': "bio", 'birthday': "bornt",
                 'protected': "lkstat", 'followers_count': "folcnt", 'friends_count': "fricnt",
                 'created_at': "regt"}
        for imap in dbmap:
            data[dbmap[imap]] = usershow[imap]
        #print (data)
        self.ffdb.insert(data)
    
    def dbclose(self):
        self.setdb.dump_userset(self.userset)
        self.setdb.dump_seedset(self.seedset)
        self.ffdb.close()

    def dbcommit(self):
        self.setdb.dump_userset(self.userset)
        self.setdb.dump_seedset(self.seedset)
        self.ffdb.commit()
        logger.info("SQLite3 DB committed...")


def main():
    setproctitle.setproctitle('FFANALYSIS')
    spider = WFSer()
    #SEED = "~dAaA02aMxXs"
    curr_search_seeds = spider.search(SEED)
    last_len = 0
    count = 0

    while count < 10:
        idpool = set()
        #print (curr_search_seeds)
        for i_sid in curr_search_seeds:
            idpool.update(spider.search(i_sid))
        idpool =  idpool - curr_search_seeds
        curr_search_seeds = idpool
        curr_len = len(spider.userset)
        if last_len == curr_len:
            count += 1
        last_len = curr_len
        logger.info ("Now in userset reaches {}, seedset reaches {}...".format(len(spider.userset), len(spider.seedset)))
        logger.info ("Now seedpool reaches {}".format(idpool))


if __name__ == "__main__":
    main()









