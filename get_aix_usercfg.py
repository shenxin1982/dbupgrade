#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess
import sys
import getopt
import socket
import json

def Usage():
    print 'get_aix_usercfg usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-u,--username::<username,username2,...>'

def main(argv):
    hostname=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:u:', ["help","hostname=","username="])
    except getopt.GetoptError, err:
        print str(err)
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=5):
        Usage()
        sys.exit()
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif op in ('-o','--hostname'):
                hostname=ar
            elif op in ('-u','--username'):
                username=ar
            else:
                print 'Error: invalid parameters'
                Usage()
                sys.exit()

def sub_dict(form_dict, sub_keys, default=None):
    return dict([(k, form_dict.get(k.strip(), default)) for k in sub_keys.split(',')])

def transtoarray(data):
    info=[]
    for i in data.split('\n\n'):
        for x in i.splitlines():
            if x:
                info.append(x)
    return info 


def get_aix_usercfg(username):
    user_cfg={}
    cmd='lsuser -f '+username+'|grep -v '+username+":"
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
    data1 = 'uname='+username+'\n'+data
    info = transtoarray(data1)
    for i in info: 
        k, v = [x.strip() for x in i.split('=')]
        user_cfg[k] = v
    userinfo=sub_dict(user_cfg,'uname,id,pgrp,groups,home,shell,expires,fsize,cpu,data,stack,rss,nofiles,fsize_hard,cpu_hard,data_hard,stack_hard,rss_hard,nofiles_hard,capabilities')
    grpname = user_cfg.get('pgrp')
    cmd = 'lsgroup -f ' + grpname +'|grep -v '+grpname+":"
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0].replace('id','groupid')
    info = transtoarray(data)
    grp_cfg={}
    for i in info:
        k, v = [x.strip() for x in i.split('=')]
        grp_cfg[k] = v
    grpinfo=sub_dict(grp_cfg,'groupid')
    
    return dict(userinfo.items()+grpinfo.items())

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    username=sys.argv[4]
    username1 = username.split(',')
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        userlist=[]
        for line in username1:
            userdict={}
            p1=get_aix_usercfg(line)
            userdict[line]=p1
            userlist.append(userdict)
        print json.dumps(userlist)
