MSG='''
\n\n
\t###########################################################################################################################################\n
\t\n\n POST_INSTALL  \n\n
\t 1. Install postgress\n
\t 2. Build a synthetic docker image\n
\t 3. Check NOKSLR tag
\n\n
\t###########################################################################################################################################\n
'''

echo $MSG


(cd setup/ami; sh install_postgres.sh)
(cd setup/docker/Docker; docker build -t synthetic .)

echo "CHECK NOKSLR"
cat /proc/cmdline


echo "CHECK SSH MAXSession and Keep ALive!"
