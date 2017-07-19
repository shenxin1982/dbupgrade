#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,os,re,sys,getopt,socket,json,logging,commands

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbprod.log',
                filemode='w')

def Usage():
    print 'get_aix_dbprod usage:  '
    print '-h,--help: print help message.'
    print '-s,--shostname::<shostname>'
    print '-o,--thostname::<thostname>'
    print '-i,--sinstname::<sinstname>'
    print '-n,--tinstname::<tinstname>'
    print '-v,--sversion::<sversion>'
    print '-t,--tversion::<tversion>'

def main(argv):
    shostname=""
    thostname=""
    sinstname=""
    tinstname=""
    sversion=""
    tversion=""
    
    try:
        opts, args = getopt.getopt(argv[1:], 'hs:o:i:n:v:t:', ["help","shostname=","thostname=","sinstname=","tinstname=","sversion=","tversion="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit()
    if(len(sys.argv)!=13):
        logging.error("The input paramters length is not correct!") 
        Usage()
        sys.exit()
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif op in ('-s','--shostname'):
                shostname=ar
            elif op in ('-o','--thostname'):
                thostname=ar
            elif op in ('-i','--sinstname'):
                sinstname=ar
            elif op in ('-n','--tinstname'):
                tinstname=ar
            elif op in ('-v','--sversion'):
                sversion=ar
            elif op in ('-t','--tversion'):
                tversion=ar
            else:
                logging.error("invalid parameters")
                Usage()
                sys.exit()


def transtoarray(data):
    info=[]
    for i in data.split('\n\n'):
        for x in i.splitlines():
            if x:
                info.append(x)
    return info 

def sub_dict(form_dict, sub_keys, default=None):
    return dict([(k, form_dict.get(k.strip(), default)) for k in sub_keys.split(',')])

## deal the input parameter version from V10.5.0.5 to V10.5
def mod_dbversion(data):
    dblevel = data.split(".")
    if dblevel[0] in ('V10','V11'):
        dbversion = data[0:5]
        return dbversion
    elif dblevel[0] == 'V9':
        dbversion = data[0:4]
        return dbversion
    else:
        logging.error("invalid dbversion!")
        dbversion = 'Error'
        return dbversion

def ck_aix_db2prod(sdbversion,versiondata,tdbversion):
    if sdbversion=='V9.1' and versiondata.find('V9.1') != -1 and versiondata.find('V9.7') != -1 and versiondata.find(tdbversion) != -1:
        message = {'DB2_product':'Yes'}
        logging.info("target host have the right DB2  version")
    elif sdbversion=='V9.5' and versiondata.find('V9.5') != -1 and versiondata.find('V9.7') != -1 and versiondata.find(tdbversion) != -1:
        message = {'DB2_product':'Yes'}
        logging.info("target host have the right DB2 version")
    elif sdbversion=='V9.7' and  versiondata.find('V9.7') != -1 and versiondata.find(tdbversion) != -1:
        message = {'DB2_product':'Yes'}
        logging.info("target host have the right DB2 version")
    elif sdbversion=='V10.1' and versiondata.find('V10.1') != -1 and versiondata.find(tdbversion) != -1:
        message = {'DB2_product':'Yes'}
        logging.info("target host have the right DB2 version")
    else:
        message = {'DB2_product':'No'}
        logging.error("target host DB2 version is not installed compelete")
    return message


def get_aix_db2prod(shostname,thostname,sversion,tversion):
    sdbversion=mod_dbversion(sversion) 
    tdbversion=mod_dbversion(tversion) 
    lhostname=socket.gethostname()
    sversioncmd = '/opt/IBM/db2/'+sversion.upper()+'/install/db2ls'
    tversioncmd = '/opt/IBM/db2/'+tversion.upper()+'/install/db2ls'
    sversiondata = subprocess.Popen(sversioncmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    tversiondata = subprocess.Popen(tversioncmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if shostname!=thostname:
        if lhostname==shostname and tdbversion in ('V10.5','V11.1'):
            if sdbversion=='V9.1' and sversiondata.find('V9.1') != -1:
                message = {'DB2_product':'Yes'}
                logging.info("source host have the right DB2 V9.1 version")
            elif sdbversion=='V9.5' and sversiondata.find('V9.5') != -1:
                message = {'DB2_product':'Yes'}
                logging.info("source host have the right DB2 V9.5 version")
            elif sdbversion=='V9.7' and sversiondata.find('V9.7') != -1:
                message = {'DB2_product':'Yes'}
                logging.info("source host have the right DB2 V9.7 version")
            elif sdbversion=='V10.1' and sversiondata.find('V10.1') != -1:
                message = {'DB2_product':'Yes'}
                logging.info("source host have the right DB2 V10.1 version")
            elif sdbversion=='V10.5' and sversiondata.find('V10.5') != -1:
                message = {'DB2_product':'Yes'}
                logging.info("source host have the right DB2 V10.5 version")
            else:
                message = {'DB2_product':'No'}
                logging.error("source host DB2 version are not in v9.1,v9.5,v9.7,v10.1,v10.5")
        elif lhostname==thostname and tdbversion=='V10.5':
             message = ck_aix_db2prod(sdbversion,tversiondata,tdbversion)
        elif lhostname==thostname and tdbversion=='V11.1':
             message = ck_aix_db2prod(sdbversion,tversiondata,tdbversion)
        else:
            message = {'DB2_product':'Error'}
            logging.error("Not Correct DB2 version or Host")
    else:
        if tdbversion=='V10.5':
            message = ck_aix_db2prod(sdbversion,tversiondata,tdbversion)
        elif tdbversion=='V11.1':
            message = ck_aix_db2prod(sdbversion,tversiondata,tdbversion)   
        else:
            message = {'DB2_product':'Error'}
            logging.error("Not Correct DB2 version or Host")
    return message


def get_aix_db2licm(shostname,thostname,sversion,tversion):
    lhostname=socket.gethostname().upper()
    slicmcmd = '/opt/IBM/db2/'+sversion.upper()+'/adm/db2licm -l'
    tlicmcmd = '/opt/IBM/db2/'+tversion.upper()+'/adm/db2licm -l'
    slicmdata = subprocess.Popen(slicmcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    tlicmdata = subprocess.Popen(tlicmcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if shostname != thostname:
        if lhostname==shostname and slicmdata.find("Permanent") != -1:
            message = {'DB2_licm':'Yes'}
            logging.info("source host have the right DB2 licm")
        elif lhostname==thostname and tlicmdata.find("Permanent") != -1:
            message = {'DB2_licm':'Yes'}
            logging.info("target host have the right DB2 licm")
        else:
            message = {'DB2_licm':'No'}    
            logging.info("DB2 have not the right DB2 licm")
    else:
        if slicmdata.find("Permanent") != -1 and tlicmdata.find("Permanent") != -1:
            message = {'DB2_licm':'Yes'}
            logging.info("DB2 in the same host and have the right DB2 licm")
        else:
            message = {'DB2_licm':'No'}
            logging.info("DB2 in the same host and have not the right DB2 licm")
    return message

if __name__ == '__main__':
    main(sys.argv)
    shostname=sys.argv[2].upper()
    thostname=sys.argv[4].upper()
    sinstname=sys.argv[6].upper()
    tinstname=sys.argv[8].upper()
    sversion = sys.argv[10].upper()
    tversion = sys.argv[12].upper()
    lhostname=socket.gethostname().upper()
    if lhostname not in (shostname,thostname):
        logging.error("Not Correct Host")
        sys.exit()
    else:
        p1=get_aix_db2prod(shostname,thostname,sversion,tversion)
        p2=get_aix_db2licm(shostname,thostname,sversion,tversion)
        pdata = dict(p1.items()+p2.items())
        print json.dumps(pdata)
