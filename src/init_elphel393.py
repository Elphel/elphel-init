#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
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
import os

#params
SENSOR_TYPE = 5
IPADDR = "192.168.0.9"
IMGSRV_PORT = 2323
CAMOGM_PORT = 3456
CAMOGM_PIPE = "/var/volatile/camogm_cmd"
SATA_EN = 1

PYDIR = "/usr/local/bin"
VERILOG_DIR = "/usr/local/verilog"
LOGFILE = "/var/log/init_elphel393.log"
FPGA_VERION_FILE = '/sys/devices/soc0/elphel393-framepars@0/fpga_version'
TIMEOUT = 120

#functions
def get_fpga():
    with open(FPGA_VERION_FILE,'r') as f:
        try:
            return f.read()
        except:
            return None
    
def fpga_OK(timeout):
    ntry = 0
    fpga = None
    while not fpga and ((not timeout) or (ntry<timeout)):
        fpga= get_fpga()
        print ('.',end='')
        sys.stdout.flush()
        ntry += 1
        time.sleep(1)
    return fpga        
    
def colorize(string, color, bold):
    color=color.upper()
    attr = []
    if color == 'RED':
        attr.append('31')
    elif color == 'GREEN':    
        attr.append('32')
    elif color == 'YELLOW':    
        attr.append('33')
    elif color == 'BLUE':    
        attr.append('34')
    elif color == 'MAGENTA':    
        attr.append('35')
    elif color == 'CYAN':    
        attr.append('36')
    elif color == 'GRAY':    
        attr.append('37')
    else:
        pass
        # red
    if bold:
        attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def log_msg(msg):
    with open ('/proc/uptime') as f: 
        t=float(f.read().split()[0])
    with open(LOGFILE,'a') as msg_file:
        print (colorize("[%8.2f] %s: "%(t, sys.argv[0].split('/')[-1].split('.')[0]),'CYAN',0)+msg)
        print("[%8.2f]  %s"%(t,msg),file=msg_file)

def shout(cmd):
    #subprocess.call prints to console
    subprocess.call(cmd,shell=True)

def init_ipaddr(ip):
    shout("ifconfig eth0 "+ip)
    
def init_mcntrl(pydir,verilogdir):
    shout(pydir+"/test_mcntrl.py @"+verilogdir+"/hargs")

def init_mcntrl_eyesis(pydir,verilogdir):
    shout(pydir+"/test_mcntrl.py @"+verilogdir+"/hargs-eyesis")

def init_imgsrv(port):
    shout("imgsrv -p "+str(port))
    #restart PHP - it can get errors while opening/mmaping at startup, then some functions fail
    shout("killall lighttpd; /usr/sbin/lighttpd -f /etc/lighttpd.conf")
    shout("/www/pages/exif.php init=/etc/Exif_template.xml")

def init_port(index):
    
    sysfs_content = init_port_readsysfs("port_mux"+index)
    if sysfs_content=="mux10359":
        init_mux10359(index)
    else:
        sysfs_content = init_port_readsysfs("sensor"+index+"0")
        #Sensor list
        #1. mt9p006
        #2. mt9f002
        #3. ...
        if (sysfs_content=="mt9p006"):
            log_msg("Port "+index+": framepars enable")
            shout("wget -O /dev/null \"localhost/framepars.php?sensor_port="+index+"&cmd=init\"")        
        else:
            switch['port'+str(i)] = 0
            log_msg("Sensor port "+str(i)+": disabled, please check device tree")

def init_port_readsysfs(filename):
    sysfs_content = ""
    with open("/sys/devices/soc0/elphel393-detect_sensors@0/"+filename, 'r') as content_file:
        sysfs_content = content_file.read()
        sysfs_content = sysfs_content.strip()
    return sysfs_content

def init_mux10359(index):
    shout("cat /usr/local/verilog/x359.bit > /dev/sfpgaconfjtag"+index)

def init_autoexp_daemon(index):
    shout("autoexposure -p "+index+" -c 0 -b 0 -d 1 &")
def init_autoexp(index):
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+index+"&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3\"")

