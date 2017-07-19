#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,re,sys,getopt,socket,json,logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_sysparm.log',
                filemode='w')

def Usage():
    print 'get_aix_sysparm usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'

def main(argv):
    hostname=""

    try:
        opts, args = getopt.getopt(argv[1:], 'ho:', ["help","hostname="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=3):
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
            else:
                logging.error("Error: invalid parameters")
                Usage()
                sys.exit()

def sub_dict(form_dict, sub_keys, default=None):
    return dict([(k, form_dict.get(k.strip(), default)) for k in sub_keys.split(',')])

def transtoarray(data):
    info=[]
    for i in data.split('\n\n'):
        for x in i.splitlines():
            if x:
                info.append(x)
    return info 

def get_aix_syscfg():
    logging.info("Begin to get syscfg:")
    syscfgcmd = 'lsattr -El sys0|grep -i maxuproc'
    sysdata = subprocess.Popen(syscfgcmd,stdout=subprocess.PIPE, shell=True).communicate()[0] 
    if sysdata.find("maxuproc") != -1:
        sysdata1 = sysdata.split()
        sysinfo = {}
        sysinfo['maxproc']=''.join(sysdata1[1])
        logging.info("Success to get syscfg End!")
        return sysinfo
    else:
        logging.info("sysdata is wrong,please check output")
        retcode=-1
        return retcode

def get_aix_vmocfg():
    logging.info("Begin to get vmoinfo:")
    vmo_info={}
    vmodata = subprocess.Popen('vmo -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if vmodata.find("minfree =") != -1:
        vmolist = transtoarray(vmodata)
        for vmoline in vmolist:
            key, value = [x.strip() for x in vmoline.split('=')]
            vmo_info[key] = value
        vmoinfo=sub_dict(vmo_info, 'minfree,maxfree,minperm%,maxperm%,maxclient%,strict_maxclient,strict_maxperm,lru_file_repage,v_pinshm,maxperm%')
        logging.info("Success to get vmocfg End!")
        return vmoinfo
    else:
        logging.info("vmoinfo is wrong,please check output")
        retcode=-1
        return retcode    


def get_aix_nocfg():
    logging.info("Begin to get noinfo:")
    no_info={}
    nodata = subprocess.Popen('no -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]    
    if nodata.find(" = ") != -1:
        nolist = transtoarray(nodata)
        for noline in nolist: 
            k, v = [x.strip() for x in noline.split('=')]
            no_info[k] = v
        noinfo=sub_dict(no_info, 'sb_max,rfc1323,tcp_sendspace,tcp_recvspace,udp_sendspace,udp_recvspace,ipqmaxlen,somaxconn,tcp_keepidle,tcp_keepcnt,tcp_keepintvl,clean_partial_connection,ip6srcrouteforward,ipignoreredirects,ipsendredirects,ipsrcrouterecv,tcp_nagle_limit,tcp_nodelayack,tcp_tcpsecure')
        logging.info("Success to get nocfg End!")
        return noinfo
    else:
        logging.info("noinfo is wrong,please check output")
        retcode=-1
        return retcode

def get_aix_ioocfg():
    logging.info("Begin to get iooinfo:")
    ioo_cfg={}
    ioodata = subprocess.Popen('ioo -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if ioodata.find(" = ") != -1:
        ioolist = transtoarray(ioodata)
        for iooline in ioolist: 
            k, v = [x.strip() for x in iooline.split('=')]
            ioo_cfg[k] = v
        iooinfo=sub_dict(ioo_cfg, 'j2_maxPageReadAhead,j2_maxRandomWrite,j2_minPageReadAhead,maxpgahead,minpgahead,maxrandwrt,j2_nBufferPerPagerDevice,numfsbufs,j2_nPagesPerWriteBehindCluster,pv_min_pbuf,sync_release_ilock')
        logging.info("Success to get ioocfg End!")
        return iooinfo
    else:
        logging.info("iooinfo is wrong,please check output")
        retcode=-1
        return retcode

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        p1=get_aix_syscfg()
        p2=get_aix_vmocfg()
        p3=get_aix_nocfg()
        p4=get_aix_ioocfg()
        if p1 == -1 or p2==-1 or p3==-1 or p4==-1:
            print "output is wrong!"
        else:
            pdata=dict(p1.items()+p2.items()+p3.items()+p4.items())
            print json.dumps(pdata)
