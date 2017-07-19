#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbmcfg.log',
                filemode='w')

def Usage():
    print 'get_aix_dbmcfg usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-v,--version::<version>'

def main(argv):
    hostname=""
    instname=""
    version=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:v:', ["help","hostname=","instname=","version="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
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
            elif op in ('-v','--version'):
                version=ar
            else:
                logging.error("invalid parameters")
                Usage()
                sys.exit()


def sub_dict(form_dict, sub_keys, default=None):
    return dict([(k, form_dict.get(k.strip(), default)) for k in sub_keys.split(',')])


def get_aix_dbmcfg(instname,version):
    logging.info("Begin to get dbmcfg:")
## deal the input parameter version from V10.5.0.5 to V10.5
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
        dbmcmd = 'su - ' + instname + ' -c \"db2 get dbm cfg\"|grep \") =\"'
        dbmdata  = subprocess.Popen(dbmcmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
        if dbmdata.find(' = ') != -1 and dbmdata.find('SQLSTATE=') == -1:
            midinfo = []
            dbmcfg={}
            for line in dbmdata.split('\n'):
                dbmlinedata=re.findall('\([A-Z_]{3,}\) = .*$',line)
                if dbmlinedata:
                    strlinedata =''.join(dbmlinedata).replace('(','').replace(')','').replace(' = ','=')
                    strlinedata2 = re.sub("=AUTOMATIC\w+","=AUTOMATIC",strlinedata)
                    splitlinedata = strlinedata2.split('=')
                    midinfo.append(splitlinedata)
            dbmcfg=dict(midinfo)
            if db2level in ('V9.1','V9.5','V9.7','V10.1','V10.5','V11.1'):
#            dbminfo=sub_dict(dbmcfg,'FEDERATED,DFT_MON_BUFPOOL,DFT_MON_LOCK,DFT_MON_SORT,DFT_MON_STMT,DFT_MON_TABLE,DFT_MON_TIMESTAMP,DFT_MON_UOW,HEALTH_MON,MON_HEAP_SZ,AUDIT_BUF_SZ,INSTANCE_MEMORY,SHEAPTHRES,KEEPFENCED,FENCED_POOL,NUM_INITFENCED,INDEXREC,SVCENAME,INTRA_PARALLEL')
                logging.info("Success to get db version v11.1 dbmcfg End!")
                return dbmcfg
            else:
                logging.error("db2 version is not in:V9.1,V9.5,V9.7,V10.5,V11.1")
                retcode=-1
                return retcode
        else:
            logging.error("The ouput have something wrong!")
            logging.error(dbmdata)
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
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        pdata=get_aix_dbmcfg(instname,version)
        if pdata != -1:
            print json.dumps(pdata)
        else:
            logging.error("The output is wrong!")
            sys.exit()