def init_autoexp_eyesis(index):
    shout("autoexposure -p "+index+" -c 0 -b 0 -d 1 &")
    roi = "HISTWND_RWIDTH=0xc000&HISTWND_RHEIGHT=0xffff&HISTWND_RLEFT=0xffff&HISTWND_RTOP=0x8000"
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+index+"&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AUTOEXP_EXP_MAX=5000&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=1&"+roi+"\"")

def init_autowb(index):
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+index+"&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x20000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000\"")

def init_autowb_eyesis(index):
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+index+"&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x0&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x20000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x1be3e&GAING=0x18000&GAINGB=0x18000&GAINB=0x26667\"")

def init_other_eyesis(index):
    shout("wget -O /dev/null \"localhost/camogm_interface.php?cmd=set_parameter&sensor_port="+index+"&pname=QUALITY&pvalue=97\"")
    shout("wget -O /dev/null \"localhost/camogm_interface.php?cmd=set_parameter&sensor_port="+index+"&pname=COLOR&pvalue=5\"")

def init_sata(sata_en,pydir):
    if (sata_en==1):
        if not get_fpga():
            log_msg ("Waiting for the FPGA to be programmed to start SATA")
            if not fpga_OK(TIMEOUT):
                print()
                log_msg ("Timeout while waiting for the FPGA to be programmed")
                return
            else:
                print (" Done")
        shout(pydir+"/x393sata.py")
        shout("modprobe ahci_elphel &")
        shout("sleep 2")
        shout("echo 1 > /sys/devices/soc0/amba@0/80000000.elphel-ahci/load_module")

def init_usb_hub():
    """
    Initializes USB HUB on 10389 board (stays inituialized through reboot, does not respond after initialized)
    """
    if not os.path.exists('/sys/bus/usb/devices/1-1'):
        shout("i2cset -y 0 0x2c 0xff 0x0201 w")
        shout("i2cset -y 0 0x2c 0xff 0x0001 w")
        shout("i2cset -y 0 0x2c 0x00 0x3401 w")
        shout("i2cset -y 0 0x2c 0x01 0x1201 w")
        shout("i2cset -y 0 0x2c 0x06 0x9b01 w")
        shout("i2cset -y 0 0x2c 0x07 0x1001 w")
        shout("i2cset -y 0 0x2c 0x08 0x0001 w")
        shout("i2cset -y 0 0x2c 0xff 0x0101 w")
        log_msg ("Initialized USB hub with Vendor=1234")
    else:
        log_msg ("USB hub was already initialized")

def start_gps_compass():
    """
    Detect GPS and/or compass boards and start them
    """
    if not get_fpga():
        log_msg ("Waiting for the FPGA to be programmed to start SATA")
        if not fpga_OK(TIMEOUT):
            print()
            log_msg ("Timeout while waiting for the FPGA to be programmed")
            return
        else:
            print (" Done")
    
    shout("start_gps_compass.php")
    
def disable_gpio_10389():
    gpio_10389 = "/sys/devices/soc0/elphel393-pwr@0/gpio_10389"
    shout("echo '0x101' > "+gpio_10389) #power on
    shout("echo '0x100' > "+gpio_10389) #power off
    time.sleep(1)

#main

# default
switch = {
    'usb_hub':1,
    'ip':1,
    'mcntrl':1,
    'imgsrv':1,
    'port1':1,
    'port2':1,
    'port3':1,
    'port4':1,
    'framepars':1,
    'autoexp_daemon':0,
    'autocampars':0,
    'autoexp':1,
    'autowb':1,
    'sata':1,
    'gps':1,
    'eyesis':0
    }

# update from argv
if len(sys.argv) > 1:
    switch.update(eval(sys.argv[1]))
#pre
volatile_html = '/var/volatile/html'
if not os.path.exists(volatile_html):
    os.mkdir(volatile_html)

#need to disable fan for eyesis
#if switch['eyesis']!=0:
#    log_msg('Eyesis mode: turn off gpio 10389')
#    disable_gpio_10389()

# start temperature monitor and let it control fan (set 'off' to disable fan control)
#Move tempon early, so other problems will not block it
if switch['eyesis']!=0:
    log_msg('Eyesis mode: turn off gpio 10389')
    disable_gpio_10389()
    log_msg("Eyesis: fan off")
    shout("tempmon.py --control_fan off &")
