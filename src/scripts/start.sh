sudo mount /dev/sda1 /media/zat/usb
sudo ip route add 192.167.10.0/24 dev eth1
sudo chmod 777 /dev/tty7
sleep 20
python /home/zat/Scripts/modbustest.py >> /dev/null &
sudo -u zat startx  /usr/bin/python /home/zat/Scripts/zatpi/main.py -- vt7
killall python

