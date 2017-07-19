#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbcfg.log',
                filemode='w')

def Usage():
    print 'get_aix_dbcfg usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-v,--version::<version>'
    print '-d,--dbname::<version>'

def main(argv):
    hostname=""
    instname=""
    version=""
    dbname=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:v:d:', ["help","hostname=","instname=","version=","dbname="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=9):
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
            elif op in ('-v','--version'):
                version=ar
            elif op in ('-d','--dbname'):
                dbname=ar
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


def get_aix_dbcfg(instname,version,dbname):
    logging.info("Begin to get dbcfg:")
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
##annotate: get the instance db2level
    dblcmd = 'su - ' + instname + ' -c \"db2level\"|grep \"DB2 v\"'
    dbldata = subprocess.Popen(dblcmd,stdout=subprocess.PIPE, shell=True).communicate()[0].split(' ')[4]
    dblspld = ''.join(dbldata).split('.')
    dblevel = ''.join(dblspld[0]).upper()+'.'+''.join(dblspld[1])

    if db2level == dblevel:
        getdbcfgcmd = 'su - ' + instname + ' -c \"db2 get db cfg for ' + dbname + '\"'
        middata = subprocess.Popen(getdbcfgcmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
        if middata.find(' = ') != -1 and middata.find('SQLSTATE=') == -1:
            middata1 = middata.replace('Database territory','(DB_TERRITORY)').replace('Database code page','(DB_CODEPAGE)').replace('Database code set','(DB_CODESET)').replace('Database country/region code','(DB_COUNTRY)').replace('Database collating sequence','(DB_COLLATE)').replace('Number compatibility','(NUM_COMPAT)').replace('Varchar2 compatibility','(VARCHAR2_COMPAT)').replace('Date compatibility','(DATE_COMPAT)').replace('Database page size','(DB_PAGESIZE)').replace('Default number of containers','Default number of containers (DEFNUM_CONT) ').replace('Path to log files','(ACTLOGPATH)').replace('First active log file','(FIRST_ACTLOGFIL)').replace('HADR database role','(HADR_DBROLE)').replace('Database is in write suspend state','(DB_WSSTATE)').replace(' ','')
            midinfo = []
            dbcfg={}
            for line in middata1.split('\n'):
                dblinedata = re.findall('\([A-Z_]{3,}\)=.*$',line)
                if dblinedata:
                    strlinedata=''.join(dblinedata)
                    strlinedata2 = re.sub('\(([A-Z_]{3,})\)=','\\1=',strlinedata)
                    strlinedata3 = re.sub("=AUTOMATIC\(\w+\)","=AUTOMATIC",strlinedata2)
                    splitlinedata = strlinedata3.split('=')
                    midinfo.append(splitlinedata)
            dbcfg=dict(midinfo)
            if db2level in ('V9.1','V9.5','V9.7','V10.1','V10.5','V11.1'):
                logging.info("Success to get dbcfg End!")
                return dbcfg
            else:
                logging.error("db2 version is not in:V9.1,V9.5,V9.7,V10.5,V11.1")
                retcode=-1
                return retcode
        else:
            logging.error("The ouput have something wrong!")
            logging.error(middata)
            retcode=-1
            return retcode
    else:
        logging.error("The input db2 version parameter is not match the instance db2level")
        retcode=-1
        return retcode

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    instname=sys.argv[4]
    version=sys.argv[6]
    dbname=sys.argv[8]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        logging.error("The input hostname is not match the local hostname!")
        sys.exit()
    else:
        pdata=get_aix_dbcfg(instname,version,dbname)
        if pdata != -1:
            print json.dumps(pdata)
        else:
            logging.error("The output is wrong!")
            sys.exit()
