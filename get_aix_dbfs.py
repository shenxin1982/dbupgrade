#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,re,json

def Usage():
    print 'get_aix_dbfs usage:  '
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


def fsubstr(substrings,destString):
    return ', '.join([str([destString.index(x),x]) for x in substrings if x in destString])


def get_aix_dbfsinfo():
    fsinfo={}
    dbhomedata = subprocess.Popen('lsfs|grep -i \'/db/dbhome\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    managedata = subprocess.Popen('lsfs|grep -i \'/db/manage\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    dbdiagdata = subprocess.Popen('lsfs|grep -i \'/db/dbdiag\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    actlogdata = subprocess.Popen('lsfs|grep -i \'/db/actlog\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    mirlogdata = subprocess.Popen('lsfs|grep -i \'/db/mirlog\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    dbdatadata = subprocess.Popen('lsfs|grep -i \'/db/dbdata\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    archm1data = subprocess.Popen('lsfs|grep -i \'/db/archm1\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    archm2data = subprocess.Popen('lsfs|grep -i \'/db/archm2\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    fsinfo = dict(zip(('dbhomepath','dbhomesize','dbhomefstype','managepath','managesize','managefstype','dbdiagpath','dbdiagsize','dbdiagfstype','actlogpath','actlogsize','actlogfstype','mirlogpath','mirlogsize','mirlogfstype','dbdatapath','dbdatasize','dbdatafstype','archm1path','archm1size','archm1fstype','archm2path','archm2size','archm2fstype'),(dbhomedata[2],dbhomedata[4],dbhomedata[3],managedata[2],managedata[4],managedata[3],dbdiagdata[2],dbdiagdata[4],dbdiagdata[3],actlogdata[2],actlogdata[4],actlogdata[3],mirlogdata[2],mirlogdata[4],mirlogdata[3],dbdatadata[2],dbdatadata[4],dbdatadata[3],archm1data[2],archm1data[4],archm1data[3],archm2data[2],archm2data[4],archm2data[3])))
    return fsinfo 



if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        pdata=get_aix_dbfsinfo()
        print json.dumps(pdata)
