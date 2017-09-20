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



def get_aix_db2set(instname,version):
    logging.info("Begin to get db2set:")
    Cmd_get_db2set = 'su - '+ instname + ' -c \"db2set;exit\"'
    Data_get_db2set = subprocess.Popen(Cmd_get_db2set,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if Data_get_db2set == '':
        logging.info("DB2set parameter is not set!")
        sys.exit(2)
    elif Data_get_db2set.find('=') != -1 and Data_get_db2set.find('SQLSTATE=')== -1:
        Dict_db2set={}
        List_db2set_data = transtoarray(Data_get_db2set)
        for Line_db2set_data in List_db2set_data:
            key, value = [x.strip() for x in Line_db2set_data.split('=')]
            Dict_db2set[key] = value
        Dict_db2set_data = sub_dict(Dict_db2set,'DB2_LOAD_COPY_NO_OVERRIDE,DB2_MAX_GLOBAL_SNAPSHOT_SIZE,DB2_USE_ALTERNATE_PAGE_CLEANING,DB2_LOGGER_NON_BUFFERED_IO,DB2_SNAPSHOT_NOAUTH,DB2_TRUST_MDC_BLOCK_FULL_HINT,DB2_MDC_ROLLOUT,DB2_EVALUNCOMMITTED,DB2_SKIPINSERTED,DB2SOSNDBUF,DB2SORCVBUF,DB2_ANTIJOIN,DB2_FORCE_FCM_BP,DB2_PARALLEL_IO,DB2COMM,DB2AUTOSTART,DB2CODEPAGE,DB2_HADR_SOSNDBUF,DB2_HADR_SORCVBUF,DB2_HADR_NO_IP_CHECK,DB2_HADR_BUF_SIZE,DB2_HADR_PEER_WAIT_LIMIT,DB2_HADR_ROS,DB2_STANDBY_ISO')
        logging.info("Success to get db2set End!")
        return Dict_db2set_data
    else:
        logging.error("The ouput have something wrong!")
        logging.error(Data_get_db2set)
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    instname=sys.argv[4]
    version=sys.argv[6]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit(2)
    else:
        dict_data_result=get_aix_db2set(instname,version)
        print json.dumps(dict_data_result)
