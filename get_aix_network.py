#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_dbfs.log',
                filemode='w')

def Usage():
    print 'get_aix_network usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:', ["help","hostname="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=3):
        logging.error("The input paramters length is not correct!")
        Usage()
        sys.exit(2)
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(2)
            elif op in ('-o','--hostname'):
                hostname=ar
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



def get_aix_network():
    logging.info('begin to get network info:')
    Cmd_network_one_get_network = 'ifconfig -l'
    Data_get_network = subprocess.Popen(Cmd_network_one_get_network, stdout=subprocess.PIPE, shell=True).communicate()[0].replace(' ','\n').split('\n')
#    (status, output) = commands.getstatusoutput(Cmd_network_one_get_network)
#    Data_get_network = output.replace(' ','\n').split('\n')
    List_ipaddress=[]
    List_tcpsend=[]
    List_tcprecv=[]
    List_rfc=[]

    for Line_network_data in Data_get_network: 
        if Line_network_data and not Line_network_data.startswith('lo'):
            Cmd_network_one = 'ifconfig ' + Line_network_data
            Data_network_one = subprocess.Popen(Cmd_network_one, stdout=subprocess.PIPE, shell=True).communicate()[0].replace('\n','').replace('\t','').split(' ')
            List_ipaddress.append(Data_network_one[2])
                        
            if Data_network_one[8]!='1048576':
                List_tcpsend.append(Data_network_one[2])
            else:
                List_tcpsend.append(Data_network_one[8])
            if Data_network_one[10]!='1048576':
                List_tcprecv.append(Data_network_one[2])
            else:
                List_tcprecv.append(Data_network_one[10])
            if Data_network_one[12]!='1':
                List_rfc.append(Data_network_one[2])
            else:
                List_rfc.append(Data_network_one[12])               

    Dict_network_info={'ipaddr':List_ipaddress,'tcp_sendspace':check_list_value(List_tcpsend,'1048576'),'tcp_recvspace':check_list_value(List_tcprecv,'1048576'),'rfc1323':check_list_value(List_rfc,'1')}

    logging.info('Successful to get network info')
    return Dict_network_info


def check_list_value(listname,value):
    list_error_value=[]
    for i in range(len(listname)):
        if listname[i]!=value:
            list_error_value.append(listname[i])
    if len(list_error_value)!=0:            
        return list_error_value
    else:
        return value

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        dict_data_result=get_aix_network()
        print json.dumps(dict_data_result)
