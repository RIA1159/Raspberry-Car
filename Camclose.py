#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from time import sleep
import time
def Close():
    f=os.popen("ps -ef | grep python")
    txt=f.readlines()
    for line in txt:
        colum=line.split()
        pid=colum[1]
        name=colum[-1]
        if name=='Main.py':
            cmd = "sudo kill -9 %d" % int(pid)
            os.system(cmd)
if __name__ == '__main__':
    Close()
    sleep(10)
    print('hello')