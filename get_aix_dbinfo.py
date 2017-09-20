#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

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



def get_aix_db2sysc(instname):
    logging.info('Begin to check db2sysc process is exist or not:')
    cmd_db2sysc = 'ps -ef|grep -i db2sysc|grep -i ' + instname.upper().strip() + '|grep -v grep>/dev/null'
    retcode=subprocess.call(cmd_db2sysc,shell=True)
    if retcode == 0: 
        message={'inst_stat':'yes'}
    else:
        message={'inst_stat':'no'}
    logging.info('Check db2sysc process end!')
    return message


def get_aix_dbcon(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db con status:')
    cmd_dbcon = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + ';exit\"'
    data_dbcon =subprocess.Popen(cmd_dbcon,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if data_dbcon.find(' = ') != -1 and data_dbcon.find('SQLSTATE=') == -1:
        dict_dbcon={'dbcon_stat':'yes'}
    else:
        dict_dbcon = {'dbcon_stat':'no'}
    return dict_dbcon


def get_aix_dbtbsinfo(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    regutbsmaxpage=16777216
    largtbsmaxpage=536870912
    logging.info('Begin to check db tbs status:')
    cmd_cktbs = 'su - ' + instname + ' -c \"db2 connect to ' + dbname + '>/dev/null ;db2  -x \"select tbsp_name,tbsp_total_size_kb,\
    tbsp_total_pages,tbsp_type,tbsp_content_type,tbsp_state from sysibmadm.tbsp_utilization with ur\";exit\"'
    data_cktbs = subprocess.Popen(cmd_cktbs,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if data_cktbs.find('SQLSTATE=') != -1:
        logging.error('There are something error:')
        logging.error(data_cktbs)
        sys.exit(2)
    else:
        list_tbstype=[]
        dict_tbstype={}
        for line_cktbs in data_cktbs.split('\n'):
            if line_cktbs:
                split_data_cktbs=''.join(line_cktbs).split()
                if split_data_cktbs[5] != 'NORMAL':
                    tbs_stat={'tbs_stat':'no'}
                else:
                    tbs_stat={'tbs_stat':'yes'}
                if (split_data_cktbs[4] == 'REGULER' and split_data_cktbs[2] <=regutbsmaxpage)  or (split_data_cktbs[4] == 'LARGE' and split_data_cktbs[2] <=largtbsmaxpage):
                    tbs_maxlimit={'tbs_maxlimit':'yes'}
                else:
                    tbs_maxlimit={'tbs_maxlimit':'no'}
                list_tbstype.append(split_data_cktbs[4])
        dict_tbstype['tbs_type']=list_tbstype
        tbs_info=dict(tbs_stat.items()+tbs_maxlimit.items()+dict_tbstype.items())                
        return tbs_info

def get_aix_dbcat(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db catalog info:')
    cmd_dbcatalog = 'su - ' + instname + ' -c \" db2 list db directory;exit\"'
    data_dbcatalog =subprocess.Popen(cmd_dbcatalog,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].replace(' ','')
    dict_dbcatalog={}
    if data_dbcatalog.find(dbname.upper()) != -1 and data_dbcatalog.find('SQLSTATE=') == -1:
        dict_dbcatalog['dbcat_data']=data_dbcatalog
    else:
        dict_dbcatalog['dbcat_data']='Error'
    return dict_dbcatalog

def get_aix_nodecat(instname):
    instname=instname.lower().strip()
    logging.info('Begin to check node catalog info:')
    cmd_ndcatalog = 'su - ' + instname + ' -c \" db2 list node directory;exit\"'
    data_ndcatalog =subprocess.Popen(cmd_ndcatalog,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].replace(' ','')
    dict_ndcatalog={}
    dict_ndcatalog['nodecat_data']=data_ndcatalog
    return dict_ndcatalog


def get_aix_db_fedstat(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db fed info:')
    cmd_getfedstatus = 'su - ' + instname + ' -c \" db2look -d ' + dbname + '-e -fedonly ;exit\"'
    data_getfedstatus =subprocess.Popen(cmd_getfedstatus,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if data_getfedstatus.find('CREATE NICKNAME')!= -1:
#        nickcount=data_getfedstatus.count('CREATE NICKNAME')
        dict_getfedstatus={'fed_config':'yes'}   
    else:
        dict_getfedstatus={'fed_config':'no'}
    return dict_getfedstatus

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
        dict_get_db2sysc = get_aix_db2sysc(instname)
        dict_get_dbcon = get_aix_dbcon(instname,dbname)
        dict_get_tbsinfo = get_aix_dbtbsinfo(instname,dbname)
        dict_get_dbcat = get_aix_dbcat(instname,dbname)
        dict_get_nodecat = get_aix_nodecat(instname)
        dict_get_fedstat = get_aix_db_fedstat(instname,dbname)
        dict_data_result = dict(dict_get_db2sysc.items()+dict_get_dbcon.items()+dict_get_tbsinfo.items()+dict_get_dbcat.items()+dict_get_nodecat.items()+dict_get_fedstat.items())
        print json.dumps(dict_data_result)
