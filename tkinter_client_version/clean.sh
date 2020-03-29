
if [[ $(lsof -t -i:33008) ]]; then
    kill -9 $(lsof -t -i:33008)
fi
pkill -f client.py