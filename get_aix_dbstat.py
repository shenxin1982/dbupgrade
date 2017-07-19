#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,os,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbstat.log',
                filemode='w')

def Usage():
    print 'get_aix_dbstat usage:  '
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

def ck_db_version(instname,version):
    dbversion = version.upper()
    dbversion1 = dbversion.split(".")
    if dbversion1[0] in ('V10','V11'):
        db2level=dbversion[0:5]
    elif dbversion1[0] == 'V9':
        db2level=dbversion[0:4]
    else:
        logging.error("invalid dbversion!")
        retcode=-1
        return retcode
    dblcmd = 'su - ' + instname.lower() + ' -c \"db2level\"|grep \"DB2 v\"'
    dbldata = subprocess.Popen(dblcmd,stdout=subprocess.PIPE, shell=True).communicate()[0].split(' ')[4]
    dblspld = ''.join(dbldata).split('.')
    dblevel = ''.join(dblspld[0]).upper()+'.'+''.join(dblspld[1])
    if db2level == dblevel:
        return 125
    else:
        return -1    


def get_aix_db2sysc(instname,version):
    logging.info('Begin to check db2sysc process is start or not:')
    instname=instname.lower().strip()
    if ck_db_version(instname,version)==125:
        db2syscmd = 'ps -ef|grep -i db2sysc|grep -i ' + instname.strip() + '|grep -v grep>/dev/null'
        retcode=subprocess.call(db2syscmd,shell=True)
        if retcode == 0: 
            message={'db2_process':'Yes'}
        else:
            message={'db2_process':'No'}
        logging.info('Check db2sysc process end!')
        return message
    else:
        logging.error('The instance version is wrong')
        retcode=-1
        return retcode


def get_aix_dbcat(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db con status:')
    catdbcmd = 'su - ' + instname + ' -c \" db2 list db directory\"'
    catdbdata =subprocess.Popen(catdbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if catdbdata.find(dbname.upper()) != -1 and catdbdata.find('SQLSTATE=') == -1:
        catdbdict={'dbcat_stat':'Yes'}
    else:
        catdbdict = {'dbcon_stat':'No'}
    return catdbdict


def get_aix_dbtbsinfo(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    condbcmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + '\"'
    condbdata =subprocess.Popen(condbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if condbdata.find(dbname.upper()) != -1 and condbdata.find('SQLSTATE=') == -1:
        logging.info('Begin to check db tbs status:')
        cktbscmd = 'su - ' + instname + ' -c \" db2  -x \"select tbsp_name,TBSP_TOTAL_SIZE_KB,TBSP_TOTAL_PAGES, tbsp_type,TBSP_CONTENT_TYPE,TBSP_STATE from SYSIBMADM.TBSP_UTILIZATION with ur\"\"'
        cktbsdata = subprocess.Popen(cktbscmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
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
            tbsinfo['tbsname'] = [x[0] for x in tbsarray]
            tbsstatlist = [x[5] for x in tbsarray]
            for  i in range(len(tbsstatlist)):
                if ''.join(tbsstatlist[i]) != 'NORMAL':
                    tbsinfo['tbsstat']='No'
                else:
                    tbsinfo['tbsstat']='Yes'
            return tbsinfo
    else:
        logging.error('Connect to db have error!')
        logging.error(condbdata)
        retcode=-1
        return retcode

def get_aix_tblcount(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    condbcmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + '\"'
    condbdata =subprocess.Popen(condbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if condbdata.find(dbname.upper()) != -1 and condbdata.find('SQLSTATE=') == -1:
        logging.info('Begin to check table count:')
        cktblcountcmd = 'su - ' + instname + ' -c \"db2 -x \"select tabname from syscat.tables where tabschema not like \'SYS%\' with ur\"\"'
        print cktblcountcmd
        cktblcountdata = subprocess.Popen(cktblcountcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
        print cktblcountdata
        if cktblcountdata.find('SQLSTATE=') != -1:
            logging.error('There are something error:')
            logging.error(cktblcountdata)
            retcode=-1
            return retcode
        else:
            tblcountdict={}
            tblcountdict['tblcount']=cktblcountdata
            print tblcountdict
    else:
        logging.error('Connect to db have error!')
        logging.error(condbdata)
        retcode=-1
        return retcode        


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
        p1 = get_aix_db2sysc(instname,version)
        p2 = get_aix_dbcat(instname,dbname)
        p3 = get_aix_dbtbsinfo(instname,dbname)
        p4 = get_aix_tblcount(instname,dbname)
        if p1 != -1 and p2 != -1 and p3 != -1:
            pdata = dict(p1.items()+p2.items()+p3.items())
            print json.dumps(pdata)
        else:
            logging.error("The output is wrong!")
            sys.exit()
