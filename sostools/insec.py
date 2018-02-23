#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 zhou <zhou@Macbook>
#
# Distributed under terms of the MIT license.

"""

"""
import pickle

with open('usersetdb.pickle', "rb") as f:
    pickle_set = pickle.load(f)

from db.db import FFDB

dbobj = FFDB("db.sqlite3")
db_set = dbobj.retrieve_allids()

pickle_notin_db = pickle_set - db_set
pickle_real_set = pickle_set - pickle_notin_db
print (len(pickle_notin_db))
#with open('usersetdb.pickle', "wb") as f:
#    pickle.dump(pickle_real_set, f)


