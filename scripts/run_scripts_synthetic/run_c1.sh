

TAG='cc'

echo "C1 - 551"
python3 client.py control --dump --notify --log_file c1_551_${TAG}_log --input_path  $HOME/Devel/control/input/551/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
sleep 600
python3 client.py control --dump --notify --log_file c1_551_${TAG}_log --input_path  $HOME/Devel/control/input/551/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
sleep 600
python3 client.py control --dump --notify --log_file c1_551_${TAG}_log --input_path  $HOME/Devel/control/input/551/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
sleep 600

#echo "C1 - 552"
#python3 client.py control --dump --notify --log_file c1_552_${TAG}_log --input_path  $HOME/Devel/control/input/552/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
#sleep 600
#python3 client.py control --dump --notify --log_file c1_552_${TAG}_log --input_path  $HOME/Devel/control/input/552/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
#sleep 600
#python3 client.py control --dump --notify --log_file c1_552_${TAG}_log --input_path  $HOME/Devel/control/input/552/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
#sleep 600
#
#echo "C1 - 553"
#python3 client.py control --dump --notify --log_file c1_553_${TAG}_log --input_path  $HOME/Devel/control/input/553/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
#sleep 600
#python3 client.py control --dump --notify --log_file c1_553_${TAG}_log --input_path  $HOME/Devel/control/input/553/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
#sleep 600
#python3 client.py control --dump --notify --log_file c1_553_${TAG}_log --input_path  $HOME/Devel/control/input/553/ --revocation_rate 0.0004761905	--resume_rate 0.0000000000
#sleep 600

