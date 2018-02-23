#! /bin/sh
#
# restart.sh
# Copyright (C) 2018 zhou <zhou@Macbook>
#
# Distributed under terms of the MIT license.
#

FFPID=`ps aux | grep 'FFANALYSIS' | grep -v 'grep' | awk -F" " '{print $2}'`
kill $FFPID
python3 fetcher.py


