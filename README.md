# mssql2sendpulse

### Linux distribution
Ubuntu 18.04

### Install basic requirements
```
sudo apt-get install git nano \
  build-essential libssl-dev libffi-dev uuid-dev libcap-dev libpcre3-dev \
  freetds-dev freetds-bin unixodbc unixodbc-dev tdsodbc -y \
  python3-pip python3.6 python3.6-dev -y
```

### Install pipenv
```
sudo pip3 install pipenv
```

### Initialize virtualenv
```
pipenv shell --python 3.6
```

### Install python requirements
```
pipenv install
```

### Configure cron jobs

Open cron config
```
crontab -e
```

Run jobs every hour
```
0 * * * * /home/user/.local/share/virtualenvs/mssql2sendpulse-OYLWRT-f/bin/python /home/user/projects/esputnik/send_client_info_bulk.py
0 * * * * /home/user/.local/share/virtualenvs/mssql2sendpulse-OYLWRT-f/bin/python /home/user/projects/esputnik/send_contact_info_bulk.py
```
