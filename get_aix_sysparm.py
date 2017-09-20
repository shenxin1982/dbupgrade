#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging

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
    cmd_syscfg = 'lsattr -El sys0|grep -i maxuproc'
    data_syscfg = subprocess.Popen(cmd_syscfg,stdout=subprocess.PIPE, shell=True).communicate()[0] 
    if data_syscfg.find("maxuproc") != -1:
        split_data_syscfg = data_syscfg.split()
        dict_syscfg = {}
        dict_syscfg['maxuproc']=''.join(split_data_syscfg[1])
        logging.info("Success to get syscfg End!")
        return dict_syscfg
    else:
        logging.info("sysdata is wrong,please check output")
        sys.exit(2)

def get_aix_vmocfg():
    logging.info("Begin to get vmoinfo:")
    dict_vmo_info={}
    dict_mid_vmoinfo={}
    data_vmo_data = subprocess.Popen('vmo -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if data_vmo_data.find("minfree =") != -1:
        list_vmo_data = transtoarray(data_vmo_data)
        for line_vmo_data in list_vmo_data:
            key, value = [x.strip() for x in line_vmo_data.split('=')]
            dict_vmo_info[key] = value
        Data_get_oslevel = subprocess.Popen('oslevel -s',stdout=subprocess.PIPE, shell=True).communicate()[0]
        if Data_get_oslevel[0] in ('5','6'):
            dict_vmoinfo=sub_dict(dict_vmo_info, 'minfree,maxfree,minperm%,maxperm%,maxclient%,strict_maxclient,strict_maxperm,lru_file_repage,v_pinshm,maxperm%')
        else:
            dict_mid_vmoinfo=sub_dict(dict_vmo_info, 'minfree,maxfree,minperm%,maxperm%,maxclient%,strict_maxclient,strict_maxperm,v_pinshm,maxperm%')
            dict_lrufilerepage={'lru_file_repage':'0'}
            dict_vmoinfo=dict(dict_mid_vmoinfo.items()+dict_lrufilerepage.items())
        logging.info("Success to get vmocfg End!")
        return dict_vmoinfo
    else:
        logging.info("vmoinfo is wrong,please check output")
        sys.exit(2)

def get_aix_nocfg():
    logging.info("Begin to get noinfo:")
    dict_no_info={}
    data_no_info = subprocess.Popen('no -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]    
    if data_no_info.find(" = ") != -1:
        list_no_info = transtoarray(data_no_info)
        for line_no_info in list_no_info: 
            k, v = [x.strip() for x in line_no_info.split('=')]
            dict_no_info[k] = v
        dict_noinfo=sub_dict(dict_no_info, 'sb_max,rfc1323,tcp_sendspace,tcp_recvspace,udp_sendspace,udp_recvspace,ipqmaxlen,somaxconn,tcp_keepidle,tcp_keepcnt,tcp_keepintvl,tcp_keepinit')
        logging.info("Success to get nocfg End!")
        return dict_noinfo
    else:
        logging.info("noinfo is wrong,please check output")
        sys.exit(2)

def get_aix_ioocfg():
    logging.info("Begin to get iooinfo:")
    dict_ioo_cfg={}
    data_ioo_cfg = subprocess.Popen('ioo -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if data_ioo_cfg.find(" = ") != -1:
        list_ioo_cfg = transtoarray(data_ioo_cfg)
        for line_ioo_cfg in list_ioo_cfg: 
            k, v = [x.strip() for x in line_ioo_cfg.split('=')]
            dict_ioo_cfg[k] = v
        dict_iooinfo=sub_dict(dict_ioo_cfg, 'j2_maxPageReadAhead,j2_maxRandomWrite,j2_minPageReadAhead,maxpgahead,minpgahead,maxrandwrt,j2_nBufferPerPagerDevice,numfsbufs,j2_nPagesPerWriteBehindCluster,pv_min_pbuf,sync_release_ilock')
        logging.info("Success to get ioocfg End!")
        return dict_iooinfo
    else:
        logging.info("iooinfo is wrong,please check output")
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        dict_get_maxuproc=get_aix_syscfg()
        dict_get_vmocfg=get_aix_vmocfg()
        dict_get_nocfg=get_aix_nocfg()
        dict_get_ioocfg=get_aix_ioocfg()
        dict_data_result=dict(dict_get_maxuproc.items()+dict_get_vmocfg.items()+dict_get_nocfg.items()+dict_get_ioocfg.items())
        print json.dumps(dict_data_result)
