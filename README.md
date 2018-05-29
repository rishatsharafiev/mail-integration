# mssql2sendpulse

### Linux distribution
Ubuntu 18.04

### Install basic requirements
sudo apt-get install \
  && build-essential libssl-dev libffi-dev uuid-dev libcap-dev libpcre3-dev \
  && freetds-dev freetds-bin unixodbc unixodbc-dev tdsodbc -y \
  && python3-pip python3.6 python3.6-dev \
  && git nano -y

### Install pipenv
sudo pip3 install pipenv
