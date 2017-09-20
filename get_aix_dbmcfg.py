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


def get_aix_dbmcfg(instname):
    logging.info("Begin to get dbmcfg:")
    cmd_dbmcfg = 'su - ' + instname + ' -c \"db2 get dbm cfg\"|grep \") =\";exit'
    data_dbmcfg  = subprocess.Popen(cmd_dbmcfg,stdout=subprocess.PIPE, shell=True).communicate()[0]
    if data_dbmcfg.find(' = ') != -1 and data_dbmcfg.find('SQLSTATE=') == -1:
        list_dbmdata = []
        dict_dbmcfg={}
        for line in data_dbmcfg.split('\n'):
            data_dbmline=re.findall('\([A-Z_]{3,}\) = .*$',line)
            if data_dbmline:
                data_strline =''.join(data_dbmline).replace('(','').replace(')','').replace(' = ','=')
                data_strline1 = re.sub("=AUTOMATIC\w+","=AUTOMATIC",data_strline)
                data_splitline = data_strline1.split('=')
                list_dbmdata.append(data_splitline)
        dict_dbmcfg=dict(list_dbmdata)
#        dbminfo=sub_dict(dict_dbmcfg,'FEDERATED,DFT_MON_BUFPOOL,DFT_MON_LOCK,DFT_MON_SORT,DFT_MON_STMT,DFT_MON_TABLE,DFT_MON_TIMESTAMP,DFT_MON_UOW,HEALTH_MON,MON_HEAP_SZ,AUDIT_BUF_SZ,INSTANCE_MEMORY,SHEAPTHRES,KEEPFENCED,FENCED_POOL,NUM_INITFENCED,INDEXREC,SVCENAME,INTRA_PARALLEL')
        logging.info("Success to get db dbmcfg End!")
        return dict_dbmcfg
    else:
        logging.error("Failed to get db dbmcfg !")
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    instname=sys.argv[4]
    version=sys.argv[6]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        dict_data_result=get_aix_dbmcfg(instname)
        print json.dumps(dict_data_result)
