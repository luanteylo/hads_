MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n
\t SETUP HIBERNATION FEATURE
\t\n\n
\t###########################################################################################################################################\n
'''

echo $MSG

sudo apt -y update
sudo apt -y dist-upgrade

sudo apt install -y ec2-hibinit-agent

echo "Disabling KASLR"
#sudo reboot
printf "
	# Cloud Image specific Grub settings for Generic Cloud Images\n
	# CLOUD_IMG: This file was created/modified by the Cloud Image build process\n
	# Set the recordfail timeout\n
	GRUB_RECORDFAIL_TIMEOUT=0\n
	# Do not wait on grub prompt\n
	GRUB_TIMEOUT=0\n
	# Set the default commandline\n
	GRUB_CMDLINE_LINUX_DEFAULT=\"console=tty1 console=ttyS0 nvme_core.io_timeout=4294967295 nokaslr\"\n
	# Set the grub console type\n
	GRUB_TERMINAL=console\n
	GRUB_HIDDEN_TIMEOUT=0.1\n
"  | sudo tee  /etc/default/grub.d/50-cloudimg-settings.cfg > /dev/null

sudo update-grub