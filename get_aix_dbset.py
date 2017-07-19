#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_db2set.log',
                filemode='w')

def Usage():
    print 'get_aix_db2set usage:  '
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
    dblcmd = 'su - ' + instname + ' -c \"db2level\"|grep \"DB2 v\"'
    dbldata = subprocess.Popen(dblcmd,stdout=subprocess.PIPE, shell=True).communicate()[0].split(' ')[4]
    dblspld = ''.join(dbldata).split('.')
    dblevel = ''.join(dblspld[0]).upper()+'.'+''.join(dblspld[1])
    if db2level == dblevel:
        return 125
    else:
        return -1    



def get_aix_db2set(instname,version):
    logging.info("Begin to get db2set:")
    dbckint=ck_db_version(instname,version)
    if dbckint==125:
        getsetcmd = 'su - '+ instname + ' -c \"db2set\"'
        middata = subprocess.Popen(getsetcmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
        if middata == '':
            logging.info("DB2set parameter is not set!")
            retcode=-1
            return retcode
        elif middata.find('=') != -1 and middata.find('SQLSTATE=')== -1:
            setcfg={}
            midinfo = transtoarray(middata)
            for line in midinfo:
                key, value = [x.strip() for x in line.split('=')]
                setcfg[key] = value
            setinfo = sub_dict(setcfg,'DB2_LOAD_COPY_NO_OVERRIDE,DB2_MAX_GLOBAL_SNAPSHOT_SIZE,DB2_USE_ALTERNATE_PAGE_CLEANING,DB2_LOGGER_NON_BUFFERED_IO,DB2_SNAPSHOT_NOAUTH,DB2_TRUST_MDC_BLOCK_FULL_HINT,DB2_MDC_ROLLOUT,DB2_EVALUNCOMMITTED,DB2_SKIPINSERTED,DB2SOSNDBUF,DB2SORCVBUF,DB2_ANTIJOIN,DB2_FORCE_FCM_BP,DB2_PARALLEL_IO,DB2COMM,DB2AUTOSTART,DB2CODEPAGE,DB2_HADR_SOSNDBUF,DB2_HADR_SORCVBUF,DB2_HADR_NO_IP_CHECK,DB2_HADR_BUF_SIZE,DB2_HADR_PEER_WAIT_LIMIT,DB2_HADR_ROS,DB2_STANDBY_ISO')
#                setinfo=sub_dict(setcfg,'DB2_OVERRIDE_BPF,DB2_PARALLEL_IO,DB2ACCOUNT,DB2ADMINSERVER,DB2BQTIME,DB2BQTRY,DB2CHKPTR,DB2CLIINIPATH,DB2CODEPAGE,DB2COMM,DB2DBDFT,DB2DBMSADDR,DB2INCLUDE,DB2INSTDEF,DB2INSTPROF,DB2IQTIME,DB2LOADREC,DB2LOCK_TO_RB,DB2OPTIONS,DB2PATH,DB2PRIORITIES,DB2REMOTEPREG,DB2RQTIME,DB2SORCVBUF,DB2SORT,DB2SOSNDBUF,DB2SYSTEM,DB2_FORCE_NLS_CACHE,DB2_AVOID_PREFETCH,DB2_COLLECT_TS_REC_INFO,DB2_GRP_LOOKUP,DB2_MMAP_READ,DB2_MMAP_WRITE,DB2DISCOVERYTIME,DB2ENVLIST,DB2MEMDISCLAIM,DB2LIBPATH,DB2CHKSQLDA,DB2NOEXITLIST,DB2LOADFLAGS,DB2NTMEMSIZE,DB2CHECKCLIENTINTERVAL,DB2_FALLBACK,DB2PROCESSORS,DB2_SORT_AFTER_TQ,DB2ASSUMEUPDATE,DB2MAXFSCRSEARCH,DB2BIDI,DB2_NEW_CORR_SQ_FF,DB2CHGPWD_EEE,DB2LOCALE,DB2_SKIPDELETED,DB2_SMP_INDEX_CREATE,DB2LDAPHOST,DB2LDAPCACHE,DB2LDAP_BASEDN,DB2_ENABLE_LDAP,DB2_SYSTEM_MONITOR_SETTINGS,DB2_FCM_SETTINGS,DB2SATELLITEID,DB2_LIC_STAT_SIZE,DB2CONNECT_IN_APP_PROCESS,DB2_NUM_FAILOVER_NODES,DB2_DJ_INI,DB2TCPCONNMGRS,DB2_SQLROUTINE_PREPOPTS,DB2_ANTIJOIN,DB2_DISABLE_FLUSH_LOG,DB2_SELECTIVITY,DB2_EXTENDED_OPTIMIZATION,DB2_PINNED_BP,DB2_APM_PERFORMANCE,DB2_XBSA_LIBRARY,DB2_VENDOR_INI,DB2DOMAINLIST,DB2_FMP_COMM_HEAPSZ,DB2_LOGGER_NON_BUFFERED_IO,DB2_EVALUNCOMMITTED,DB2TERRITORY,DB2_PARTITIONEDLOAD_DEFAULT,DB2_REDUCED_OPTIMIZATION,DB2_USE_PAGE_CONTAINER_TAG,DB2_NUM_CKPW_DAEMONS,DB2_KEEPTABLELOCK,DB2GRAPHICUNICODESERVER,DB2_MINIMIZE_LISTPREFETCH,DB2_INLIST_TO_NLJN,DB2STMM,DB2_MEM_TUNING_RANGE,DB2_CLPPROMPT,DB2_FORCE_APP_ON_MAX_LOG,DB2_BCKP_INCLUDE_LOGS_WARNING,DB2_BCKP_PAGE_VERIFICATION,DB2_CLP_EDITOR,DB2_CLP_HISTSIZE,DB2LOGINRESTRICTIONS,DB2_LOAD_COPY_NO_OVERRIDE,DB2_MAX_NON_TABLE_LOCKS,DB2_SMS_TRUNC_TMPTABLE_THRESH,DB2_USE_ALTERNATE_PAGE_CLEANING,DB2_HADR_BUF_SIZE,DB2_MAX_CLIENT_CONNRETRIES,DB2_CONNRETRIES_INTERVAL,DB2_DOCHOST,DB2_DOCPORT,DB2_TAPEMGR_TAPE_EXPIRATION,DB2_OBJECT_TABLE_ENTRIES,DB2_LOGGING_DETAIL,DB2_VIEW_REOPT_VALUES,DB2_SELUDI_COMM_BUFFER,DB2_RESOURCE_POLICY,DB2TCP_CLIENT_RCVTIMEOUT,DB2_DDL_SOFT_INVAL,DB2_SKIPINSERTED,DB2CONNECT_DISCONNECT_ON_INTERRUPT,DB2_LARGE_PAGE_MEM,DB2_HISTORY_FILTER,DB2_ALTERNATE_GROUP_LOOKUP,DB2AUTH,DB2FODC,DB2RSHCMD,DB2RSHTIMEOUT,DB2_DMU_DEFAULT,DB2_MDC_ROLLOUT,DB2_TRUNCATE_REUSESTORAGE,DB2_WORKLOAD,DB2_DXX_PATHS_ALLOWED_READ,DB2_DXX_PATHS_ALLOWED_WRITE,DB2TCP_CLIENT_CONTIMEOUT,DB2_MAX_INACT_STMTS,DB2_USE_FAST_PREALLOCATION,DB2FCMCOMM,DB2_EXTENDED_IO_FEATURES,DB2_UTIL_MSGPATH,DB2_ENABLE_AUTOCONFIG_DEFAULT,DB2_OPT_MAX_TEMP_SIZE,DB2_MAX_LOB_BLOCK_SIZE,DB2_MINIMUM_CLIENT_LEVEL,DB2CONNECT_ENABLE_EURO_CODEPAGE,DB2_RESOLVE_CALL_CONFLICT,DB2_IO_PRIORITY_SETTING,DB2_EVMON_STMT_FILTER,DB2_SERVER_CONTIMEOUT,DB2_DISPATCHER_PEEKTIMEOUT,DB2_CONNECT_GWY_AUTH_SUPP,DB2_EVMON_EVENT_LIST_SIZE,DB2_MEMORY_PROTECT,DB2_SET_MAX_CONTAINER_SIZE,DB2_UPDDBCFG_SINGLE_DBPARTITION,DB2_LIMIT_FENCED_GROUP,DB2_MAX_GLOBAL_SNAPSHOT_SIZE,DB2_COMPATIBILITY_VECTOR,DB2_CAPTURE_LOCKTIMEOUT,DB2_HADR_NO_IP_CHECK,DB2_HADR_PEER_WAIT_LIMIT,DB2_THREAD_SUSPENSION,DB2_OPTSTATS_LOG,DB2_ATS_ENABLE,DB2_PMODEL_SETTINGS,DB2_KEEP_AS_AND_DMS_CONTAINERS_OPEN,DB2RESILIENCE,DB2_FORCE_OFFLINE_ADD_PARTITION,DB2_HADR_SOSNDBUF,DB2_HADR_SORCVBUF,DB2_DEFERRED_PREPARE_SEMANTICS,DB2TCP_CLIENT_KEEPALIVE_TIMEOUT,DB2_PMAP_COMPATIBILITY,DB2_HADR_ROS,DB2_STANDBY_ISO,DB2_BACKUP_USE_DIO,DB2_NCHAR_SUPPORT,DB2_RESTORE_GRANT_ADMIN_AUTHORITIES,DB2_ENFORCE_MEMBER_SYNTAX,DB2_MEMBER_LOAD_WEIGHT_COMPOSITION,DB2_CF_API_SAMPLING_COUNT,DB2_CF_API_SAMPLING_INTERVAL,DB2_CF_API_SPIN_YIELD_THRESHOLD,DB2_CPU_BINDING,DB2_AVOID_SECONDARY_DELETE,DB2_SAL_FAILOVER_REGISTERPAGES_INSTEADOF_INVALIDATE_ALL,DB2_DATABASE_CF_MEMORY,DB2_MCR_RECOVERY_PARALLELISM_CAP,DB2_CONFIG_OS_ENV,DB2_SQLWORKSPACE_CACHE,DB2TCP_SERVER_KEEPALIVE_TIMEOUT,DB2_INDEX_PCTFREE_DEFAULT,DB2_ALLOW_WLB_WITH_SEQUENCES,DB2_XSLT_ALLOWED_PATH,DB2_SAS_SETTINGS,DB2LDAP_UID,DB2LDAP_PWD,DB2_SD_ALLOW_SLOW_NETWORK,DB2_TRANSCHEMA_EXCLUDE_STATS,DB2_REDUCE_LEAF_PREFETCH_REQUESTS')
            logging.info("Success to get db2set End!")
            return setinfo
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
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        pdata=get_aix_db2set(instname,version)
        if pdata != -1:
            print json.dumps(pdata)
        else:
            logging.error("The output is wrong!")
            sys.exit()
