#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbobject.log',
                filemode='w')

def Usage():
    print 'get_aix_dbobject usage:  '
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



def get_aix_dbobject(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db object info:')

    Sql_select_procedure='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select procschema,procname from syscat.procedures with ur\";exit\"'
    Sql_select_function='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select funcschema,funcname from syscat.functions with ur\";exit\"'
    Sql_select_package='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select pkgschema,pkgname from syscat.packages with ur\";exit\"'
    Sql_select_table='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select tabschema,tabname,type from syscat.tables  with ur\";exit\"'

    Str_Data_procudure =subprocess.Popen(Sql_select_procedure,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    Str_Data_function =subprocess.Popen(Sql_select_function,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    Str_Data_package =subprocess.Popen(Sql_select_package,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    Str_Data_table =subprocess.Popen(Sql_select_table,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')

    List_table_data=[]
    for Line_table_data in Str_Data_table:
        if Line_table_data:
            Split_table_data = ''.join(Line_table_data).split()
            Table_sys_data = ''.join(Split_table_data[0])[0:3]
            if Table_sys_data != 'SYS' and Split_table_data[2] == 'T':
                Str_table_line=''.join(Split_table_data)
                List_table_data.append(Str_table_line)
    Dict_table_count = {'tb_count':str(len(List_table_data))}
    
    List_proc_data = []
    for Line_proc_data in Str_Data_procudure:
        if Line_proc_data: 
            Split_str_proc_data = ''.join(Line_proc_data).split()
            Proc_sys_data = ''.join(Split_str_proc_data[0])[0:3]
            if Proc_sys_data != 'SYS':
                Str_proc_line=''.join(Split_str_proc_data) 
                List_proc_data.append(Str_proc_line)
    Dict_proc_count = {'proc_count':str(len(List_proc_data))}

    List_Func_data = []
    for Line_func_data in Str_Data_function:
        if Line_func_data:
            Split_str_fun_data = ''.join(Line_func_data).split()
            Func_sys_data = ''.join(Split_str_fun_data[0])[0:3]
            if Func_sys_data != 'SYS':
                Str_fun_line=''.join(Split_str_fun_data)
                List_Func_data.append(Str_fun_line)
    Dict_func_count = {'func_count':str(len(List_Func_data))}

    List_pkg_data = []
    for Line_pkg_data in Str_Data_package:
        if Line_pkg_data:
            Split_str_pkg_data = ''.join(Line_pkg_data).split()
            Pkg_str_data =''.join(Split_str_pkg_data[0])
            Package_sys_data = Pkg_str_data[0:3]
            Package_nullid_data = Pkg_str_data[0:6]
            if Package_sys_data != 'SYS' and Package_nullid_data != 'NULLID':
                Str_pkg_line=''.join(Split_str_pkg_data)
                List_pkg_data.append(Str_pkg_line)
    Dict_pkg_data = {'pakg_count':str(len(List_pkg_data))}

    Dict_final_data=dict(Dict_proc_count.items()+Dict_func_count.items()+Dict_pkg_data.items()+Dict_table_count.items())
    return Dict_final_data


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
        dict_data_result = get_aix_dbobject(instname,dbname)
        print json.dumps(dict_data_result)
