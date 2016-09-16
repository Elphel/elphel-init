SYSCONFDIR=$(DESTDIR)/etc
INITDIR=$(DESTDIR)/etc/init.d
MODPROBEDIR=$(SYSCONFDIR)/modprobe.d
DRIVER_NAME=ahci_elphel
CONFDIR=$(SYSCONFDIR)/elphel393

OWN = -o root -g root

INSTALL = install
INSTMODE   = 0755

SCRIPT1=init_elphel393.sh
SCRIPT2=init_elphel393

all:
	@echo "make all in src"

install:
	@echo "make install in src"
	# below depends on Yocto and the corresponding recipe (meta-core/init/init.bb)

	sed -e 's/192.168.0.9/$(REMOTE_IP)/' $(SCRIPT1) > $(SCRIPT1).tmp
	$(INSTALL) $(OWN) -d $(CONFDIR)
	$(INSTALL) $(OWN) -m $(INSTMODE) $(SCRIPT1).tmp $(CONFDIR)/$(SCRIPT1)
	rm $(SCRIPT1).tmp

	#INITSTRING default is defined in local.conf, weak default - meta-core/init/init.bb
	sed -e 's/init_elphel393.sh/$(INITSTRING)/' $(SCRIPT2) > $(SCRIPT2).tmp
	$(INSTALL) $(OWN) -d $(INITDIR)
	$(INSTALL) $(OWN) -m $(INSTMODE) $(SCRIPT2).tmp $(INITDIR)/$(SCRIPT2)
	rm $(SCRIPT2).tmp
	
	# blacklist AHCI driver to prevent it from loading before FPGA is configured
	$(INSTALL) $(OWN) -d $(MODPROBEDIR)
	echo "blacklist $(DRIVER_NAME)" >> $(MODPROBEDIR)/blacklist.conf

clean:
	@echo "make clean in src"