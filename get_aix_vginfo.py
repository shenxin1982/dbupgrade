#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,re,json,logging


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_vginfo.log',
                filemode='w')

def Usage():
    print 'get_aix_vginfo usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-v,--vgname::<vgname,vgname1,vgname2...>'

def main(argv):
    hostname=""
    vgname=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:v:', ["help","hostname=","vgname="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=5):
        logging.error("The input paramters length is not correct!")
        Usage()
        sys.exit()
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif op in ('-o','--hostname'):
                hostname=ar
            elif op in ('-v','--vgname'):
                vgname=ar
            else:
                logging.error("Error: invalid parameters")
                Usage()
                sys.exit()



def get_aix_vginfo(vgname):
    actvgdata = subprocess.Popen('lsvg -o',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    if vgname=='rootvg':
        mircmd = 'lsvg -l rootvg |grep \"/\"|awk \'{print $5}\'|uniq'
        mirdata = subprocess.Popen(mircmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
        data1 = int(mirdata)
        if data1 == 1:
            rootvgmir ={'rootvgmir':'No'}
        else:
            rootvgmir ={'rootvgmir':'Yes'}
        vgcmd = 'lsvg '+ vgname
        vgdata = subprocess.Popen(vgcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('megabytes)','MB').replace('(','')
        vglist = vgdata.split()
        vgdict = {'rootvgstat':vglist[8],'rootvgsize':vglist[19]}
        vgdict1 = {}
        vgdict1[vgname] = dict(rootvgmir.items()+vgdict.items())
        return vgdict1
    elif actvgdata.find(vgname)!= -1 :
        vgdict={}
        vgcmd = 'lsvg '+ vgname
        vgdata = subprocess.Popen(vgcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('megabytes)','MB').replace('(','')
        vglist = vgdata.split()
        vgdict[vgname] = {'vgstat':vglist[8],'vgsize':vglist[19]}
        return vgdict
    else:
        logging.error("The vgname is not in the active vg list")
        retcode=-1
        return retcode



if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    vgname = sys.argv[4]
    vgname1=vgname.split(',')
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        getvglist=[]
        for line in vgname1:
            p1 = get_aix_vginfo(line)
            print p1
