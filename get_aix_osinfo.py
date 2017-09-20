#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,time,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_osinfo.log',
                filemode='w')
def Usage():
    print 'get_aix_osinfo usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-p,--port::<port>'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:p:', ["help","hostname=","instname=","port="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit()
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
            elif op in ('-p','--port'):
                port=ar
            else:
                logging.error("Error: invalid parameters")
                Usage()
                sys.exit()


def transtoarray(data):
    info=[]
    for i in data.split('\n\n'):
        for x in i.splitlines():
            if x:
                info.append(x)
    return info 

def get_aix_osinfo():
    logging.info("Begin to get osinfo:")
    Data_get_oslevel = subprocess.Popen('oslevel -s',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if Data_get_oslevel[0] not in ('7','6'):
        Data_get_oslevel = 'Error'
        logging.info("oslevel is not in 7.1 or 6.1")
    else:
        Data_get_oslevel = Data_get_oslevel
    Data_get_memsize = subprocess.Popen('lsattr -El mem0 -a goodsize -F value',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    Data_get_numproc = subprocess.Popen('lsdev -Sa -Cc processor|awk \'END{print NR}\'',stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()[0]
    Data_get_clevel = subprocess.Popen('lslpp -l|grep -i xlc.rte',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].split()
    Data_get_jdklevel= subprocess.Popen('java -version',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[1]
    Data_get_timezone = subprocess.Popen('echo $TZ',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    Data_get_nowtime = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    Data_get_pgspace = subprocess.Popen('lsps -as|grep -i MB',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('MB','').split()
    Dict_osinfo = {'oslevel':Data_get_oslevel[0:10].strip(),'memsize':Data_get_memsize.strip(),'numproc':Data_get_numproc.strip(),\
                   'clevel':Data_get_clevel[1],'timezone':Data_get_timezone.strip(),'nowtime':Data_get_nowtime.strip(),\
                   'pgspace':Data_get_pgspace[0],'jdklevel':Data_get_jdklevel.replace('"','').split()[2]}
    logging.info("osinfo is collected complete!")
    return Dict_osinfo


def get_aix_hostsinfo():
    logging.info("Begin to get hostsinfo:")
    Dict_final_hsinfo={}
    Dict_hosts_info={}
    Data_hostsinfo = subprocess.Popen('cat /etc/hosts',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0] 
    Data_mid_hostsinfo = re.sub('#.*|.*local.*','',Data_hostsinfo)
    List_hostsinfo=[]
    for Line_hostsinfo in Data_mid_hostsinfo.split('\n'):
        if Line_hostsinfo:
            List_hostsinfo.append(Line_hostsinfo)
    Dict_final_hsinfo['hostinfo']=List_hostsinfo
    logging.info("hostsinfo is collected complete!")
    return Dict_final_hsinfo

def get_db2port_info(instname,port):
    logging.info("Begin to get db2 portinfo:")
    instname=instname.lower()
    Dict_db2_portinfo={}
    Dict_final_db2port={}
    Cmd_get_db2port = 'cat /etc/services|grep -i ' + instname.strip() + '|grep -i '+ port.strip()
    Data_get_db2port = subprocess.Popen(Cmd_get_db2port,stdout=subprocess.PIPE, shell=True).communicate()[0].replace(' ','')
##    List_get_db2port = transtoarray(Data_get_db2port)
#    for Line_get_db2port in List_get_db2port:
#        k, v = [x.strip() for x in Line_get_db2port.split()]
#        Dict_db2_portinfo[k] = v
#    Dict_final_db2port['db2portinfo']=Dict_db2_portinfo
    Dict_final_db2port['db2portinfo']=Data_get_db2port
    logging.info("db2 portinfo is collected complete!")
    return Dict_final_db2port

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    instname=sys.argv[4]
    port=sys.argv[6]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        Dict_get_osinfo=get_aix_osinfo()
        Dict_get_hostsinfo=get_aix_hostsinfo()
        Dict_get_db2port=get_db2port_info(instname,port)
        dict_data_result=dict(Dict_get_osinfo.items()+Dict_get_hostsinfo.items()+Dict_get_db2port.items())
        print json.dumps(dict_data_result)