else:
    log_msg("Fan on")
    shout("tempmon.py --control_fan on &")




#0
if switch['usb_hub']==1:
    log_msg('Initialize USB hub')
    init_usb_hub()
else:
    log_msg("skip USB hub initiualization")

#1
if switch['ip']==1:
    log_msg(sys.argv[0]+": ip = "+IPADDR)
    init_ipaddr(IPADDR)
else:
    log_msg("skip ip")
    
#2
if switch['mcntrl']==1:
    log_msg(sys.argv[0]+": mcntrl")
    if switch['eyesis']!=0:
        init_mcntrl_eyesis(PYDIR,VERILOG_DIR)
    else:
        init_mcntrl(PYDIR,VERILOG_DIR)
else:
    log_msg("skip mcntrl")

#3
if switch['imgsrv']==1:
    log_msg(sys.argv[0]+": imgsrv")
    init_imgsrv(IMGSRV_PORT)
else:
    log_msg("skip imgsrv")

#4
for i in range(1,5):        
    if switch['port'+str(i)]==1:
        init_port(str(i-1))
    else:
        log_msg("skip sensor port "+str(i))



#5
if (switch['eyesis'] != 0) and (switch['framepars'] != 0):
    #time.sleep(1)
    for i in range(4):
        sysfs_content = init_port_readsysfs("sensor"+str(i)+"0")
        if sysfs_content=="mt9p006":
            shout("wget -O - \"localhost/framepars.php?sensor_port="+str(i)+"&cmd=min_init\"")
    time.sleep(2)
    shout("cat /proc/interrupts")
    
    for i in range(4):
        sysfs_content = init_port_readsysfs("sensor"+str(i)+"0")
        if sysfs_content=="mt9p006":
            shout("wget -O - \"localhost/framepars.php?sensor_port="+str(i)+"&cmd=eyesis_trig\"")
    time.sleep(2)
    shout("cat /proc/interrupts")
    
    for i in range(4):
        sysfs_content = init_port_readsysfs("sensor"+str(i)+"0")
        if sysfs_content=="mt9p006":
            log_msg("AUTOEXP und AUTOWB, channel = "+str(i))
            init_other_eyesis(str(i))
            time.sleep(1)
            init_autoexp_eyesis(str(i))
            init_autowb_eyesis(str(i))
    
else:
    log_msg(sys.argv[0]+": auto exposure and auto white balance")
    for i in range(1,5):
        if (switch['autoexp_daemon']==1) or (switch['autoexp']==1):
            init_autoexp_daemon(str(i-1))
        if switch['port'+str(i)]==1:
            if switch['autoexp']==1:
                sysfs_content = init_port_readsysfs("sensor"+str(i-1)+"0")
                if sysfs_content=="mt9p006":
                    init_autoexp(str(i-1))
            else:
                log_msg("Port "+str(i)+": skip autoexp")
                
            if switch['autowb']==1:
                sysfs_content = init_port_readsysfs("sensor"+str(i-1)+"0")
                if sysfs_content=="mt9p006":
                        init_autowb(str(i-1))
            else:
                log_msg("Port "+str(i)+": skip autowb")
if switch ['autocampars'] == 1:
#   shout("autocampars.php --init --ignore-revision")
    shout("autocampars.php --init")
    
#flips for eyesis head cams
if (switch['eyesis'] == 1) and (switch['framepars'] != 0):
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port=3&MULTI_FLIPV=4\"")
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port=2&MULTI_FLIPV=3\"")
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port=0&MULTI_FLIPV=4\"")
    shout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port=1&MULTI_FLIPV=3\"")

#6
if switch['sata']==1:
    log_msg("init SATA")
    init_sata(SATA_EN,PYDIR)
else:
    log_msg("skip SATA")
    

#7
if switch['gps']==1:
    log_msg('Start GPS and event logger')
    start_gps_compass()
else:
    log_msg("skip GPS")


# create directory for camogm pipes, symlink /var/state should already be in rootfs

if not os.path.exists("/var/volatile/state"):
    os.mkdir('/var/volatile/state')
else:
    log_msg ("/var/volatile/state already exists")

    
log_msg("DONE, log file: "+LOGFILE)
