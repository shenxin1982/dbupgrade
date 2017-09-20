#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbauth.log',
                filemode='w')

def Usage():
    print 'get_aix_dbauth usage:  '
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



def get_aix_dbauth(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db object info:')

    Sql_select_dbauth='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select GRANTOR,GRANTORTYPE,GRANTEE,GRANTEETYPE,BINDADDAUTH,CONNECTAUTH,CREATETABAUTH,DBADMAUTH,EXTERNALROUTINEAUTH,IMPLSCHEMAAUTH,LOADAUTH,NOFENCEAUTH,QUIESCECONNECTAUTH,LIBRARYADMAUTH,SECURITYADMAUTH,SQLADMAUTH,WLMADMAUTH,EXPLAINAUTH,DATAACCESSAUTH,ACCESSCTRLAUTH,CREATESECUREAUTH from syscat.dbauth with ur\";exit\"'
#    Sql_select_dbauth='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select grantee from syscat.dbauth with ur\";exit\"'    

    Str_Data_dbauth =subprocess.Popen(Sql_select_dbauth,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].replace(' ','')
    List_Data_dbauth = transtoarray(Str_Data_dbauth)
    Dict_dbauth_info = {'dbauth_info':List_Data_dbauth}
    return Dict_dbauth_info


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
        dict_data_result = get_aix_dbauth(instname,dbname)
        print json.dumps(dict_data_result)
