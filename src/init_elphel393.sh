#/bin/sh
#ifconfig eth0 down
#ifconfig eth0 hw ether 00:0e:64:10:00:02 192.168.0.7

# select sensor type: 5 Mpx (set 5) or 14 Mpx (set 14)
# 14MPix does not work with framepars & parsedit!!!
SENSOR_TYPE=5
# imgsrv port number 
IMGSRV_PORT=2323
# camogm port number
CAMOGM_PORT=3456
# camogm command pipe name
CAMOGM_PIPE=/var/volatile/camogm_cmd
# enable SATA, set this to 1 if camera is equipped with SSD drive
SATA_EN=1

#IP will be modified to the $(REMOTE_IP) by the Makefile during install. You may change it in your 
ifconfig eth0 192.168.0.9

PYDIR=/usr/local/bin
VERILOG_DIR=/usr/local/verilog
$PYDIR/test_mcntrl.py @${VERILOG_DIR}/hargs
echo imgsrv -p 2323
imgsrv -p 2323
#restart PHP - it can get errors while opening/mmaping at startup, then some functions fail
killall lighttpd; /usr/sbin/lighttpd -f /etc/lighttpd.conf
/www/pages/exif.php init=/etc/Exif_template.xml

echo "init sensor port"

wget -O /dev/null "localhost/framepars.php?sensor_port=0&cmd=init"
wget -O /dev/null "localhost/framepars.php?sensor_port=1&cmd=init"
wget -O /dev/null "localhost/framepars.php?sensor_port=2&cmd=init"
wget -O /dev/null "localhost/framepars.php?sensor_port=3&cmd=init"

echo "start autoexposure daemons on each sensor port"
autoexposure -p 0 -c 0 -b 0 -d 1 &
autoexposure -p 1 -c 0 -b 0 -d 1 &
autoexposure -p 2 -c 0 -b 0 -d 1 &
autoexposure -p 3 -c 0 -b 0 -d 1 &

echo "Set autoexposure parameters and enable autoesposure for each sensor port, delay startup of daemon until enough frames are acquired"

wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=0&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3"
wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=1&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3"
wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=2&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3"
wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=3&COMPRESSOR_RUN=2&DAEMON_EN=1*12&AUTOEXP_ON=1&AEXP_FRACPIX=0xff80&AEXP_LEVEL=0xf800&AE_PERIOD=4&AE_THRESH=500&HIST_DIM_01=0x0a000a00&HIST_DIM_23=0x0a000a00&EXP_AHEAD=3"

echo "set up white balance parameters"

wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=0&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x18000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000"
wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=1&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x18000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000"
wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=2&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x18000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000"
wget -O /dev/null "localhost/parsedit.php?immediate&sensor_port=3&COMPRESSOR_RUN=2&DAEMON_EN=1&WB_EN=0x1&WB_MASK=0xd&WB_PERIOD=16&WB_WHITELEV=0xfae1&WB_WHITEFRAC=0x028f&WB_SCALE_R=0x10000&WB_SCALE_GB=0x10000&WB_SCALE_B=0x10000&WB_THRESH=500&GAIN_MIN=0x18000&GAIN_MAX=0xfc000&ANA_GAIN_ENABLE=1&GAINR=0x10000&GAING=0x10000&GAINGB=0x10000&GAINB=0x10000"

if [ $SATA_EN -eq 1 ]; then
    $PYDIR/x393sata.py
    modprobe ahci_elphel &
    sleep 2
    echo 1 > /sys/devices/soc0/amba@0/80000000.elphel-ahci/load_module
fi

echo "/etc/init_elphel393.sh done"
exit 0
