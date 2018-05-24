
all:
	@echo "Welcome to the rp_powerbutton 'installer'"
	@echo "Normal installation procedure is to:"
	@echo "1. 'sudo make dep' to install any missing components (python-rpi.gpio, espeak)."
	@echo "2. 'sudo make install' to install pi_powerbutton itself."
	@echo "3. edit /etc/pi_powerbutton to desired settings. Defaults are ok for most situations."
	@echo "4. 'sudo service pi_powerbutton start' or just reboot the RPi entirely to enable pi_powerbutton."

	@echo "'sudo make uninstall' stops and uninstalls pi_powerbutton"

dep:
	apt-get update
	apt-get install python-rpi.gpio python3-rpi.gpio espeak

install:
	/bin/cp -n ./pi_powerbutton.cfg /etc/pi_powerbutton
	chown root.root /etc/pi_powerbutton

	mkdir -p /opt/pi_powerbutton/
	/bin/cp -rf ./pi_powerbutton.py /opt/pi_powerbutton/

	mkdir /opt/pi_powerbutton/locale/
	/bin/cp -rf ./locale/*.cfg /opt/pi_powerbutton/locale/

	/bin/cp -rf ./pi_powerbutton.rc /etc/init.d/pi_powerbutton
	chmod +x /etc/init.d/pi_powerbutton

	chown -r root.root /opt/pi_powerbutton/

	update-rc.d pi_powerbutton defaults

remove: uninstall

uninstall:
	service pi_powerbutton stop
	rm /etc/init.d/pi_powerbutton
	rm -rf /opt/pi_powerbutton/
	update-rc.d pi_powerbutton remove
