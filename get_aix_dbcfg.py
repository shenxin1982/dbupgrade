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
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:v:d:', ["help","hostname=","instname=","version=","dbname="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=9):
        logging.error("The input paramters length is not correct!")
        Usage()
        sys.exit(2)
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
                sys.exit(2)

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
    cmd_dbcfg = 'su - ' + instname + ' -c \"db2 get db cfg for ' + dbname + ';exit\"'
    data_dbcfg = subprocess.Popen(cmd_dbcfg,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if data_dbcfg.find(' = ') != -1 and data_dbcfg.find('SQLSTATE=') == -1:
        data1_dbcfg = data_dbcfg.replace('Database territory','(DB_TERRITORY)').replace('Database code page','(DB_CODEPAGE)').\
        replace('Database code set','(DB_CODESET)').replace('Database country/region code','(DB_COUNTRY)').\
        replace('Database collating sequence','(DB_COLLATE)').replace('Number compatibility','(NUM_COMPAT)').\
        replace('Varchar2 compatibility','(VARCHAR2_COMPAT)').replace('Date compatibility','(DATE_COMPAT)').\
        replace('Database page size','(DB_PAGESIZE)').replace('Default number of containers','Default number of containers (DEFNUM_CONT) ').\
        replace('Path to log files','(ACTLOGPATH)'). replace('First active log file','(FIRST_ACTLOGFIL)').replace('HADR database role','(HADR_DBROLE)').\
        replace('Database is in write suspend state','(DB_WSSTATE)').replace(' ','')
        list_middata = []
        dict_dbcfg={}
        for line in data1_dbcfg.split('\n'):
            data_dbline = re.findall('\([A-Z_]{3,}\)=.*$',line)
            if data_dbline:
                data_strline=''.join(data_dbline)
                data1_strline = re.sub('\(([A-Z_]{3,})\)=','\\1=',data_strline)
                data2_strline = re.sub("=AUTOMATIC\(\w+\)","=AUTOMATIC",data1_strline)
                data_splitline = data2_strline.split('=')
                list_middata.append(data_splitline)
        dict_dbcfg=dict(list_middata)
#        if dict_dbcfg['HADR_DBROLE'] in ('PRIMARY','STANDBY'):
#            dict_dbinfo = sub_dict(dict_dbcfg,'DFT_DEGREE,SELF_TUNING_MEM,DATABASE_MEMORY,DB_MEM_THRESH,LOCKLIST,MAXLOCKS,PCKCACHESZ,SHEAPTHRES_SHR,SORTHEAP,DBHEAP,CATALOGCACHE_SZ,LOGBUFSZ,UTIL_HEAP_SZ,STMTHEAP,APPLHEAPSZ,APPL_MEMORY,STAT_HEAP_SZ,DLCHKTIME,LOCKTIMEOUT,TRACKMOD,MAXFILOP,LOGFILSIZ,LOGPRIMARY,LOGSECOND,ACTLOGPATH,MIRRORLOGPATH,BLK_LOG_DSK_FUL,BLOCKNONLOGGED,MAX_LOG,NUM_LOG_SPAN,SOFTMAX,LOGARCHMETH1,LOGARCHMETH2,AUTORESTART,INDEXREC,LOGINDEXBUILD,NUM_DB_BACKUPS,REC_HIS_RETENTN,AUTO_DEL_REC_OBJ,AUTO_MAINT,AUTO_DB_BACKUP,AUTO_TBL_MAINT,AUTO_RUNSTATS,AUTO_STMT_STATS,AUTO_REORG,HADR_DBROLE,HADR_LOCAL_HOST,HADR_LOCAL_SVC,HADR_REMOTE_HOST,HADR_REMOTE_SVC,HADR_REMOTE_INST,HADR_TIMEOUT,HADR_SYNCMODE,HADR_PEER_WINDOW'
#        else:
#            dict_dbinfo = sub_dict(dict_dbcfg,'DFT_DEGREE,SELF_TUNING_MEM,DATABASE_MEMORY,DB_MEM_THRESH,LOCKLIST,MAXLOCKS,PCKCACHESZ,SHEAPTHRES_SHR,SORTHEAP,DBHEAP,CATALOGCACHE_SZ,LOGBUFSZ,UTIL_HEAP_SZ,STMTHEAP,APPLHEAPSZ,APPL_MEMORY,STAT_HEAP_SZ,DLCHKTIME,LOCKTIMEOUT,TRACKMOD,MAXFILOP,LOGFILSIZ,LOGPRIMARY,LOGSECOND,ACTLOGPATH,MIRRORLOGPATH,BLK_LOG_DSK_FUL,BLOCKNONLOGGED,MAX_LOG,NUM_LOG_SPAN,SOFTMAX,LOGARCHMETH1,LOGARCHMETH2,AUTORESTART,INDEXREC,LOGINDEXBUILD,NUM_DB_BACKUPS,REC_HIS_RETENTN,AUTO_DEL_REC_OBJ,AUTO_MAINT,AUTO_DB_BACKUP,AUTO_TBL_MAINT,AUTO_RUNSTATS,AUTO_STMT_STATS,AUTO_REORG' 
        logging.info("Success to get dbcfg End!")
        return dict_dbcfg
    else:
        logging.error("Error to get db cfg")
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    instname=sys.argv[4]
    version=sys.argv[6]
    dbname=sys.argv[8]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        logging.error("The input hostname is not match the local hostname!")
        sys.exit(2)
    else:
        dict_data_result=get_aix_dbcfg(instname,version,dbname)
        print json.dumps(dict_data_result)
