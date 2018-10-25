#!/usr/bin/env python

from __future__ import division
from __future__ import print_function

'''
/**
 * @file generate_default_network_interfaces.py
 * @brief - Generate the default /etc/network/interfaces file
 *          based on the Elphel's Poky config: poky/build/conf/local.conf
 *          which contains ip address (and network mask)
 *        - Install into rootfs
 * @copyright Copyright (C) 2018 Elphel Inc.
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

__copyright__ = "Copyright (C) 2018 Elphel, Inc."
__license__ = "GPL-3.0-or-later"
__maintainer__ = "Oleg Dzhimiev"
__email__ = "oleg@elphel.com"

'''
Usage (command line):
  ~$ generate_default_network_interfaces.py <ipaddr> <netmask> <gateway>
Example:
  ~$ generate_default_network_interfaces.py 192.168.0.9 255.255.255.0 192.168.0.15
'''

import os
import sys

path = "generated"
filepath = os.path.join(path,"interfaces")

ip      = "192.168.0.9"
mask    = "255.255.255.0"
gateway = "192.168.0.15"

# in python 3 it's a single line:
#     os.makedirs(path, exist_ok=True)
try:
  os.makedirs(path)
except OSError:
  if not os.path.isdir(path):
    raise

try:
  ip = sys.argv[1]
except:
  pass

try:
  mask = sys.argv[2]
except:
  pass

try:
  gateway = sys.argv[3]
except:
  pass

with open(filepath,"w") as f:
    f.write("""\
# This is an auto-generated file created by a script that is run from
# Elphel's Yocto Poky framework setup.
#
# See
#   project: https://git.elphel.com/Elphel/elphel-init
#   file   : src/generate_default_network_interfaces.py
#

# /etc/network/interfaces -- configuration file for ifup(8), ifdown(8)

auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address {0}
    netmask {1}
    gateway {2}
""".format(ip,mask,gateway))




























