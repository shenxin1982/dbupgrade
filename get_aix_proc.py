#!/usr/bin/python
# encoding: utf-8
# -*- coding: utf8 -*
import os
import subprocess
import sys
import getopt
import socket
import json

def Usage():
    print 'check_aix_proc.py usage:   '
    print 'use to check whether the process is exists  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'

def main(argv):
    hostname=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:', ["help","hostname="])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=3):
        Usage()
        sys.exit()
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif op in ('-o','--hostname'):
                hostname=ar
            else:
                print 'Error: invalid parameters'
                Usage()
                sys.exit()


def transtoarray(data):
    info=[]
    for i in data.split('\n\n'):
        for x in i.splitlines():
            if x:
                info.append(x)
    return info 

def get_aix_crontab():
    cmd = 'cat /var/spool/cron/crontabs/*|grep -v \"^#\"'
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    crondict = {'crontab':data}
    return crondict


def get_aix_proc(proname):
    processcmd="ps -ef|grep -i " + proname + "|grep -v grep >/dev/null"
    processCK=os.system(processcmd)
    if processCK == 0:
        result = proname + ": yes";
    else:
        result = proname + ": no";
    return result

def check_aix_proc():
    procinfo = {}
    ckops = get_aix_proc('opsware')
    ckitm = get_aix_proc('itm')
    cknim = get_aix_proc('nim')
    cknbu = get_aix_proc('nbu')
    ckdb2m = get_aix_proc('db2_mon')
    cktivo = get_aix_proc('tivoli')
    ckkanb = get_aix_proc('kanban')
    ckcdcr = get_aix_proc('cdc_run')
    data = ckops,ckitm,cknim,cknbu,ckdb2m,cktivo,ckkanb,ckcdcr
    info = list(data)
    for i in info:
        k, v = [x.strip() for x in i.split(':')]
        procinfo[k] = v
    return procinfo

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        p1=check_aix_proc()
        p2=get_aix_crontab()
        pdata = dict(p1.items()+p2.items())
        print json.dumps(pdata)

