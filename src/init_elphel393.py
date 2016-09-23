#!/usr/bin/env python
'''
# Copyright (C) 2016, Elphel.inc.
# Usage: known
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http:#www.gnu.org/licenses/>.

@author:     Oleg K Dzhimiev
@copyright:  2016 Elphel, Inc.
@license:    GPLv3.0+
@contact:    oleg@elphel.com
@deffield    updated: unknown

'''

__author__ = "Elphel"
__copyright__ = "Copyright 2016, Elphel, Inc."
__license__ = "GPL"
__version__ = "3.0+"
__maintainer__ = "Oleg K Dzhimiev"
__email__ = "oleg@elphel.com"
__status__ = "Development"

import subprocess
import sys
import time

#params
SENSOR_TYPE = 5
IPADDR = "192.168.0.9"
IMGSRV_PORT = 2323
CAMOGM_PORT = 3456
CAMOGM_PIPE = "/var/volatile/camogm_cmd"
SATA_EN = 1

PYDIR = "/usr/local/bin"
VERILOG_DIR = "/usr/local/verilog"

#functions
def shout(cmd):
    #subprocess.call prints to console
    subprocess.call(cmd,shell=True)

def init_ipaddr(ip):
    shout("ifconfig eth0 "+ip)
    
def init_mcntrl(pydir,verilogdir):
    shout(pydir+"/test_mcntrl.py @"+verilogdir+"/hargs")

def init_imgsrv(port):
    shout("imgsrv -p "+str(port))
    #restart PHP - it can get errors while opening/mmaping at startup, then some functions fail
    shout("killall lighttpd; /usr/sbin/lighttpd -f /etc/lighttpd.conf")
    shout("/www/pages/exif.php init=/etc/Exif_template.xml")

def init_port(index):
    print("Port "+index+": framepars enable")
    shout("wget -O /dev/null \"localhost/framepars.php?sensor_port="+index+"&cmd=init\"")        

def init_autoexp(index):
    shout("autoexposure -p "+index+" -c 0 -b 0 -d 1 &")
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+index+"&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3\"")

def init_autowb(index):
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+index+"&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x18000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000\"")

def init_sata(sata_en,pydir):
    if (sata_en==1):
        shout(pydir+"/x393sata.py")
        shout("modprobe ahci_elphel &")
        shout("sleep 2")
        shout("echo 1 > /sys/devices/soc0/amba@0/80000000.elphel-ahci/load_module")



#main

# default
switch = {
    'ip':1,
    'mcntrl':1,
    'imgsrv':1,
    'port1':1,
    'port2':1,
    'port3':1,
    'port4':1,
    'framepars':1,
    'autoexp':1,
    'autowb':1,
    'sata':1
    }

# update from argv
if len(sys.argv) > 1:
    switch.update(eval(sys.argv[1]))

#1
if switch['ip']==1:
    print(sys.argv[0]+": ip = "+IPADDR)
    init_ipaddr(IPADDR)
else:
    print("skip ip")
    
#2
if switch['mcntrl']==1:
    print(sys.argv[0]+": mcntrl")
    init_mcntrl(PYDIR,VERILOG_DIR)
else:
    print("skip mcntrl")
    
#3
if switch['imgsrv']==1:
    print(sys.argv[0]+": imgsrv")
    init_imgsrv(IMGSRV_PORT)
else:
    print("skip imgsrv")
    
#4
print(sys.argv[0]+": init ports")
for i in range(1,5):        
    if switch['port'+str(i)]==1:
        index = str(i-1)
        sysfs_content = ""
        # read sysfs, overwrite if argv?!  
        with open("/sys/devices/soc0/elphel393-detect_sensors@0/sensor"+index+"0", 'r') as content_file:
            sysfs_content = content_file.read()
            sysfs_content = sysfs_content.strip()
        
        #Sensor list
        #1. mt9p006
        #2. mt9f002
        #3. ...
        if (sysfs_content=="mt9p006"):
            init_port(index)
        else:
            switch['port'+str(i)] = 0
            print("Sensor port "+str(i)+": disabled, please check device tree")
    else:
        print("skip sensor port "+str(i))

time.sleep(1)

#5
print(sys.argv[0]+": auto exposure and auto white balance")
for i in range(1,5):
    if switch['port'+str(i)]==1:
        index = str(i-1)
        if switch['autoexp']==1:
            init_autoexp(index)
        else:
            print("Port "+str(i)+": skip autoexp")
            
        if switch['autowb']==1:
            init_autowb(index)
        else:
            print("Port "+str(i)+": skip autowb")

#6
print(sys.argv[0]+" SATA")
if switch['sata']==1:
    init_sata(SATA_EN,PYDIR)
else:
    print("skip SATA")

# create directory for camogm pipes, symlink /var/state should already be in rootfs 
shout("mkdir /var/volatile/state")
