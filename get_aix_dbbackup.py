#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbbackup.log',
                filemode='w')

def Usage():
    print 'get_aix_dbbackup usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-v,--version::<version>'
    print '-d,--dbname::<dbname>'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:d:p:v:', ["help","hostname=","instname=","version=","dbname="])
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



def get_aix_dbbackup(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db backup info:')

    Dict_dbbackup={}
    Cmd_db2set_backup='su - ' + instname + ' -c \"db2set > /tmp/db2set.backup;exit\"'
    Data_db2set_backup=subprocess.Popen(Cmd_db2set_backup,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    Data_db2set_backup.communicate()[0]
    Rc_db2set_backup=Data_db2set_backup.returncode 
    if Rc_db2set_backup==0:
        Dict_dbbackup['dbset_backup'] = 'yes'
    else:
        Dict_dbbackup['dbset_backup'] = 'no'
 
    Cmd_dbmcfg_backup='su - ' + instname + ' -c \"db2 get dbm cfg > /tmp/dbmcfg.backup;exit\"'
    Data_dbmcfg_backup=subprocess.Popen(Cmd_dbmcfg_backup,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    Data_dbmcfg_backup.communicate()[0]
    Rc_dbmcfg_backup=Data_dbmcfg_backup.returncode 
    if Rc_dbmcfg_backup==0:
        Dict_dbbackup['dbmcfg_backup'] = 'yes'
    else:
        Dict_dbbackup['dbmcfg_backup'] = 'no'

    Cmd_dbcfg_backup='su - ' + instname + ' -c \"db2 get db cfg for ' + dbname + ' > /tmp/dbcfg.backup;exit\"'
    Data_dbcfg_backup=subprocess.Popen(Cmd_dbcfg_backup,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    Data_dbcfg_backup.communicate()[0]
    Rc_dbcfg_backup=Data_dbcfg_backup.returncode 
    if Rc_dbcfg_backup==0:
        Dict_dbbackup['dbcfg_backup'] = 'yes'
    else:
        Dict_dbbackup['dbcfg_backup'] = 'no'

    Cmd_function_backup='su - ' + instname + ' -c \"cd ; tar -cvf /tmp/funcbackup.tar ~/sqllib/function;exit\"'
    Data_function_backup=subprocess.Popen(Cmd_function_backup,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    Data_function_backup.communicate()[0]
    Rc_function_backup=Data_function_backup.returncode 
    if Rc_function_backup==0:
        Dict_dbbackup['dbfunc_backup'] = 'yes'
    else:
        Dict_dbbackup['dbfunc_backup'] = 'no'


    Cmd_dbnodes_backup='su - ' + instname + ' -c \"cd ; cp ~/sqllib/db2nodes.cfg /tmp/db2nodes.cfg.backup;exit\"'
    Data_dbnodes_backup=subprocess.Popen(Cmd_dbnodes_backup,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    Data_dbnodes_backup.communicate()[0]
    Rc_dbnodes_backup=Data_dbnodes_backup.returncode 
    if Rc_dbnodes_backup==0:
        Dict_dbbackup['dbnodes_backup'] = 'yes'
    else:
        Dict_dbbackup['dbnodes_backup'] = 'no'

    return Dict_dbbackup


if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2].upper()
    instname=sys.argv[4].upper()
    dbname=sys.argv[8].upper()
    version = sys.argv[6].upper()
    lhostname=socket.gethostname().upper()
    if lhostname!=hostname:
        logging.error("error hostname")
        sys.exit()
    else:
        dict_data_result = get_aix_dbbackup(instname,dbname)
        print json.dumps(dict_data_result)
