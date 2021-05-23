
MSG='''
\n\n
\t###########################################################################################################################################\n
\tThat script installs all dependencies and prepares all files and default folders to execute the Hibernation Aware Dynamic Scheduler (HADS).\n\n
\tPlease check all vars before start it.\n\n
\tThe script works well on: Ubuntu 18.04.\n
\t###########################################################################################################################################\n
'''

echo $MSG

GIT_ACCOUNT=luanteylo
BRANCH=ipdps
PROJECT_NAME=control


DEVEL_PATH=$HOME/Devel
HADS_PATH="$HOME/Devel/$PROJECT_NAME"

echo $DEVEL_PATH
echo $HADS_PATH

sudo apt -y update
sudo apt -y install git


echo "creating folders"

mkdir -p $HADS_PATH


echo "installing"

(cd $DEVEL_PATH/; git clone https://github.com/$GIT_ACCOUNT/$PROJECT_NAME; cd $HADS_PATH; git checkout $BRANCH)

(cd $HADS_PATH/scripts/setup; sh install_worker.sh)

echo -n "Do you wish to reboot(y/n)? "
read answer

if [ "$answer" != "${answer#[Yy]}" ] ;then
    sudo reboot -h 0
fi
