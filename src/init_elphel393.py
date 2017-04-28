#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

''' 
/**
 * @file init_elphel393.py
 * @brief 10393 related init script
 * @copyright Copyright (C) 2016 Elphel Inc.
 * @author Oleg Dzhimiev <oleg@elphel.com>
 * @deffield updated: unknown
 *
 * @par <b>License</b>:
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
'''

__author__ = "Oleg Dzhimiev"
__copyright__ = "Copyright (C) 2016 Elphel, Inc."
__license__ = "GPL"
__version__ = "3.0+"
__maintainer__ = "Oleg Dzhimiev"
__email__ = "oleg@elphel.com"
__status__ = "Development"

import subprocess
import sys
import time
import os

#params
SENSOR_TYPE = 5
IPADDR = "192.168.0.9"
NETMASK = "255.255.255.0"
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
    '''
    Get fpga bitstream version once it's available
    @timeout - int - seconds
    '''
    ntry = 0
    fpga = None
    while not fpga and ((not timeout) or (ntry<timeout)):
        fpga = get_fpga()
        print ('.',end='')
        sys.stdout.flush()
        ntry += 1
        time.sleep(1)
    return fpga        
    
def colorize(string, color, bold):
    '''
    Colors for terminal output
    @string - string - text to print
    @color - string - see below
    @bold - bool - True/False
    '''  
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

def log_msg(msg, mode=0):
    '''
    Print log message
    @msg
    @mode - int - 0,2,3,4
    '''  
    bold = False
    color = ""
    if mode == 2: #bold red - error
        color = "RED"
        bold = True
    elif mode == 3: # just bold
        bold = True
    elif mode == 4: # just bold
        bold = True
        color = "YELLOW" #warning
            
    with open ('/proc/uptime') as f: 
        t=float(f.read().split()[0])
    with open(LOGFILE,'a') as msg_file:
        print("[%8.2f]  %s"%(t,msg),file=msg_file)
    if bold or color:
        msg = colorize(msg,color,bold)    
    print (colorize("[%8.2f] %s: "%(t, sys.argv[0].split('/')[-1].split('.')[0]),'CYAN',0)+msg)

def shout(cmd):
    '''
    call subprocess with shell=True
    @cmd
    '''  
    #subprocess.call prints to console
    subprocess.call(cmd,shell=True)

def init_ipaddr(ip, mask):
    '''
    simple 'ifconfig'
    @ip - string - ip address
    @mask - string - netmask
    '''  
    shout("ifconfig eth0 "+ip+" netmask "+mask)

def init_imgsrv(port):
    '''
    Start Image Server (imgsrv), restart lighttpd (for imgsrv?) and initialize exif header template
    @port - int or str
    '''   
    shout("imgsrv -p "+str(port))
    #restart PHP - it can get errors while opening/mmaping at startup, then some functions fail
    shout("killall lighttpd; /usr/sbin/lighttpd -f /etc/lighttpd.conf")
    shout("/www/pages/exif.php init=/etc/Exif_template.xml")
            
def init_autoexp_daemon(index):
    '''
    Start autoexposure daemon, provide port
    @index - string
    '''  
    shout("autoexposure -p "+index+" -c 0 -b 0 -d 1 &")

def init_sata(sata_en):
    '''
    SATA init
    @sata_en - int - 0 or 1
    '''  
    # init SATA only if 10389 board is present
    if os.path.isfile("/sys/devices/soc0/elphel393-pwr@0/detected_10389"):
        if (sata_en==1):
            # SATA core is implented in fpga - first chech, then wait until programmed
            if not get_fpga():
                log_msg ("Waiting for the FPGA to be programmed to start SATA", 4)
                # look up TIMEOUT in the params in the beginning of the file
                if not fpga_OK(TIMEOUT):
                    log_msg ("Timeout while waiting for the FPGA to be programmed", 2)
                    return
                else:
                    log_msg ("Done waiting for the FPGA", 4)
                    
            # default init will connect to internal SSD
            shout(PYDIR+"/x393sata.py")  # Should be after modprobe? Wait for the FPGA should be before it
            
            # for Eyesis4Pi (temporary fix)
            if switch['eyesis']!=0:
              
              log_msg ("Setting VSC3304 for Eyesis4Pi (driver will be loaded)", 4)
              log_msg ("  Details : /var/log/x393sata_control.log")
              log_msg ("  State   : /var/state/ssd")
              
              # Option 1: use internal SSDs: zynq <-> internal ssd, AHCI module will be loaded by the script
              # uncomment for use
              #shout(PYDIR+"/x393sata_control.py set_zynq_ssd")
              
              # Option 2: use external SSDs: zynq <-> external ssd, AHCI module will be loaded by the script
              # uncomment for use
              shout(PYDIR+"/x393sata_control.py set_zynq_esata")
            else:
              # load the AHCI driver module
              shout("modprobe ahci_elphel &")
              shout("sleep 2")
              shout("echo 1 > /sys/devices/soc0/amba@0/80000000.elphel-ahci/load_module")
    else:
        log_msg ("10389 was not detected: skipping SATA init")

