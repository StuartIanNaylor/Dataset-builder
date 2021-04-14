# Dataset-builder
KWS dataset builder for Google-streaming-kws

```
sudo apt update -y
sudo apt install -y python3-dev python3-pip python3-venv libatlas-base-dev libsndfile1 libportaudio2
python3 -m venv --system-site-packages ./venv
source ./venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt 
```

git pull origin master


If you want a CLI VU meter then `arecord -D plughw:1 -V mono -r 16000 -f S16_LE -c 1 /dev/null`


