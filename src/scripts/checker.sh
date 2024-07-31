if ! pgrep -f "/home/zat/Scripts/modbustest.py" &>/dev/null; then
	if ! pgrep -f "/home/zat/Scripts/zatpi/main.py" &>/dev/null; then
		killall python
	        /home/zat/Scripts/start.sh &
	else
               sudo -u zat python /home/zat/Scripts/modbustest.py >> /dev/null &
        fi
elif ! pgrep -f "/home/zat/Scripts/zatpi/main.py" &>/dev/null; then
	killall python
	/home/zat/Scripts/start.sh &
fi


