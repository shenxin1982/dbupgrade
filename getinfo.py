#!/usr/bin/env python
# encoding: utf-8
# -*- coding: utf8 -*
import subprocess,os,re,sys,getopt,socket,json,logging,time,commands

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/getinfo.log',
                filemode='w')
sysparm_value_dict={'minfree':'8192','maxfree':'8704','minperm%':'5','maxperm%':'10','maxclient%':'10','maxuproc':'4096','sb_max':'1310720','rfc1323':'1','tcp_sendspace':'1048576','tcp_recvspace':'1048576','udp_sendspace':'262144','udp_recvspace':'262144','ipqmaxlen':'250','somaxconn':'1024','tcp_keepidle':'300','tcp_keepcnt':'5','tcp_keepintvl':'12','tcp_keepinit':'120','clean_partial_conns':'1','ip6srcrouteforward':'0','ipignoreredirects':'1','ipsendredirects':'0','ipsrcrouterecv':'1','tcp_nagle_limit':'1','tcp_nodelayack':'1','tcp_tcpsecure':'5','strict_maxclient':'1','strict_maxperm':'1','lru_file_repage':'0','v_pinshm':'1','j2_maxPageReadAhead':'128','j2_maxRandomWrite':'0','j2_minPageReadAhead':'2','maxpgahead':'8','minpgahead':'2','maxrandwrt':'0','j2_nBufferPerPagerDevice':'512','numfsbufs':'196','j2_nPagesPerWriteBehindCluster':'32','pv_min_pbuf':'512','sync_release_ilock':'0'}
usrparm_value_dict={'fsize':'-1','cpu':'-1','data':'-1','stack':'-1','rss':'-1','nofiles':'-1','fsize_hard':'-1','cpu_hard':'-1','data_hard':'-1','stack_hard':'-1','rss_hard':'-1','nofiles_hard':'-1','capabilities':'CAP_BYPASS_RAC_VMM,CAP_PROPAGATE'}
fsparm_value_dict={'dbhomepath':'/db/dbhome','managepath':'/db/manage','dbdiagpath':'/db/dbdiag','actlogpath':'/db/actlog','mirlogpath':'/db/mirlog','dbdatapath':'/db/dbdata','archm1path':'/db/archm1','archm2path':'/db/archm2','dbhomefstype':'jfs2','dbdiagstype':'jfs2','managefstype':'jfs2','dbdatastype':'jfs2','actlogfstype':'jfs2','mirlogfstype':'jfs2','archm1fstype':'jfs2','archm2fstype':'jfs2'}
ifparm_value_dict={'rfc1323':'1','tcp_sendspace':'1048576','tcp_recvspace':'1048576'}
db2set_vaule_dict={'DB2_LOAD_COPY_NO_OVERRIDE':'NONRECOVERABLE','DB2_MAX_GLOBAL_SNAPSHOT_SIZE':'20971520','DB2_USE_ALTERNATE_PAGE_CLEANING':'ON','DB2_LOGGER_NON_BUFFERED_IO':'ON','DB2_TRUST_MDC_BLOCK_FULL_HINT':'YES','DB2_MDC_ROLLOUT':'DEFER','DB2_EVALUNCOMMITTED':'ON','DB2_SKIPINSERTED':'ON','DB2SOSNDBUF':'1048576','DB2SORCVBUF':'1048576','DB2_ANTIJOIN':'YES','DB2_PARALLEL_IO':'*','DB2COMM':'TCPIP','DB2AUTOSTART':'YES','DB2CODEPAGE':'1386','DB2_HADR_SOSNDBUF':'1048576','DB2_HADR_SORCVBUF':'1048576','DB2_HADR_PEER_WAIT_LIMIT':'1','DB2_HADR_ROS':'ON','DB2_STANDBY_ISO':'UR'}




def Usage():
    print 'getinfo.py usage:  '
    print '-h,--help: print help message.'
    print '-o,--hostname::<hostname>'
    print '-i,--instname::<instname>'
    print '-d,--dbname::<dbname>'
    print '-p,--port::<port>'
    print '-v,--version::<version>'
    print '-m,--parameter::<osinfo,sysparm,dbinfo,dbfsinfo,db2set,dbmcfg,dbcfg,ckprod,vginfo,network,userinfo,dbstat,dbobject,suggest,result>'
    print 'osinfo : get os info like oslevel,xlclevel etc.'
    print 'sysparm : get os  parameter like vmo,ioo,no,maxuproc'
    print 'dbinfo : get dbinfo like dbversion,db catalog info etc.'
    print 'dbfsinfo : get database file system info'
    print 'db2set : get db2set parameter info'
    print 'dbmcfg : get dbm cfg info'
    print 'dbcfg : get db cfg info'
    print 'ckprod: get requeired installed software and crontab'
    print 'vginfo: get vg info'
    print 'network: get network info'
    print 'userinfo: get user info'
    print 'dbstat: get database info'
    print 'dbojbect: get database object info'
    print 'suggest: get all suggest'
    print 'result: get all result'

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'ho:i:d:p:v:m', ["help","hostname=","instname=","dbname=","port=","version=","parameter="])
    except getopt.GetoptError, err:
        logging.error(str(err))
        Usage()
        sys.exit(2)
    if(len(sys.argv)!=13):
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
            elif op in ('-p','--port'):
                port=ar
            elif op in ('-v','--version'):
                version=ar
            elif op in ('-m','--parameter'):
                parameter=ar
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

