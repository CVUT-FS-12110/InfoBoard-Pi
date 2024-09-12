#!/usr/bin/env bash

PWD=$(pwd)

if [ ! -f "$PWD"/src/infoboard/configuration.py ]; then
  echo "Infoboard Pi source code doesn't found, start thi script inside the repository directory."
  exit
else
  echo "Infoboard Pi source code found"
fi

echo "Installing services"

sudo cp "$PWD"/src/scripts/infoboard-pi.service /etc/systemd/system/infoboard-pi.service
sudo cp "$PWD"/src/scripts/infoboard-pi-server.service /etc/systemd/system/infoboard-pi-server.service

sudo rm /usr/local/sbin/infoboardPi.sh
sudo rm /usr/local/sbin/infoboardPiServer.sh

echo exec "$PWD"/src/scripts/start.sh | sudo tee -a /usr/local/sbin/infoboardPi.sh
echo exec "$PWD"/src/scripts/check_server.sh | sudo tee -a /usr/local/sbin/infoboardPiServer.sh

sudo systemctl daemon-reload