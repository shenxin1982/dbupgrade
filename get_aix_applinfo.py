#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_applinfo.log',
                filemode='w')

def Usage():
    print 'get_aix_applinfo usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-d,--dbname::<dbname>'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:d:p:v:', ["help","hostname=","instname=","dbname="])
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


def get_aix_applstatus(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db con status:')
    list_applstatus=[]
    cmd_applstatus = 'su - ' + instname + ' -c \" db2 list applications ;exit\"'
    data_applstatus =subprocess.Popen(cmd_applstatus,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if data_applstatus.find('SQLSTATE=') != -1:
        logging.error('There are something error:')
        logging.error(data_applstatus)
        sys.exit(2)
    elif data_applstatus.find('SQL1611W') != -1:
        dict_appl_count={'appl_con':'0','appl_info':'0'}
    else:
        for line_applstatus in data_applstatus.split('\n'):
            if line_applstatus.find(dbname.upper()) != -1:
                list_applstatus.append(line_applstatusreplace(' ','')
        length_applinfo=str(len(list_applstatus))
        dict_appl_count={'appl_con':length_applinfo,'appl_info':list_applstatus}

    return dict_appl_count


if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2].upper()
    instname=sys.argv[4].upper()
    dbname=sys.argv[6].upper()
    lhostname=socket.gethostname().upper()
    if lhostname!=hostname:
        logging.error("error hostname")
        sys.exit()
    else:
        dict_data_result = get_aix_applstatus(instname,dbname)
#        dict_get_applstatus = get_aix_applstatus(instname,dbname)
#        dict_data_result = dict(dict_get_fedstat.items()+dict_get_applstatus.items())
        print json.dumps(dict_data_result)
        
