killall -9 python 2> /dev/null
nohup python server/main.py $@ &
