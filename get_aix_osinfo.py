#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,time,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_osinfo.log',
                filemode='w')
def Usage():
    print 'get_aix_osinfo usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-p,--port::<port>'

def main(argv):
    hostname=""
    instname=""
    port=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:p:', ["help","hostname=","instname=","port="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit()
    if(len(sys.argv)!=7):
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
            elif op in ('-i','--instname'):
                instname=ar
            elif op in ('-p','--port'):
                port=ar
            else:
                logging.error("Error: invalid parameters")
                Usage()
                sys.exit()


def transtoarray(data):
    info=[]
    for i in data.split('\n\n'):
        for x in i.splitlines():
            if x:
                info.append(x)
    return info 

def get_aix_osinfo():
    logging.info("Begin to get osinfo:")
    osinfo={}
    oslevel = subprocess.Popen('oslevel -s',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if oslevel[0] not in ('7','6'):
        oslevel = 'Error'
        logging.info("oslevel is not in 7.1 or 6.1")
    else:
        oslevel = oslevel
    memsize = subprocess.Popen('lsattr -El mem0 -a goodsize -F value',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    numproc = subprocess.Popen('lsdev -Sa -Cc processor|awk \'END{print NR}\'',stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()[0]
    clevel = subprocess.Popen('lslpp -l|grep -i xlc.rte',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].split()
    jdklevel= subprocess.Popen('java -version',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[1]
    timezone = subprocess.Popen('echo $TZ',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    nowtime = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    pgspace = subprocess.Popen('lsps -as|grep -i MB',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('MB','').split()
    osinfo = {'oslevel':oslevel[0:10].strip(),'memsize':memsize.strip(),'numproc':numproc.strip(),'clevel':clevel[1],'timezone':timezone.strip(),'nowtime':nowtime.strip(),'pgspace':pgspace[0],'jdklevel':jdklevel.replace('"','').split()[2]}
    logging.info("osinfo is collected complete!")
    return osinfo


def get_aix_hostsinfo():
    logging.info("Begin to get hostsinfo:")
    hostsinfo={}
    hostscfg={}
    data = subprocess.Popen('cat /etc/hosts|grep -v \"#\"|grep -i "^[0-9]"|awk \'{print $1,\":\",$2,$3,$4}\'',stdout=subprocess.PIPE, shell=True).communicate()[0]
    info = transtoarray(data)
    for i in info:
        if i:
            k, v = [x.strip() for x in i.split(':')]
            hostsinfo[k] = v
    hostscfg['hostinfo']=hostsinfo
    logging.info("hostsinfo is collected complete!")
    return hostscfg

def get_db2port_info(instname):
    logging.info("Begin to get db2portinfo:")
    db2portinfo={}
    db2portcfg={}
    cmd = 'cat /etc/services|grep -i ' + instname.strip()
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
    info = transtoarray(data)
    for i in info:
        k, v = [x.strip() for x in i.split()]
        db2portinfo[k] = v
    db2portcfg['db2portinfo']=db2portinfo
    logging.info("db2portinfo is collected complete!")
    return db2portcfg

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    instname=sys.argv[4]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        p1=get_aix_osinfo()
        p2=get_aix_hostsinfo()
        p3=get_db2port_info(instname)
        pdata=dict(p1.items()+p2.items()+p3.items())
        print json.dumps(pdata)
