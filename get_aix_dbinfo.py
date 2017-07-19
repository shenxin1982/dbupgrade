#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,os,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbinfo.log',
                filemode='w')

def Usage():
    print 'get_aix_dbinfo usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-d,--dbname::<dbname>'
    print '-p,--port::<port>'
    print '-v,--version::<version>'

def main(argv):
    hostname=""
    instname=""
    dbname=""
    port=""
    version=""
    
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:d:p:v:', ["help","hostname=","instname=","dbname=","port=","version="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=11):
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
            elif op in ('-d','--dbname'):
                dbname=ar
            elif op in ('-p','--port'):
                port=ar
            elif op in ('-v','--version'):
                version=ar
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


def get_aix_db2sysc(instname):
    logging.info('Begin to check db2sysc process is exist or not:')
    db2syscmd = 'ps -ef|grep -i db2sysc|grep -i ' + instname.upper().strip() + '|grep -v grep>/dev/null'
    retcode=subprocess.call(db2syscmd,shell=True)
    if retcode == 0: 
        message={'db2_process':'Yes'}
    else:
        message={'db2_process':'No'}
    logging.info('Check db2sysc process end!')
    return message


def get_aix_dbcon(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db con status:')
    condbcmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + '\"'
    condbdata =subprocess.Popen(condbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if condbdata.find(' = ') != -1 and condbdata.find('SQLSTATE=') == -1:
        condbdict={'dbcon_stat':'YES'}
    else:
        condbdict = {'dbcon_stat':'NO'}
    return condbdict


def get_aix_dbtbsinfo(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    regutbsmaxpage=16777216
    largtbsmaxpage=536870912
    condbcmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + '\"'
    condbdata =subprocess.Popen(condbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]

    logging.info('End to check db con status')
    logging.info('Begin to check db tbs status:')
    cktbscmd = 'su - ' + instname + ' -c \" db2  -x \"select tbsp_name,TBSP_TOTAL_SIZE_KB,TBSP_TOTAL_PAGES, tbsp_type,TBSP_CONTENT_TYPE,TBSP_STATE from SYSIBMADM.TBSP_UTILIZATION with ur\"\"'
    cktbsdata = subprocess.Popen(cktbscmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    print cktbsdata
    if cktbsdata.find('SQLSTATE=') != -1:
        logging.error('There are something error:')
        logging.error(cktbsdata)
        retcode=-1
        return retcode
    else:
        tbsdict = {}
        tbsinfo = {}
        tbslist = transtoarray(cktbsdata)
        tbsarray = [map(str,ln.strip().split()) for ln in cktbsdata.splitlines() if ln.strip()]
        tbsdict['tbspaceinfo']=tbsarray
        tbsinfo['tbsname'] = [x[0] for x in tbsarray]
        tbsinfo['tbstotalsize'] = [x[1] for x in tbsarray]
        tbsinfo['tbsmaxpage'] = [x[2] for x in tbsarray]
        tbsinfo['tbstype'] = [x[3] for x in tbsarray]
        tbsinfo['tbscontenttype'] = [x[4] for x in tbsarray]
        tbsinfo['tbsstat'] = [x[5] for x in tbsarray]
    #    return tbsinfo
        return tbsdict



if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2].upper()
    instname=sys.argv[4].upper()
    dbname=sys.argv[6].upper()
    port=sys.argv[8].upper()
    version = sys.argv[10].upper()
    lhostname=socket.gethostname().upper()
    if lhostname!=hostname:
        logging.error("error hostname")
        sys.exit()
    else:
        p1 = get_aix_db2sysc(instname)
        p2 = get_aix_dbcon(instname,dbname)
        p3 = get_aix_dbtbsinfo(instname,dbname)
        pdata = dict(p1.items()+p2.items()+p3.items())
        print pdata
