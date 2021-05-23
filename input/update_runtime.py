import json

times = {
    '1000': 304.0,
    '600': 260.0,
    '400': 119.0
}

# Update env file
with open("/home/luan/Devel/control/input/553/job.json", "r") as jsonFile:
    data = json.load(jsonFile)

# updating prices on env_file
tmp = data["tasks"]

for id in tmp:
    size = tmp[id]['command'].split()[-1]
    tmp[id]['runtime']['t3.xlarge'] = times[size]

data["tasks"] = tmp

with open("/home/luan/Devel/control/input/553/job.json", "w") as jsonFile:
    json.dump(data, jsonFile, sort_keys=False, indent=4, default=str)
