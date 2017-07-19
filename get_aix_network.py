#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import commands
import subprocess
import sys
import getopt
import socket
import re
import json

def Usage():
    print 'get_aix_network usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'

def main(argv):
    hostname=""
    instname=""
    dbname=""

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



def get_aix_network():
    adaptercmd = 'ifconfig -l'
    ifnetdata = subprocess.Popen(adaptercmd, stdout=subprocess.PIPE, shell=True)
#    ifnetname = ifnetdata.communicate()[0].replace(' ','\n').split('\n')
    (status, output) = commands.getstatusoutput(adaptercmd)
    ifnetname = output.replace(' ','\n').split('\n')
    ipinfo=[]
    tcpsinfo=[]
    tcprinfo=[]
    rfcinfo=[]
    ifnetinfo={}

    for line in ifnetname: 
        if line and not line.startswith('lo'):
            cmd = 'ifconfig ' + line
            tmpdata = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0].replace('\n','').replace('\t','').split(' ')
            adname = line.strip()
            ipinfo.append(tmpdata[2])
            tcpsinfo.append(tmpdata[8])
            tcprinfo.append(tmpdata[10])
            rfcinfo.append(tmpdata[12])
    ifnetinfo={'ipaddr':ipinfo,'tcp_sendspace':tcpsinfo,'tcp_recvspace':tcprinfo,'rfc1323':rfcinfo}
    return ifnetinfo


if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        p1=get_aix_network()
        print json.dumps(p1)
