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
    print 'get_aix_dbfs usage:  '
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
        Usage()
        sys.exit(2)
    else:
        for op, ar in opts:
            if op in ('-h', '--help'):
                Usage()
                sys.exit(1)
            elif op in ('-o','--hostname'):
                hostname=ar
            else:
                logging.error('Error: invalid parameters')
                Usage()
                sys.exit(2)



def get_aix_dbfsinfo():
    logging.info("Begin to get db file system info")

    data_dbhome = subprocess.Popen('lsfs|grep -i \'/db/dbhome\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_manage = subprocess.Popen('lsfs|grep -i \'/db/manage\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_dbdiag = subprocess.Popen('lsfs|grep -i \'/db/dbdiag\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_actlog = subprocess.Popen('lsfs|grep -i \'/db/actlog\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_mirlog = subprocess.Popen('lsfs|grep -i \'/db/mirlog\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_dbdata = subprocess.Popen('lsfs|grep -i \'/db/dbdata\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_archm1 = subprocess.Popen('lsfs|grep -i \'/db/archm1\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()
    data_archm2 = subprocess.Popen('lsfs|grep -i \'/db/archm2\'',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).communicate()[0].split()

    dict_dbhome = {'dbhomepath':data_dbhome[2],'dbhomesize':data_dbhome[4],'dbhomefstype':data_dbhome[3]}
    dict_manage = {'managepath':data_manage[2],'managesize':data_manage[4],'managefstype':data_manage[3]}
    dict_dbdiag = {'dbdiagpath':data_dbdiag[2],'dbdiagsize':data_dbdiag[4],'dbdiagfstype':data_dbdiag[3]}
    dict_actlog = {'actlogpath':data_actlog[2],'actlogsize':data_actlog[4],'actlogfstype':data_actlog[3]}
    dict_mirlog = {'mirlogpath':data_mirlog[2],'mirlogsize':data_mirlog[4],'mirlogfstype':data_mirlog[3]}
    dict_dbdata = {'dbdatapath':data_dbdata[2],'dbdatasize':data_dbdata[4],'dbdatafstype':data_dbdata[3]}
    dict_archm1 = {'archm1path':data_archm1[2],'archm1size':data_archm1[4],'archm1fstype':data_archm1[3]}
    dict_archm2 = {'archm2path':data_archm2[2],'archm2size':data_archm2[4],'archm2fstype':data_archm2[3]}

    fsinfo = dict(dict_dbhome.items()+dict_manage.items()+dict_dbdiag.items()+dict_actlog.items()+dict_mirlog.items()+dict_dbdata.items()\
                  +dict_archm1.items()+dict_archm2.items())
    logging.info("End to get db file system info")
    return fsinfo 



if __name__ == '__main__':
    main(sys.argv)
    hostname=sys.argv[2]
    lhostname=socket.gethostname()
    if lhostname!=hostname:
        sys.exit()
    else:
        dict_data_result=get_aix_dbfsinfo()
        print json.dumps(dict_data_result)
