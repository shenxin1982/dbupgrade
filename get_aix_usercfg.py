#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,sys,getopt,socket,json,logging,re

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/get_aix_usercfg.log',
                filemode='w')


def Usage():
    print 'get_aix_usercfg usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-u,--instname::<instname>'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:', ["help","hostname=","instname="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=5):
        Usage()
        sys.exit()
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif op in ('-o','--hostname'):
                hostname=ar
            elif op in ('-u','--instname'):
                instname=ar
            else:
                logging.error('Error: invalid parameters')
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


def get_aix_userlist():
    list_username = []
    cmd_get_usrname = 'cat /etc/passwd'
    data_usrname = subprocess.Popen(cmd_get_usrname,stdout=subprocess.PIPE, shell=True).communicate()[0]
    for line_usrname in data_usrname.split('\n'):
        list_line_usrname = [x for x in line_usrname.split(':')]
        if list_line_usrname[0] not in ('root','daemon','bin','sys','adm','uucp','guest','nobody','lpd','lp','invscout','snapp','ipsec','nuucp','pconsole','esaadmin','srvproxy','sshd'):
            list_username.append(list_line_usrname[0])
    return list_username

def get_aix_usercfg(username):
    dict_get_usrcfg={}
    cmd_get_usrcfg='lsuser -f '+username+'|grep -v '+username+":"
    data_get_usrcfg = subprocess.Popen(cmd_get_usrcfg,stdout=subprocess.PIPE, shell=True).communicate()[0]
    data1_get_usrcfg = 'uname='+username+'\n'+data_get_usrcfg
    data2_get_usrcfg = re.sub('#.*','',data1_get_usrcfg)
    list_get_usrcfg = transtoarray(data2_get_usrcfg)
    for line_get_usrcfg in list_get_usrcfg: 
        k, v = [x.strip() for x in line_get_usrcfg.split('=')]
        dict_get_usrcfg[k] = v
    dict_userinfo=sub_dict(dict_get_usrcfg,'uname,id,pgrp,home,shell,expires,fsize,cpu,data,stack,rss,nofiles,fsize_hard,cpu_hard,data_hard,stack_hard,rss_hard,nofiles_hard,capabilities')
    grpname = dict_userinfo.get('pgrp')
    cmd_get_grpname = 'lsgroup -f ' + grpname +'|grep -v '+grpname+":"
    data_grpname = subprocess.Popen(cmd_get_grpname,stdout=subprocess.PIPE, shell=True).communicate()[0].replace('id','groupid')
    list_grpname = transtoarray(data_grpname)
    dict_grp_cfg={}
    for line_grpname in list_grpname:
        k, v = [x.strip() for x in line_grpname.split('=')]
        dict_grp_cfg[k] = v
    grpinfo=sub_dict(dict_grp_cfg,'groupid')
    
    return dict(dict_userinfo.items()+grpinfo.items())

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
    usrname_list=get_aix_userlist()
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        uname_userlist=[]
        id_userlist=[]
        pgrp_userlist=[]
        grpid_userlist=[]
        home_userlist=[]
        shell_userlist=[]
        expires_userlist=[]
        fsize_userlist=[]
        cpu_userlist=[]
        data_userlist=[]
        stack_userlist=[]
        rss_userlist=[]
        nofiles_userlist=[]
        capabilities_userlist=[]
        fsize_hard_userlist=[]
        cpu_hard_userlist=[]
        data_hard_userlist=[]
        stack_hard_userlist=[]
        rss_hard_userlist=[]
        nofiles_hard_userlist=[]
        for usrname in usrname_list:
            if usrname:
                userdict=get_aix_usercfg(usrname)
                uname_userlist.append(userdict['uname'])
                id_userlist.append(userdict['id'])
                pgrp_userlist.append(userdict['pgrp'])
                grpid_userlist.append(userdict['groupid'])
                expires_userlist.append(userdict['expires'])
                home_userlist.append(userdict['home'])
                shell_userlist.append(userdict['shell'])
                if userdict['shell']!='/usr/bin/ksh':
                    shell_userlist.append(userdict['uname'])
                else:
                    shell_userlist.append(userdict['shell']) 
                if userdict['fsize']!='-1':
                    fsize_userlist.append(userdict['uname'])
                else:
                    fsize_userlist.append(userdict['fsize'])
                if userdict['cpu']!='-1':
                    cpu_userlist.append(userdict['uname'])
                else:
                    cpu_userlist.append(userdict['cpu'])               
                if userdict['data']!='-1':
                    data_userlist.append(userdict['uname'])
                else:
                    data_userlist.append(userdict['data'])    
                if userdict['stack']!='-1':
                    stack_userlist.append(userdict['uname'])
                else:
                    stack_userlist.append(userdict['stack'])                        
                if userdict['rss']!='-1':
                    rss_userlist.append(userdict['uname'])
                else:
                    rss_userlist.append(userdict['rss'])    
                if userdict['nofiles']!='-1':
                    nofiles_userlist.append(userdict['uname'])
                else:
                    nofiles_userlist.append(userdict['nofiles'])    
                if userdict['fsize_hard']!='-1':
                    fsize_hard_userlist.append(userdict['uname'])
                else:
                    fsize_hard_userlist.append(userdict['fsize_hard'])
                if userdict['cpu_hard']!='-1':
                    cpu_hard_userlist.append(userdict['uname'])
                else:
                    cpu_hard_userlist.append(userdict['cpu_hard'])               
                if userdict['data_hard']!='-1':
                    data_hard_userlist.append(userdict['uname'])
                else:
                    data_hard_userlist.append(userdict['data_hard'])    
                if userdict['stack_hard']!='-1':
                    stack_hard_userlist.append(userdict['uname'])
                else:
                    stack_hard_userlist.append(userdict['stack_hard'])                        
                if userdict['rss_hard']!='-1':
                    rss_hard_userlist.append(userdict['uname'])
                else:
                    rss_hard_userlist.append(userdict['rss_hard'])    
                if userdict['nofiles_hard']!='-1':
                    nofiles_hard_userlist.append(userdict['uname'])
                else:
                    nofiles_hard_userlist.append(userdict['nofiles_hard'])   
                if userdict['capabilities']!='CAP_BYPASS_RAC_VMM,CAP_PROPAGATE':
                    capabilities_userlist.append(userdict['uname'])
                else:
                    capabilities_userlist.append(userdict['capabilities'])    

        dict_data_result={'uname':uname_userlist,'id':id_userlist,'pgrp':pgrp_userlist,'groupid':grpid_userlist,\
                          'home':home_userlist,'shell':check_list_value(shell_userlist,'/usr/bin/ksh'),\
                          'expires':expires_userlist,'fsize':check_list_value(fsize_userlist,'-1'),\
                          'cpu':check_list_value(cpu_userlist,'-1'),'data':check_list_value(data_userlist,'-1'),\
                          'stack':check_list_value(stack_userlist,'-1'),'rss':check_list_value(rss_userlist,'-1'),\
                          'nofiles':check_list_value(nofiles_userlist,'-1'),'fsize_hard':check_list_value(fsize_hard_userlist,'-1'),\
                          'cpu_hard':check_list_value(cpu_hard_userlist,'-1'),'data_hard':check_list_value(data_hard_userlist,'-1'),\
                          'stack_hard':check_list_value(stack_hard_userlist,'-1'),'rss_hard':check_list_value(rss_hard_userlist,'-1'),\
                          'nofiles_hard':check_list_value(nofiles_hard_userlist,'-1'),\
                          'capabilities':check_list_value(capabilities_userlist,'CAP_BYPASS_RAC_VMM,CAP_PROPAGATE')}
        print json.dumps(dict_data_result)
