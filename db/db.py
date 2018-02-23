#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 zhou <zhou@Macbook>
#
# Distributed under terms of the MIT license.

"""
Database wrapper for main program.
"""

import sqlite3
import os
import pickle


class FFDB:
    def __init__(self, dbfn):
        self.dbfn = dbfn
        self.get_conn_cursor()     # self.conn and self.cursor
        self.schema = """CREATE TABLE IF NOT EXISTS FFUSER
            (ID     TEXT PRIMARY KEY NOT NULL,
             URLID  TEXT            NOT NULL,
             NAME   TEXT            NOT NULL,
             GENDER CHAR(5),
             LOC    TEXT,
             BIO    TEXT            NOT NULL,
             BORNT  TEXT,
             LKSTAT BOOLEAN         NOT NULL,
             FOLCNT INTEGER         NOT NULL,
             FRICNT INTEGER         NOT NULL,
             REGT   TEXT            NOT NULL,
             MSGCNT INTEGER         NOT NULL
             );"""
        self.create_table()
    
    def get_conn_cursor(self):
        #assert(os.path.exists(self.dbfn)), "DB FILE {} nonexists...".format(self.dbfn)
        conn = sqlite3.connect(self.dbfn)
        print ("Open database successfully...")
        self.conn = conn
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute(self.schema)
        print ("Table created or exists...")

    def checkexist(self, urlid):
        print ("CHECKING SELECT EXISTS(SELECT 1 FROM FFUSER WHERE URLID==\"{}\");".format(urlid))
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM FFUSER WHERE URLID==\"{}\");".format(urlid))
        return bool(self.cursor.__next__()[0])

    def checkuniqexist(self, uniqid):
        #print ("CHECKING SELECT EXISTS(SELECT 1 FROM FFUSER WHERE ID==\"{}\");".format(uniqid))
        self.cursor.execute("SELECT EXISTS(SELECT 1 FROM FFUSER WHERE ID==\"{}\");".format(uniqid))
        return bool(self.cursor.__next__()[0])

    def insert(self, data):
        if self.checkuniqexist(data['id']) is False:
            self.cursor.execute("INSERT INTO FFUSER (ID, URLID, NAME, GENDER, LOC, BIO, BORNT, LKSTAT, FOLCNT, FRICNT, REGT, MSGCNT) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", ( \
                data['id'], data['urlid'], data['name'], data['gender'], data['loc'], data['bio'], data['bornt'], \
                data['lkstat'], data['folcnt'], data['fricnt'], data['regt'], data['msgcnt']))
        else:
            print ("UNIQUE ID {} exists...".format(data['id']))

    def delete(self):
        pass

    def retrieve(self, bound):
        return self.cursor.fetchall()

    def retrieve_allids(self):
        self.cursor.execute("SELECT URLID from FFUSER")
        all_tuple_ids = self.cursor.fetchall()
        all_ids = set()
        for i in all_tuple_ids:
            all_ids.add(i[0])
        return all_ids


    def update(self):
        pass
    
    def close(self):
        conn = self.conn
        conn.commit()
        conn.close()

    def commit(self):
        self.conn.commit()

class AssistDB:
    def __init__(self, userdbfn, seeddbfn):
        self.userdbfn = userdbfn
        self.seeddbfn = seeddbfn
        self.load()

    def load(self):
        if os.path.exists(self.userdbfn) and os.path.exists(self.seeddbfn):
            with open(self.userdbfn, "rb") as f:
                self.userdb = pickle.load(f)
            with open(self.seeddbfn, "rb") as f:
                self.seeddb = pickle.load(f)
        else:
            self.userdb = set()
            self.seeddb = set()

    def dump_userset(self, userset):
        with open(self.userdbfn, "wb") as f:
            pickle.dump(userset, f)

    def dump_seedset(self, seedset):
        with open(self.seeddbfn, "wb") as f:
            pickle.dump(seedset, f)

if __name__ == "__main__":
    ffdb = FFDB("../db.sqlite3")

    #print (ffdb.checkuniqexist("~llqo7Ohpu6o"))
    allids = ffdb.retrieve_allids()

    print (allids)
    



