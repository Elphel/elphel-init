SYSCONFDIR=$(DESTDIR)/etc
INITDIR=$(DESTDIR)/etc/init.d
MODPROBEDIR=$(SYSCONFDIR)/modprobe.d
DRIVER_NAME=ahci_elphel
CONFDIR=$(SYSCONFDIR)/elphel393

STATEDIR = $(DESTDIR)/var/volatile/state
STATELINK = $(DESTDIR)/var/state
LINK = ln

OWN = -o root -g root

INSTALL = install
INSTMODE   = 0755

SCRIPT1=init_elphel393.py
SCRIPT2=init_elphel393
 # init_elphel393.sh is used for Eyesis 12-sensors
SCRIPT3=init_elphel393.sh
SCRIPT4=init_eyesis_bottom2.sh

all:
	@echo "make all in src"

install:
	@echo "make install in src"
	# below depends on Yocto and the corresponding recipe (meta-core/init/init.bb)

	sed -e 's/192.168.0.9/$(REMOTE_IP)/' $(SCRIPT1) > $(SCRIPT1).tmp
	$(INSTALL) $(OWN) -d $(CONFDIR)
	$(INSTALL) $(OWN) -m $(INSTMODE) $(SCRIPT1).tmp $(CONFDIR)/$(SCRIPT1)
	rm $(SCRIPT1).tmp

	sed -e 's/192.168.0.9/$(REMOTE_IP)/' $(SCRIPT3) > $(SCRIPT3).tmp
	$(INSTALL) $(OWN) -d $(CONFDIR)
	$(INSTALL) $(OWN) -m $(INSTMODE) $(SCRIPT3).tmp $(CONFDIR)/$(SCRIPT3)
	rm $(SCRIPT3).tmp

	sed -e 's/192.168.0.9/$(REMOTE_IP)/' $(SCRIPT4) > $(SCRIPT4).tmp
	$(INSTALL) $(OWN) -d $(CONFDIR)
	$(INSTALL) $(OWN) -m $(INSTMODE) $(SCRIPT4).tmp $(CONFDIR)/$(SCRIPT4)
	rm $(SCRIPT4).tmp
	
	
	#INITSTRING default is defined in local.conf, weak default - meta-core/init/init.bb
	sed -e 's/init_elphel393.py/$(INITSTRING)/' $(SCRIPT2) > $(SCRIPT2).tmp
	$(INSTALL) $(OWN) -d $(INITDIR)
	$(INSTALL) $(OWN) -m $(INSTMODE) $(SCRIPT2).tmp $(INITDIR)/$(SCRIPT2)
	rm $(SCRIPT2).tmp
	
	# blacklist AHCI driver to prevent it from loading before FPGA is configured
	$(INSTALL) $(OWN) -d $(MODPROBEDIR)
	echo "blacklist $(DRIVER_NAME)" >> $(MODPROBEDIR)/blacklist.conf
	
	# create directories to support legacy scripts
	$(INSTALL) $(OWN) -d $(STATEDIR)
	$(LINK) -s -r $(STATEDIR) $(STATELINK)

clean:
	@echo "make clean in src"