def get_aix_dbinfo(instname,dbname,version):
    instname = instname.lower().strip()
    dbname = dbname.lower().strip()
    dbversion = version.upper()
    dbversion1 = dbversion.split(".")
    if dbversion1[0] in ('V10','V11'):
        db2level=dbversion[0:5]
    elif dbversion1[0] == 'V9':
        db2level=dbversion[0:4]
    else:
        logging.error("invalid dbversion!")
        retcode=-1
        return retcode
    cmd_suuser= 'su - ' + instname.lower() + ' -c '
    cmd_db2level=' db2level|grep \"DB2 v\" '
    cmd_exit=';exit'
    dbldata = subprocess.Popen(cmd_suuser+cmd_db2level+cmd_exit,stdout=subprocess.PIPE, shell=True).communicate()[0].split(' ')[4]
    dblspld = ''.join(dbldata).split('.')
    dblevel = ''.join(dblspld[0]).upper()+'.'+''.join(dblspld[1])
    if db2level == dblevel:
        ckdbvdict={'ck_dbversion':'Yes'}
    else:
        ckdbvdict={'ck_dbversion':'No'}

    logging.info('Begin to check db2sysc process is exist or not:')
    db2syscmd = 'ps -ef|grep -i db2sysc|grep -i ' + instname.upper().strip() + '|grep -v grep>/dev/null'
    retcode=subprocess.call(db2syscmd,shell=True)
    if retcode == 0: 
        db2sysdict={'db2_process':'Yes'}
    else:
        db2sysdict={'db2_process':'No'}
    logging.info('Check db2sysc process end!')

    logging.info('Begin to check db con status:')
    condbcmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + ';exit\"'
    condbdata =subprocess.Popen(condbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if condbdata.find(' = ') != -1 and condbdata.find('SQLSTATE=') == -1:
        condbdict={'dbcon_stat':'Yes'}
    else:
        condbdict = {'dbcon_stat':'No'}

    logging.info('Begin to check db tbs status:')
    regutbsmaxpage=16777216
    largtbsmaxpage=536870912
    cktbscmd = 'su - ' + instname + ' -c \"db2 connect to ' + dbname + '>/dev/null ;db2  -x \"select tbsp_name,tbsp_total_size_kb,tbsp_total_pages,tbsp_type,tbsp_content_type,tbsp_state from sysibmadm.tbsp_utilization with ur\";exit\"'
    cktbsdata = subprocess.Popen(cktbscmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if cktbsdata.find('SQLSTATE=') != -1:
        logging.error('There are something error:')
        logging.error(cktbsdata)
        sys.exit(2)
    else:
        tbs_typelist=[]
        tbs_typedict={}
        for line in cktbsdata.split('\n'):
            if line:
                tbsdatasp=''.join(line).split()
                if tbsdatasp[5] != 'NORMAL':
                    tbs_stat={'tbs_stat':'No'}
                else:
                    tbs_stat={'tbs_stat':'Yes'}
                if (tbsdatasp[4] == 'REGULER' and tbsdatasp[2] <=regutbsmaxpage)  or (tbsdatasp[4] == 'LARGE' and tbsdatasp[2] <=largtbsmaxpage):
                    tbs_maxlimit={'tbs_maxlimit':'Yes'}
                else:
                    tbs_maxlimit={'tbs_maxlimit':'No'}
                tbs_typelist.append(tbsdatasp[4])
        tbs_typedict['tbs_type']=tbs_typelist
        tbsinfodcit=dict(tbs_stat.items()+tbs_maxlimit.items()+tbs_typedict.items())                

    logging.info('Begin to check db catalog info:')
    catdbcmd = 'su - ' + instname + ' -c \" db2 list db directory;exit\"'
    catdbdata =subprocess.Popen(catdbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    catdbdict={}
    if catdbdata.find(dbname.upper()) != -1 and catdbdata.find('SQLSTATE=') == -1:
        catdbdict['dbcat_data']=catdbdata
    else:
        catdbdict['dbcat_data']='Error'

    logging.info('Begin to check node catalog info:')
    nodedbcmd = 'su - ' + instname + ' -c \" db2 list node directory;exit\"'
    nodedbdata =subprocess.Popen(nodedbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    nodedbdict={}
    nodedbdict['nodecat_data']=nodedbdata

    logging.info('Begin to check db fed info:')
    getfedcmd = 'su - ' + instname + ' -c \" db2look -d ' + dbname + '-e -fedonly ;exit\"'
    getfeddata =subprocess.Popen(getfedcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if getfeddata.find('CREATE NICKNAME')!= -1:
        nickcount=getfeddata.count('CREATE NICKNAME')
        fed_dict={'fed_config':nickcount}   
    else:
        fed_dict={'fed_config':'No'}

    dbinfodict=dict(fed_dict.items()+catdbdict.items()+tbsinfodcit.items()+ckdbvdict.items()+db2sysdict.items()+condbdict.items()+nodedbdict.items())
    return dbinfodict

def check_shell_cmd(checkcmd):
    shelldata=subprocess.Popen(checkcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()
    if shelldata[1]=='':
        finaldata=shelldata[0]
    else:
        finaldata=shelldata[1]
        logging.error(finaldata)
    return finaldata
  
def get_aix_osinfo():
    logging.info("Begin to get osinfo:")
    oslevel = subprocess.Popen('oslevel -s',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    if oslevel[0] not in ('7','6'):
        oslevel = 'Error'
        logging.info("oslevel is not in 7.1 or 6.1")
    else:
        oslevel = oslevel
#    memsize = subprocess.Popen('lsattr -El mem0 -a goodsize -F value',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    cmd_memsize='lsattr -El mem0 -a goodsize -F value'
    memsize = check_shell_cmd(cmd_memsize)
    numproc = subprocess.Popen('lsdev -Sa -Cc processor|awk \'END{print NR}\'',stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True).communicate()[0]
    xlcversion = subprocess.Popen('lslpp -l|grep -i xlc.rte',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].split()
    jdklevel= subprocess.Popen('java -version',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[1]
    timezone = subprocess.Popen('echo $TZ',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    nowtime = time.strftime("%Y-%m-%d %H.%M.%S", time.localtime())
    pgspace = subprocess.Popen('lsps -as|grep -i MB',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('MB','').split()
    osinfo = {'oslevel':oslevel[0:10].strip(),'memsize':memsize.strip(),'numproc':numproc.strip(),'xlcversion':xlcversion[1],'timezone':timezone.strip(),'nowtime':nowtime.strip(),'pgspace':pgspace[0],'jdklevel':jdklevel.replace('"','').split()[2]}

    logging.info("osinfo is collected complete!")

    logging.info("Begin to get hostsinfo:")
    hostsinfodict={}
    hostsdict={}
    hostsdata = subprocess.Popen('cat /etc/hosts|grep -v \"#\"|grep -i "^[0-9]"|awk \'{print $1,\":\",$2,$3,$4}\'',stdout=subprocess.PIPE, shell=True).communicate()[0]
    hostsinfo = transtoarray(hostsdata)
    for i in hostsinfo:
        if i:
            k, v = [x.strip() for x in i.split(':')]
            hostsinfodict[k] = v
    hostsdict['hostinfo']=hostsinfodict
    logging.info("hostsinfo is collected complete!")

    logging.info("Begin to get db2portinfo:")
    db2portinfo={}
    db2portdict={}
    cmd = 'cat /etc/services|grep -i ' + instname.strip()
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
    info = transtoarray(data)
    for i in info:
        k, v = [x.strip() for x in i.split()]
        db2portinfo[k] = v
    db2portdict['db2portinfo']=db2portinfo
    logging.info("db2portinfo is collected complete!")
 
    osinfodict=dict(osinfo.items()+hostsdict.items()+db2portdict.items())
    return osinfodict
              
def get_aix_sysparm():
    logging.info("Begin to get syscfg:")
    sysinfo = {}
    syscfgcmd = 'lsattr -El sys0|grep -i maxuproc'
    sysdata = subprocess.Popen(syscfgcmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
    if sysdata.find("maxuproc") != -1:
        sysdata1 = sysdata.split()
        sysinfo['maxuproc']=''.join(sysdata1[1])
        logging.info("Success to get syscfg End!")
    else:
        logging.info("sysdata is wrong,please check output")
        sys.exit(2)

    logging.info("Begin to get vmoinfo:")
    vmo_info={}
    vmodata = subprocess.Popen('vmo -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if vmodata.find("minfree =") != -1:
        vmolist = transtoarray(vmodata)
        for vmoline in vmolist:
            key, value = [x.strip() for x in vmoline.split('=')]
            vmo_info[key] = value
        vmoinfo=sub_dict(vmo_info, 'minfree,maxfree,minperm%,maxperm%,maxclient%,strict_maxclient,strict_maxperm,lru_file_repage,v_pinshm')
        logging.info("Success to get vmocfg End!")
    else:
        logging.info("sysdata is wrong,please check output")
        sys.exit(2)

    logging.info("Begin to get noinfo:")
    no_info={}
    nodata = subprocess.Popen('no -F -a|grep -v \"#\"',stdout=subprocess.PIPE, shell=True).communicate()[0]
    if nodata.find(" = ") != -1:
        nolist = transtoarray(nodata)
        for noline in nolist:
            k, v = [x.strip() for x in noline.split('=')]
            no_info[k] = v
        noinfo=sub_dict(no_info, 'sb_max,rfc1323,tcp_sendspace,tcp_recvspace,udp_sendspace,udp_recvspace,ipqmaxlen,somaxconn,tcp_keepidle,tcp_keepcnt,tcp_keepintvl,tcp_keepinit,clean_partial_conns,ip6srcrouteforward,ipignoreredirects,ipsendredirects,ipsrcrouterecv,tcp_nagle_limit,tcp_nodelayack,tcp_tcpsecure')
        logging.info("Success to get nocfg End!")
    else:
        logging.info("noinfo is wrong,please check output")
        sys.exit(2)

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
    else:
        logging.info("iooinfo is wrong,please check output")
        sys.exit(2)
    sysparaminfo = dict(sysinfo.items()+vmoinfo.items()+iooinfo.items()+noinfo.items())
    
    return sysparaminfo

def get_aix_vginfo():
    actvgdata = subprocess.Popen('lsvg -o',stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0]
    vgname='rootvg'
    if vgname=='rootvg':
        mircmd = 'lsvg -l rootvg |grep \"/\"|awk \'{print $5}\'|uniq'
        mirdata = subprocess.Popen(mircmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
        data1 = int(mirdata)
        if data1 == 1:
            rootvgmir ={'rootvgmir':'No'}
        else:
            rootvgmir ={'rootvgmir':'Yes'}
        vgcmd = 'lsvg '+ vgname
        vgdata = subprocess.Popen(vgcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('megabytes)','MB').replace('(','')
        vglist = vgdata.split()
        vgdict = {'rootvgstat':vglist[8],'rootvgsize':vglist[19]}
        vgdict1 = {}
        vgdict1[vgname] = dict(rootvgmir.items()+vgdict.items())
        return vgdict1
    elif actvgdata.find(vgname)!= -1 :
        vgdict={}
        vgcmd = 'lsvg '+ vgname
        vgdata = subprocess.Popen(vgcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True).communicate()[0].replace('megabytes)','MB').replace('(','')
        vglist = vgdata.split()
        vgdict[vgname] = {'vgstat':vglist[8],'vgsize':vglist[19]}
        return vgdict
    else:
        logging.error("The vgname is not in the active vg list")
        sys.exit(2)

def get_aix_dbfsinfo():
    logging.info("Begin to get db file system info")
    dbhomedata = subprocess.Popen('lsfs|grep -i \'/db/dbhome\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    managedata = subprocess.Popen('lsfs|grep -i \'/db/manage\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    dbdiagdata = subprocess.Popen('lsfs|grep -i \'/db/dbdiag\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    actlogdata = subprocess.Popen('lsfs|grep -i \'/db/actlog\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    mirlogdata = subprocess.Popen('lsfs|grep -i \'/db/mirlog\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    dbdatadata = subprocess.Popen('lsfs|grep -i \'/db/dbdata\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    archm1data = subprocess.Popen('lsfs|grep -i \'/db/archm1\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()
    archm2data = subprocess.Popen('lsfs|grep -i \'/db/archm2\'',stdout=subprocess.PIPE, shell=True).communicate()[0].split()

    dbhomedict = {'dbhomepath':dbhomedata[2],'dbhomesize':dbhomedata[4],'dbhomefstype':dbhomedata[3]}
    managedict = {'managepath':managedata[2],'managesize':managedata[4],'managefstype':managedata[3]}
    dbdiagdict = {'dbdiagpath':dbdiagdata[2],'dbdiagsize':dbdiagdata[4],'dbdiagfstype':dbdiagdata[3]}
    actlogdict = {'actlogpath':actlogdata[2],'actlogsize':actlogdata[4],'actlogfstype':actlogdata[3]}
    mirlogdict = {'mirlogpath':mirlogdata[2],'mirlogsize':mirlogdata[4],'mirlogfstype':mirlogdata[3]}
    dbdatadict = {'dbdatapath':dbdatadata[2],'dbdatasize':dbdatadata[4],'dbdatafstype':dbdatadata[3]}
    archm1dict = {'archm1path':archm1data[2],'archm1size':archm1data[4],'archm1fstype':archm1data[3]}
    archm2dict = {'archm2path':archm2data[2],'archm2size':archm2data[4],'archm2fstype':archm2data[3]}

    fsinfodict = dict(dbhomedict.items()+managedict.items()+dbdiagdict.items()+actlogdict.items()+mirlogdict.items()+dbdatadict.items()+archm1dict.items()+archm2dict.items())
    logging.info("End to get db file system info")
    return fsinfodict

def ck_db_version(instname,version):
    dbversion = version.upper()
    dbversion1 = dbversion.split(".")
    if dbversion1[0] in ('V10','V11'):
        db2level=dbversion[0:5]
    elif dbversion1[0] == 'V9':
        db2level=dbversion[0:4]
    else:
        logging.error("invalid dbversion!")
        retcode=-1
        return retcode
    cmd_suuser= 'su - ' + instname.lower() + ' -c '
    cmd_db2level=' db2level|grep \"DB2 v\" '
    cmd_exit=';exit'
    dbldata = subprocess.Popen(cmd_suuser+cmd_db2level+cmd_exit,stdout=subprocess.PIPE, shell=True).communicate()[0].split(' ')[4]
    dblspld = ''.join(dbldata).split('.')
    dblevel = ''.join(dblspld[0]).upper()+'.'+''.join(dblspld[1])
    if db2level == dblevel:
        return 125
    else:
        return -1

def get_aix_db2set(instname,version):
    logging.info("Begin to get db2set:")
    dbckint=ck_db_version(instname,version)
    if dbckint==125:
        cmdgetset = 'su - '+ instname.lower() + ' -c \"db2set;exit\"'
        getsetdata = subprocess.Popen(cmdgetset,stdout=subprocess.PIPE, shell=True).communicate()[0]
        if getsetdata == '':
            logging.info("DB2set parameter is not set!")
            retcode=-1
            return retcode
        elif getsetdata.find('=') != -1 and getsetdata.find('SQLSTATE=')== -1:
            setcfg={}
            midinfo = transtoarray(getsetdata)
            for line in midinfo:
                key, value = [x.strip() for x in line.split('=')]
                setcfg[key] = value
            setinfo = sub_dict(setcfg,'DB2_LOAD_COPY_NO_OVERRIDE,DB2_MAX_GLOBAL_SNAPSHOT_SIZE,DB2_USE_ALTERNATE_PAGE_CLEANING,DB2_LOGGER_NON_BUFFERED_IO,DB2_SNAPSHOT_NOAUTH,DB2_TRUST_MDC_BLOCK_FULL_HINT,DB2_MDC_ROLLOUT,DB2_EVALUNCOMMITTED,DB2_SKIPINSERTED,DB2SOSNDBUF,DB2SORCVBUF,DB2_ANTIJOIN,DB2_FORCE_FCM_BP,DB2_PARALLEL_IO,DB2COMM,DB2AUTOSTART,DB2CODEPAGE,DB2_HADR_SOSNDBUF,DB2_HADR_SORCVBUF,DB2_HADR_NO_IP_CHECK,DB2_HADR_BUF_SIZE,DB2_HADR_PEER_WAIT_LIMIT,DB2_HADR_ROS,DB2_STANDBY_ISO')
            logging.info("Success to get db2set End!")
            return setinfo
        else:
            logging.error("The ouput have something wrong!")
            logging.error(getsetdata)
            retcode=-1
            return retcode
    else:
        logging.error("The input db2 version parameter is not match the instance db2level")
        sys.exit(2)

def get_aix_dbmcfg(instname,version):
    logging.info("Begin to get dbmcfg:")
    dbversion = version.upper()
    dbversion1 = dbversion.split(".")
    if dbversion1[0] in ('V10','V11'):
        db2level=dbversion[0:5]
    elif dbversion1[0] == 'V9':
        db2level=dbversion[0:4]

    dbckint=ck_db_version(instname,version)
    if dbckint==125:
        dbmcmd = 'su - ' + instname.lower() + ' -c \"db2 get dbm cfg\"|grep \") =\"'
        cmdexit = ';exit'
        dbmdata  = subprocess.Popen(dbmcmd+cmdexit,stdout=subprocess.PIPE, shell=True).communicate()[0]
        if dbmdata.find(' = ') != -1 and dbmdata.find('SQLSTATE=') == -1:
            dbmmidinfo = []
            dbmcfg={}
            for line in dbmdata.split('\n'):
                dbmlinedata=re.findall('\([A-Z_]{3,}\) = .*$',line)
                if dbmlinedata:
                    strlinedata =''.join(dbmlinedata).replace('(','').replace(')','').replace(' = ','=')
                    strlinedata2 = re.sub("=AUTOMATIC\w+","=AUTOMATIC",strlinedata)
                    splitlinedata = strlinedata2.split('=')
                    dbmmidinfo.append(splitlinedata)
            dbmcfg=dict(dbmmidinfo)
            if db2level in ('V9.1','V9.5','V9.7','V10.1','V10.5','V11.1'):
#                 dbminfo=sub_dict(dbmcfg,'FEDERATED,DFT_MON_BUFPOOL,DFT_MON_LOCK,DFT_MON_SORT,DFT_MON_STMT,DFT_MON_TABLE,DFT_MON_TIMESTAMP,DFT_MON_UOW,HEALTH_MON,MON_HEAP_SZ,AUDIT_BUF_SZ,INSTANCE_MEMORY,SHEAPTHRES,KEEPFENCED,FENCED_POOL,NUM_INITFENCED,INDEXREC,SVCENAME,INTRA_PARALLEL')
                logging.info("Success to get db version dbmcfg End!")
                return dbmcfg
            else:
                logging.error("db2 version is not in:V9.1,V9.5,V9.7,V10.5,V11.1")
                retcode=-1
                return retcode
        else:
            logging.error("The ouput have something wrong!")
            logging.error(dbmdata)
            retcode=-1
            return retcode
    else:
        logging.error("The input db2 version parameter is not match the instance db2level")
        retcode=-1
        return retcode

def get_aix_dbcfg(instname,version,dbname):
    logging.info("Begin to get dbcfg:")
    dbversion = version.upper()
    dbversion1 = dbversion.split(".")
    if dbversion1[0] in ('V10','V11'):
        db2level=dbversion[0:5]
    elif dbversion1[0] == 'V9':
        db2level=dbversion[0:4]
    dbckint=ck_db_version(instname,version)
    if dbckint==125:
        getdbcfgcmd = 'su - ' + instname.lower() + ' -c \"db2 get db cfg for ' + dbname + '\"'
        cmdexit=';exit'
        getdbcfgdata = subprocess.Popen(getdbcfgcmd+cmdexit,stdout=subprocess.PIPE, shell=True).communicate()[0]
        if getdbcfgdata.find(' = ') != -1 and getdbcfgdata.find('SQLSTATE=') == -1:
            getdbcfgdata1 = getdbcfgdata.replace('Database territory','(DB_TERRITORY)').replace('Database code page','(DB_CODEPAGE)').replace('Database code set','(DB_CODESET)').replace('Database country/region code','(DB_COUNTRY)').replace('Database collating sequence','(DB_COLLATE)').replace('Number compatibility','(NUM_COMPAT)').replace('Varchar2 compatibility','(VARCHAR2_COMPAT)').replace('Date compatibility','(DATE_COMPAT)').replace('Database page size','(DB_PAGESIZE)').replace('Default number of containers','Default number of containers (DEFNUM_CONT) ').replace('Path to log files','(ACTLOGPATH)').replace('First active log file','(FIRST_ACTLOGFIL)').replace('HADR database role','(HADR_DBROLE)').replace('Database is in write suspend state','(DB_WSSTATE)').replace(' ','')
            midinfo = []
            dbcfg={}
            for line in getdbcfgdata1.split('\n'):
                dblinedata = re.findall('\([A-Z_]{3,}\)=.*$',line)
                if dblinedata:
                    strlinedata=''.join(dblinedata)
                    strlinedata2 = re.sub('\(([A-Z_]{3,})\)=','\\1=',strlinedata)
                    strlinedata3 = re.sub("=AUTOMATIC\(\w+\)","=AUTOMATIC",strlinedata2)
                    splitlinedata = strlinedata3.split('=')
                    midinfo.append(splitlinedata)
            dbcfg=dict(midinfo)
            if db2level in ('V9.1','V9.5','V9.7','V10.1','V10.5','V11.1'):
                logging.info("Success to get dbcfg End!")
                return dbcfg
            else:
                logging.error("db2 version is not in:V9.1,V9.5,V9.7,V10.5,V11.1")
                retcode=-1
                return retcode
        else:
            logging.error("The ouput have something wrong!")
            logging.error(getdbcfgdata)
            retcode=-1
            return retcode
    else:
        logging.error("The input db2 version parameter is not match the instance db2level")
        retcode=-1
        return retcode
def get_aix_proc(proname):
    processcmd="ps -ef|grep -i " + proname + "|grep -v grep >/dev/null"
    processCK=os.system(processcmd)
    if processCK == 0:
        result = proname + ": yes";
    else:
        result = proname + ": no";
    return result

def check_aix_proc():
    logging.info("Begin to get product install info:")
    procinfo = {}
    ckops = get_aix_proc('opsware')
    ckitm = get_aix_proc('itm')
    cknim = get_aix_proc('nim')
    cknbu = get_aix_proc('nbu')
    ckdb2m = get_aix_proc('db2_mon')
    cktivo = get_aix_proc('tivoli')
    ckkanb = get_aix_proc('kanban')
    ckcdcr = get_aix_proc('cdc_run')
    ckprocdata = ckops,ckitm,cknim,cknbu,ckdb2m,cktivo,ckkanb,ckcdcr
    ckproclist = list(ckprocdata)
    for i in ckproclist:
        k, v = [x.strip() for x in i.split(':')]
        procinfo[k] = v
    logging.info("End to get product install info.")
    
    logging.info("Begin to get crontab info:")
    croncmd = 'cat /var/spool/cron/crontabs/*|grep -v \"^#\"'
    crondata = subprocess.Popen(croncmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    crondict = {'crontab':crondata}
    logging.info("End to get crontab info")

    procdict=dict(procinfo.items()+crondict.items())
    return procdict

def get_aix_network():
    adaptercmd = 'ifconfig -l'
#    ifnetdata = subprocess.Popen(adaptercmd, stdout=subprocess.PIPE, shell=True)
#    ifnetname = ifnetdata.communicate()[0].replace(' ','\n').split('\n')
    (status, output) = commands.getstatusoutput(adaptercmd)
    ifnetname = output.replace(' ','\n').split('\n')
    ipinfo=[]
    tcpsinfo=[]
    tcprinfo=[]
    rfcinfo=[]

    for line in ifnetname:
        if line and not line.startswith('lo'):
            cmd = 'ifconfig ' + line
            tmpdata = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0].replace('\n','').replace('\t','').split(' ')
            ipinfo.append(tmpdata[2])
            tcpsinfo.append(tmpdata[8])
            tcprinfo.append(tmpdata[10])
            rfcinfo.append(tmpdata[12])
    ifnetinfo={'ipaddr':ipinfo,'tcp_sendspace':tcpsinfo,'tcp_recvspace':tcprinfo,'rfc1323':rfcinfo}
    return ifnetinfo

def get_aix_usercfg(instname):
    user_cfg={}
    cmd='lsuser -f '+instname.lower()+'|grep -v '+instname.lower()+":"
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0]
    data1 = 'uname='+instname.lower()+'\n'+data
    info = transtoarray(data1)
    for i in info:
        k, v = [x.strip() for x in i.split('=')]
        user_cfg[k] = v
    userinfo=sub_dict(user_cfg,'uname,id,pgrp,groups,home,shell,expires,fsize,cpu,data,stack,rss,nofiles,fsize_hard,cpu_hard,data_hard,stack_hard,rss_hard,nofiles_hard,capabilities')
    grpname = user_cfg.get('pgrp')
    cmd = 'lsgroup -f ' + grpname +'|grep -v '+grpname+":"
    data = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True).communicate()[0].replace('id','groupid')
    info = transtoarray(data)
    grp_cfg={}
    for i in info:
        k, v = [x.strip() for x in i.split('=')]
        grp_cfg[k] = v
    grpinfo=sub_dict(grp_cfg,'groupid')

    return dict(userinfo.items()+grpinfo.items())

def get_aix_dbstat(instname,dbname,version):
    instname = instname.lower().strip()
    dbname = dbname.lower().strip()
    dbversion = version.upper()
    dbversion1 = dbversion.split(".")
    if dbversion1[0] in ('V10','V11'):
        db2level=dbversion[0:5]
    elif dbversion1[0] == 'V9':
        db2level=dbversion[0:4]
    else:
        logging.error("invalid dbversion!")
        retcode=-1
        return retcode
    cmd_suuser= 'su - ' + instname.lower() + ' -c '
    cmd_db2level=' db2level|grep \"DB2 v\" '
    cmd_exit=';exit'
    dbldata = subprocess.Popen(cmd_suuser+cmd_db2level+cmd_exit,stdout=subprocess.PIPE, shell=True).communicate()[0].split(' ')[4]
    dblspld = ''.join(dbldata).split('.')
    dblevel = ''.join(dblspld[0]).upper()+'.'+''.join(dblspld[1])
    if db2level == dblevel:
        ckdbvdict={'ck_dbversion':'Yes'}
    else:
        ckdbvdict={'ck_dbversion':'No'}

    logging.info('Begin to check db2sysc process is exist or not:')
    db2syscmd = 'ps -ef|grep -i db2sysc|grep -i ' + instname.upper().strip() + '|grep -v grep>/dev/null'
    retcode=subprocess.call(db2syscmd,shell=True)
    if retcode == 0:
        db2sysdict={'db2_process':'Yes'}
    else:
        db2sysdict={'db2_process':'No'}
    logging.info('Check db2sysc process end!')

    logging.info('Begin to check db con status:')
    catdbcmd = 'su - ' + instname + ' -c \" db2 list db directory;exit\"'
    catdbdata =subprocess.Popen(catdbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if catdbdata.find(dbname.upper()) != -1 and catdbdata.find('SQLSTATE=') == -1:
        catdbdict={'dbcat_stat':'Yes'}
    else:
        catdbdict = {'dbcat_stat':'No'}
  
    condbcmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + ';exit\"'
    condbdata =subprocess.Popen(condbcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    if condbdata.find(dbname.upper()) != -1 and condbdata.find('SQLSTATE=') == -1:
        logging.info('Begin to check db tbs status:')
        cktbscmd = 'su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select tbsp_name,TBSP_TOTAL_SIZE_KB,TBSP_TOTAL_PAGES, tbsp_type,TBSP_CONTENT_TYPE,TBSP_STATE from SYSIBMADM.TBSP_UTILIZATION with ur\";exit\"'
        cktbsdata = subprocess.Popen(cktbscmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
        if cktbsdata.find('SQLSTATE=') != -1:
            logging.error('There are something error:')
            logging.error(cktbsdata)
            retcode=-1
            return retcode
        else:
            tbsinfo = {}
            tbsarray = [map(str,ln.strip().split()) for ln in cktbsdata.splitlines() if ln.strip()]
            tbsinfo['tbsname'] = [x[0] for x in tbsarray]
            tbsstatlist = [x[5] for x in tbsarray]
            for  i in range(len(tbsstatlist)):
                if ''.join(tbsstatlist[i]) != 'NORMAL':
                    tbsinfo['tbs_stat']='No'
                else:
                    tbsinfo['tbs_stat']='Yes'
            return tbsinfo
    else:
        logging.error('Connect to db have error!')
        logging.error(condbdata)
        retcode=-1
        return retcode

    dblookcmd = 'su - ' + instname + ' -c \" db2look -d ' + dbname + ' -e ;exit\"'
    dblookdata = subprocess.Popen(dblookcmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    grepcmd = 'grep -i \"CREATE TABLE\"'
    dblookdata1 = subprocess.Popen(grepcmd,stdin=dblookdata.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0]
    tbcount = dblookdata1.count('\n')
    tblcountdict = {'tb_count':tbcount}
    
    dbstatdict=dict(tblcountdict.items()+tbsinfo.items()+ckdbvdict.items()+db2sysdict.items()+catdbdict.items())
    return dbstatdict

def get_aix_dbobject(instname,dbname):
    instname=instname.lower().strip()
    dbname = dbname.lower().strip()
    logging.info('Begin to check db object info:')
    Sql_select_procedure='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select procschema,procname from syscat.procedures with ur\";exit\"'
    Sql_select_function='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select funcschema,funcname from syscat.functions with ur\";exit\"'
    Sql_select_package='su - ' + instname + ' -c \" db2 connect to ' + dbname + '>/dev/null ; db2 -x \"select pkgschema,pkgname from syscat.packages with ur\";exit\"'
    Str_Data_procudure =subprocess.Popen(Sql_select_procedure,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    Str_Data_function =subprocess.Popen(Sql_select_function,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    Str_Data_package =subprocess.Popen(Sql_select_package,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split('\n')
    proc_list = []
    for proc_line in Str_Data_procudure:
        if proc_line:
            proc_data = ''.join(proc_line).split()
            proc_sys_data = ''.join(proc_data[0])[0:3]
            if proc_sys_data != 'SYS':
                procstr=''.join(proc_data)
                proc_list.append(procstr)
    proc_dict = {'procedureinfo':len(proc_list)}
    func_list = []
    for func_line in Str_Data_function:
        if func_line:
            func_data = ''.join(func_line).split()
            func_sys_data = ''.join(func_data[0])[0:3]
            if func_sys_data != 'SYS':
                funcstr=''.join(func_data)
                func_list.append(funcstr)
    func_dict = {'functioninfo':len(func_list)}
    package_list = []
    for package_line in Str_Data_package:
        if package_line:
            package_data = ''.join(package_line).split()
            package_sys_data = ''.join(package_data[0])[0:3]
            if package_sys_data != 'SYS':
                packagestr=''.join(package_data)
                package_list.append(packagestr)
    package_dict = {'packageinfo':len(package_list)}
    return dict(proc_dict.items()+func_dict.items()+package_dict.items())

def suggest_sysparm_result(parmname,limitvalue):
    if parmname in ('maxuproc'):
        suggest='please modified '+parmname+',\n chdev -l sys0 -a '+ parmname +'=' + limitvalue
    elif parmname in ('sb_max','rfc1323','tcp_sendspace','tcp_recvspace','udp_sendspace','udp_recvspace','ipqmaxlen','somaxconn','tcp_keepidle','tcp_keepcnt','tcp_keepintvl','clean_partial_conns','ip6srcrouteforward','ipignoreredirects','ipsendredirects','ipsrcrouterecv','tcp_nagle_limit','tcp_nodelayack','tcp_tcpsecure','tcp_keepinit'):
        suggest='please modified '+parmname+',\n no -p -o '+ parmname +'=' + limitvalue
    elif parmname in ('minfree','maxfree','minperm%','maxperm%','maxclient%','strict_maxclient','strict_maxperm','lru_file_repage','v_pinshm','maxperm%'):
        suggest='please modified '+parmname+',\n vmo -p -o '+ parmname +'=' + limitvalue
    elif parmname in ('j2_maxPageReadAhead','j2_maxRandomWrite','j2_minPageReadAhead','maxpgahead','minpgahead','maxrandwrt','j2_nBufferPerPagerDevice','numfsbufs','j2_nPagesPerWriteB:ehindCluster','pv_min_pbuf','sync_release_ilock'):
        suggest='please modified '+parmname+',\n ioo -p -o  '+ parmname +'=' + limitvalue
    elif parmname in ('cpu','data','stack','rss','nofiles','fsize_hard','cpu_hard','data_hard','stack_hard','rss_hard','nofiles_hard','capabilities'):
        suggest='please modified '+parmname+',\n chuser  '+ parmname +'=' + limitvalue + '<instname>'
    elif parmname in ('dbhomepath','managepath','dbdiagpath','actlogpath','mirlogpath','dbdatapath','archm1path','archm2path'):   
        suggest='please modified '+parmname+',\n change the path  '+ parmname +'=' + limitvalue
    elif parmname in ('dbhomefstype','dbdiagstype','managefstype','dbdatastype','actlogfstype','mirlogfstype','archm1fstype','archm2fstype'):
        suggest='please modified '+parmname+',\n change the fstype  '+ parmname +'to' + limitvalue
    elif parmname in ('rfc1323','tcp_sendspace','tcp_recvspace'):
        suggest='please modified '+parmname+',\n change the ifconfig  '+ parmname +'to' + limitvalue
    else:
        suggest='error parameter'
    result='NO'
    return suggest,result


##比较两个字典的值，输出不同的key和值
def cmpdicts(dct0, dct1):
    suggest = {}
    result={}
    keys = set(dct0.keys() + dct1.keys())
    for k in keys:
        if cmp(dct0.get(k), dct1.get(k)):
            c1=suggest_sysparm_result(k,dct1.get(k))
            suggest[k]=c1[0]
            result[k]=c1[1]
        else:
            suggest[k]=''
            result[k]='YES'
    return suggest,result


if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2].upper()
    instname=sys.argv[4].upper()
    dbname=sys.argv[6].upper()
    port=sys.argv[8].upper()
    version = sys.argv[10].upper()
    parameter = sys.argv[12]
    parameterlist=parameter.split(',')
    lhostname=socket.gethostname().upper()
    if lhostname!=hostname:
        logging.error("error hostname")
        sys.exit()
    else:
        outputdict={}
        syssuggest={}
        sysresult={}
        resultdict={}
        suggestdict={}
        for paraline in parameterlist:
            if paraline == 'osinfo': 
                outputdict['osinfo'] = get_aix_osinfo()
                
                if outputdict['osinfo']['oslevel'] not in ('7100-03-05','6100-09-05'):
                    syssuggest['oslevel']='please upgrade to the correct version'
                    sysresult['oslevel']='NO'
                else:
                    syssuggest['oslevel']='' 
                    sysresult['oslevel']='YES'
                if outputdict['osinfo']['xlcversion'] <= '12.1.0.0':
                    syssuggest['xlcversion']='please download and install xlc version to 12.1.0.0'
                    sysresult['xlcversion']='NO'
                else:
                    syssuggest['xlcversion']=''
                    sysresult['xlcversion']='YES' 
                if outputdict['osinfo']['timezone'] not in ('BEIST-8','Asia/Shanghai'):
                    syssuggest['timezone']='please modified the timezone to BEIST-8 or ASIA/Shanghai'
                    sysresult['timezone']='NO'
                else:
                    syssuggest['timezone']=''
                    sysresult['timezone']='YES' 
                memsizes=int(outputdict['osinfo']['memsize']) * 1.5
                if outputdict['osinfo']['pgspace'] <= '8192' or outputdict['osinfo']['pgspace']!=memsizes : 
                    syssuggest['pgspace']='please modified the pagespace size to 8192 or the memsize*1.5'
                    sysresult['pgspace']='NO' 
                else:
                    syssuggest['pgspace']=''
                    sysresult['pgspace']='YES' 
            if paraline == 'sysparm':
                outputdict['sysparm'] = get_aix_sysparm()
                syspcomp=cmpdicts(outputdict['sysparm'],sysparm_value_dict)
                syssuggest=syspcomp[0]
                sysresult=syspcomp[1]
                        
            if paraline == 'dbinfo':
                outputdict['dbinfo'] = get_aix_dbinfo(instname,dbname,version)
            if paraline == 'dbfsinfo':
                outputdict['dbfsinfo'] = get_aix_dbfsinfo()
            if paraline == 'db2set':
                outputdict['db2set'] = get_aix_db2set(instname,version)
            if paraline == 'dbmcfg':
                outputdict['dbmcfg'] = get_aix_dbmcfg(instname,version)
            if paraline == 'dbcfg':
                outputdict['dbcfg'] = get_aix_dbcfg(instname,version,dbname)
            if paraline == 'ckprod':
                outputdict['ckprod'] = check_aix_proc()
            if paraline == 'vginfo':
                outputdict['vginfo'] = get_aix_vginfo()
            if paraline == 'network':
                outputdict['network'] = get_aix_network()
            if paraline == 'userinfo':
                outputdict['userinfo'] = get_aix_usercfg(instname)
            if paraline == 'dbstat':
                outputdict['dbstat'] = get_aix_dbstat(instname,dbname,version)
            if paraline == 'dbobject':
                outputdict['dbobject'] = get_aix_dbobject(instname,dbname)


            resultdict['sysresult']=sysresult
            suggestdict['syssuggest']=syssuggest       
                               
        print json.dumps(outputdict),json.dumps(syssuggest),json.dumps(sysresult)