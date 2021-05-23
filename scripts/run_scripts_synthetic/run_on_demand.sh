

echo "Baseline - 551"
python3 client.py control --dump --notify --log_file on_demand_551 --input_path  $HOME/Devel/control/input/551/ --map_file map_ondemand.json --revocation_rate 0.0	--resume_rate 0.0
sleep 100

echo "Baseline - 552"
python3 client.py control --dump --notify --log_file on_demand_552 --input_path  $HOME/Devel/control/input/552/ --map_file map_ondemand.json --revocation_rate 0.0	--resume_rate 0.0
sleep 100

echo "on-demand - 553"
python3 client.py control --dump --notify --log_file on_demand_553 --input_path  $HOME/Devel/control/input/553/ --map_file map_ondemand.json --revocation_rate 0.0	--resume_rate 0.0
