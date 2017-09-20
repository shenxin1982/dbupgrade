#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,re,json,logging


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_vginfo.log',
                filemode='w')

def Usage():
    print 'get_aix_vginfo usage:  '
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

def get_aix_rootvgmir():
    cmd_rootvgmir = 'lsvg -l rootvg |grep \"/\"|awk \'{print $5}\'|uniq'
    data_rootvgmir = subprocess.Popen(cmd_rootvgmir,stdout=subprocess.PIPE, shell=True).communicate()[0]
    if int(data_rootvgmir) == 1:
        dict_rootvgmir ={'rootvgmir':'no'}
    else:
        dict_rootvgmir ={'rootvgmir':'yes'}
    return dict_rootvgmir

def get_aix_vginfo():
    data_actvgname = subprocess.Popen('lsvg -o',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    list_vgstate=[]
    list_vgsize=[]
    list_vgname=[]
    for vgname in data_actvgname.split('\n'):
        if vgname:
            cmd_get_vginfo = 'lsvg '+ vgname
            data_get_vginfo = subprocess.Popen(cmd_get_vginfo,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('megabytes)','MB').replace('(','')
            list_get_vginfo = data_get_vginfo.split()
            list_vgname.append(vgname)
            list_vgstate.append(list_get_vginfo[8])
            list_vgsize.append(list_get_vginfo[19])
    dict_vginfo = {'vgname':list_vgname,'vgstat':list_vgstate,'vgsize':list_vgsize}
    return dict_vginfo



if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        dict_get_rootvgmir = get_aix_vginfo()
        dict_vginfo = get_aix_rootvgmir()
        dict_data_result = dict(dict_get_rootvgmir,**dict_vginfo)
        print json.dumps(dict_data_result)


