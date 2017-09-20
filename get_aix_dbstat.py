#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_db2stat.log',
                filemode='w')
def Usage():
    print 'get_aix_dbstat usage:  '
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


def get_aix_db2sysc(instname,version):
    logging.info('Begin to check db2sysc process is start or not:')
    instname=instname.lower().strip()
    cmd_db2sysc = 'ps -ef|grep -i db2sysc|grep -i ' + instname.strip() + '|grep -v grep>/dev/null'
    retcode=subprocess.call(cmd_db2sysc,shell=True)
    if retcode == 0: 
        Dict_inst_status={'inst_stat':'yes'}
    else:
        Dict_inst_status={'inst_stat':'no'}
    logging.info('Check db2sysc process end!')
    return Dict_inst_status


def get_aix_dbcat(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db con status:')
    Cmd_dbcatalog = 'su - ' + instname + ' -c \" db2 list db directory;exit\"'
    Data_dbcatalog =subprocess.Popen(Cmd_dbcatalog,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if Data_dbcatalog.find(dbname.upper()) != -1 and Data_dbcatalog.find('SQLSTATE=') == -1:
        Dict_dbcatalog={'dbcat_stat':'yes'}
    else:
        Dict_dbcatalog = {'dbcat_stat':'no'}
    return Dict_dbcatalog


def get_aix_tbsinfo(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    Cmd_dbcon_status = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + ';exit\"'
    Data_dbcon_status =subprocess.Popen(Cmd_dbcon_status,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if Data_dbcon_status.find(dbname.upper()) != -1 and Data_dbcon_status.find('SQLSTATE=') == -1:
        logging.info('Begin to check db tbs status:')
        Cmd_check_tbs = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select tbsp_name,tbsp_state from sysibmadm.tbsp_utilization with ur\";exit\"'
        Data_check_tbs = subprocess.Popen(Cmd_check_tbs,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
        if Data_check_tbs.find('SQLSTATE=') != -1:
            logging.error('There are something error:')
            logging.error(Data_check_tbs)
            sys.exit(2)
        else:
            Dict_tbs_info = {}
            List_tbs_info = [map(str,ln.strip().split()) for ln in Data_check_tbs.splitlines() if ln.strip()]
            Dict_tbs_info['tbs_name'] = [x[0] for x in List_tbs_info]
            List_tbs_stat = [x[1] for x in List_tbs_info]
            for  Num_tbs_stat in range(len(List_tbs_stat)):
                if ''.join(List_tbs_stat[Num_tbs_stat]) != 'NORMAL':
                    Dict_tbs_info['tbs_stat']='no'
                else:
                    Dict_tbs_info['tbs_stat']='yes'
            return Dict_tbs_info
    else:
        logging.error('Connect to db have error!')
        logging.error(Data_dbcon_status)
        sys.exit(2)

def get_aix_tblcount(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    Sql_select_table='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select tabschema,tabname,type from syscat.tables with ur\";exit\"'
    Str_Data_table =subprocess.Popen(Sql_select_table,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    List_table_count=[]
    for table_line in Str_Data_table:
        if table_line:
            table_data = ''.join(table_line).split()
            table_sys_data = ''.join(table_data[0])[0:3]
            if table_sys_data != 'SYS' and table_data[2] == 'T':
                List_table_count.append(table_data)
    Dict_table_count = {'tb_count':str(len(List_table_count))}
    return Dict_table_count

def get_aix_db2licm(instname):
    instname=instname.lower()
    Cmd_get_dblicm = 'su - ' + instname + ' -c \" db2licm -l;exit\"'
    Data_get_dblicm = subprocess.Popen(Cmd_get_dblicm,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if Data_get_dblicm.find("Permanent") != -1:
        Dict_dblicm_status = {'db2licm_stat':'yes'}
        logging.info("source host have the right DB2 licm")
    else:
        Dict_dblicm_status = {'db2licm_stat':'no'}
        logging.info("DB2 have not the right DB2 licm")
    return Dict_dblicm_status

def get_aix_db2prod(version):
    Cmd_get_version = '/opt/IBM/db2/'+version.upper()+'/install/db2ls'
    Data_get_version = subprocess.Popen(Cmd_get_version,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if Data_get_version.find(version) != -1:
        Dict_version_status = {'db2prd_stat':'yes'}
        logging.info("host have installed the DB2 product")
        logging.info(version)
    else:
        Dict_version_status = {'db2prd_stat':'no'}
        logging.info("Host have not installed the DB2 product")
        logging.info(version)
    return Dict_version_status

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2].upper()
    instname=sys.argv[4].upper()
    version = sys.argv[6].upper()
    dbname=sys.argv[8].upper()
    lhostname=socket.gethostname().upper()
    if lhostname!=hostname:
        logging.error("error hostname")
        sys.exit()
    else:
        Dict_get_db2sysc = get_aix_db2sysc(instname,version)
        Dict_get_dbcat = get_aix_dbcat(instname,dbname)
        Dict_get_tbsinfo = get_aix_tbsinfo(instname, dbname)
        Dict_get_tbcount = get_aix_tblcount(instname,dbname)
        Dict_get_dblicm = get_aix_db2licm(instname)
        Dict_get_dbversion = get_aix_db2prod(version)
        dict_data_result = dict(Dict_get_db2sysc.items()+Dict_get_dbcat.items()+Dict_get_tbsinfo.items()+Dict_get_tbcount.items()+Dict_get_dblicm.items()+Dict_get_dbversion.items())
        print json.dumps(dict_data_result)
