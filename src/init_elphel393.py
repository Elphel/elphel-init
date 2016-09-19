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

import argparse
from argparse import RawTextHelpFormatter

import subprocess

parser = argparse.ArgumentParser(
    prog="init_elphel393.py",
    description="init script",
    usage="./init_elphel393.py or python init_elphel393.py",
    formatter_class=RawTextHelpFormatter
    )
args = parser.parse_args()

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
def chout(cmd):
    #subprocess.call prints to console
    subprocess.call(cmd,shell=True)

def init_ipaddr(ip):
    chout("ifconfig eth0 "+ip)
    
def init_mcntrl(pydir,verilogdir):
    chout(pydir+"/test_mcntrl.py @"+verilogdir+"/hargs")

def init_imgsrv(port):
    chout("imgsrv -p "+str(port))
    #restart PHP - it can get errors while opening/mmaping at startup, then some functions fail
    chout("killall lighttpd; /usr/sbin/lighttpd -f /etc/lighttpd.conf")
    chout("/www/pages/exif.php init=/etc/Exif_template.xml")

def init_autoexp_autowb(index):
    
    #mt9p006
    
    chout("wget -O /dev/null \"localhost/framepars.php?sensor_port="+str(index)+"&cmd=init\"")
    chout("autoexposure -p "+str(index)+" -c 0 -b 0 -d 1 &")
    chout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+str(index)+"&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3\"")
    chout("wget -O /dev/null \"localhost/parsedit.php?immediate&sensor_port="+str(index)+"&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x18000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000\"")

def init_sata(sata_en,pydir):
    if (sata_en==1):
        chout(pydir+"/x393sata.py")
        chout("modprobe ahci_elphel &")
        chout("sleep 2")
        chout("echo 1 > /sys/devices/soc0/amba@0/80000000.elphel-ahci/load_module")
    
#main
#1
print("Checkpoint 1: IP = "+IPADDR)
init_ipaddr(IPADDR)
#2
print("Checkpoint 2: mcntrl")
init_mcntrl(PYDIR,VERILOG_DIR)
#3
print("Checkpoint 3: imgsrv")
init_imgsrv(IMGSRV_PORT)
#4
print("Checkpoint 4: autoexposure and auto white balance")
for i in range(4):
    init_autoexp_autowb(i)
    
#5
print("Checkpoint 5: SATA")
init_sata(SATA_EN,PYDIR)