def init_usb_hub():
    '''
    Initializes USB HUB on 10389 board (stays initialized through reboot, does not respond after initialized)
    '''
    if not os.path.exists('/sys/bus/usb/devices/1-1'):
        if os.path.isfile('/sys/devices/soc0/elphel393-pwr@0/detected_10389'):
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
            log_msg ("10389 was not detected: skipping USB hub init")
    else:
        log_msg ("USB hub was already initialized")

def start_gps_compass():
    '''
    Detect GPS and/or compass boards and start them
    '''
    if not get_fpga():
        log_msg ("Waiting for the FPGA to be programmed to start SATA", 4)
        if not fpga_OK(TIMEOUT):
            print()
            log_msg ("Timeout while waiting for the FPGA to be programmed", 2)
            return
        else:
            log_msg ("Done waiting for the FPGA", 4)
    shout("start_gps_compass.php")
    
def disable_gpio_10389():
    '''
    Is needed for Eyesis4Pi because GPIO is used to power something else
    '''
    gpio_10389 = "/sys/devices/soc0/elphel393-pwr@0/gpio_10389"
    shout("echo '0x101' > "+gpio_10389) #power on
    shout("echo '0x100' > "+gpio_10389) #power off
    time.sleep(1)

#main

# default
switch = {
    'usb_hub':1,
    'ip':1,
    'imgsrv':1,
    'autoexp_daemon':1,
    'autocampars':1,
    'sata':1,
    'gps':1,
    'eyesis':0
    }

# update 'switch' dictionary from argv[1] which should be evaluated as dictionary as well:
# look it up in /etc/init.d/init_elphel393
if len(sys.argv) > 1:
    switch.update(eval(sys.argv[1]))
    
#pre
volatile_html = '/var/volatile/html'
if not os.path.exists(volatile_html):
    os.mkdir(volatile_html)

# need to disable fan for eyesis
# if switch['eyesis']!=0:
#    log_msg('Eyesis mode: turn off gpio 10389')
#    disable_gpio_10389()

# Start temperature monitor and let it control fan (set 'off' to disable fan control)
# Move tempon early, so other problems will not block it
if switch['eyesis']!=0:
    log_msg('Eyesis mode: turn off gpio 10389')
    disable_gpio_10389()
    log_msg("Eyesis: fan off")
    shout("tempmon.py --control_fan off &")
else:
    log_msg("Fan on")
    shout("tempmon.py --control_fan on &")

'''
1: program USB hub
'''
if switch['usb_hub']==1:
    log_msg('Initialize USB hub')
    init_usb_hub()
else:
    log_msg("skip USB hub initiualization")

'''
2: set ip and netmask
'''
if switch['ip']==1:
    log_msg(sys.argv[0]+": ip = "+IPADDR+", mask = "+NETMASK)
    init_ipaddr(IPADDR, NETMASK)
else:
    log_msg("skip ip")
    
'''
3: init image server
'''
if switch['imgsrv']==1:
    log_msg(sys.argv[0]+": imgsrv")
    init_imgsrv(IMGSRV_PORT)
else:
    log_msg("skip imgsrv")

'''
4: init autoexposure daemon - try for all possible ports
'''
log_msg(sys.argv[0]+": auto exposure daemon")
if switch['autoexp_daemon']==1:
    for i in range(1,5):
        init_autoexp_daemon(str(i-1))

'''
5: Init camera parameters
   * FPGA gets programmed at this step - default bitstream is used which
     depends on the camera type programmed in 10389 if detected.
     If the board is not found then the default bitstream is:
     /usr/local/verilog/x393_parallel.bit
'''
if switch ['autocampars'] == 1:
#   shout("autocampars.php --init --ignore-revision")
    shout("autocampars.php --init")

'''
6: Init SATA
   * If the bitstream wasn't programmed at the previous step
     it will be programmed here by x339sata.py,
     the default bitstream is /usr/local/verilog/x393_sata.bit
     but it does not include the camera part
'''
if switch['sata']==1:
    log_msg("init SATA")
    init_sata(SATA_EN)
else:
    log_msg("skip SATA")
    

'''
7: Start GPS/IMU if any detected
'''
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

    
log_msg("DONE, log file: "+LOGFILE, 3)
