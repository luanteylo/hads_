TAG='cc'

echo "Baseline - xx 551"

python3 client.py control --dump --notify --log_file baseline_${TAG}_551 --input_path  $HOME/Devel/control/input/551/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600
python3 client.py control --dump --notify --log_file baseline_${TAG}_551 --input_path  $HOME/Devel/control/input/551/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600
python3 client.py control --dump --notify --log_file baseline_${TAG}_551 --input_path  $HOME/Devel/control/input/551/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600

echo "Baseline - 552"
python3 client.py control --dump --notify --log_file baseline_${TAG}_552 --input_path  $HOME/Devel/control/input/552/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600
python3 client.py control --dump --notify --log_file baseline_${TAG}_552 --input_path  $HOME/Devel/control/input/552/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600
python3 client.py control --dump --notify --log_file baseline_${TAG}_552 --input_path  $HOME/Devel/control/input/552/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600

echo "Baseline - 553"
python3 client.py control --dump --notify --log_file baseline_${TAG}_553 --input_path  $HOME/Devel/control/input/553/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600
python3 client.py control --dump --notify --log_file baseline_${TAG}_553 --input_path  $HOME/Devel/control/input/553/ --revocation_rate 0.0	--resume_rate 0.0
sleep 600
python3 client.py control --dump --notify --log_file baseline_${TAG}_553 --input_path  $HOME/Devel/control/input/553/ --revocation_rate 0.0	--resume_rate 0.0


