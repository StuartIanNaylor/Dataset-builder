# Dataset-builder
KWS dataset builder for Google-streaming-kws

```
sudo apt update -y
sudo apt install -y python3-dev python3-pip python3-venv libsndfile1 libportaudio2 libsox-fmt-all ffmpeg sox bc
python3 -m venv --system-site-packages ./venv
source ./venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt 
```

If you want a CLI VU meter then adapt to suit `arecord -D plughw:1 -V mono -r 16000 -f S16_LE -c 1 /dev/null`

If you are struggling with your alsa setting `./alsa.sh` will create a /etc/asound.conf for you

# Usage
Still a very linear hack but will relatively quickly produce a dataset of 1000 samples of KW from a few recordings.

Start with `python3 record.py` you can do a `python3 record.py -h` if you wish to change any parameters from default
For the notkw try and find sentences that contain as many phones and alophones in as short as sentence as possible.
It doesn't actually have to make grammatic sense just choice words.

Always try and record on the device of use and maybe record 2 batches 'close' 0 - 0.3m from mic and far => 3m.
If your mic is insensitive reduce the distance the proximity effect of unidirectionals and room echo will benefit 
from recording those sounds patterns but if not just record a single batch 'close' to the mic of use.

Examples of phonetic pangrams can be found at http://clagnut.com/blog/2380/#English_phonetic_pangrams and the more the 
variation of sounding in phones and allophones the better.

The results will be stored in /rec and you may want to do a quick quality check.

Also whilst speaking the words try to voice them as individual words than as sentences.
The next part 'split' is a simple silence dectector but its strange how unnatural it is to put in even short pauses in a spoken sentence.

So its record keywords and say 20-40 keywords with a slight pause between them.
Read out some notkeyword sentences again with pauses again trying to garner at least 20-40 words
Silence is used as a threhold reference and also as a background file so if you can be patient try to at least add 90 secs of normal silence 
room silence.
Whatever you normal room silence is without sparadic noises, bangs, coughs or key presses.

You might want to review those files with audacity or some other editor just to check also some soundcards are worse then others for start and end 'clicks'

Next run `python3 split.py` again you can do a `python3 split.py -h` if you wish to change from default parameters.
Before you do to add more variation to background-noise create a '_background_noise_' dir and add some applicable noise files an example zip can downloaded from 
https://drive.google.com/file/d/1qyV2hsM8ODbfyFHdc_L0PrfEOcdWqr_F/view?usp=sharing 
Split will then split your recorded sentences into words and background & silence files into 1-sec samples.
The destination folder is '/splits' and check that they silence threshold has sucessfully managed to split the words correctly.

Finally run `python3 mix.py` again you can do a `python3 mix.py -h` if you wish to change from default parameters.
This will mix background noises into your word samples whilst also mixing in silence at the level of record to pad out your word splits.
Background noise is a random range based on the amplitude of the word sample where 1.0 means if random.random() does produce a 1 then 
background noise and word volume will be the same the default is 0.5

Finally you will then have a /dataset directory containing /testing, /training & / validation directories that default to a proportional split of 10% testing and 10% training.
In those folders the wanted-words directories of /kw, /notkw & /silence where /notkw & /silence are percentages of /kw 50% & 30% defaults respectively.
Changes in percentage can greatly affect inference weighting and you can change this to affect inference results.

This is just a hacky script as the Googleresearch_streaming_kws (https://github.com/google-research/google-research/tree/master/kws_streaming) 
auto dataset controls do not match the levels of background_noise and kw or notkw so it limits the ability to vary 
kw & notkw volume and also limits the range of background noise as otherwise background_noise will be in the forgeground of non background_noise classifactions.
You can use the Googleresearch_streaming_kws but with these scripts louder volumes of background noise can be used and should be more accurate.
Also the variation effects to create a 1000 or more samples from as low as an initial 20 can be used with Googleresearch_streaming_kws auto dataset byt just a copy and paste.

To use a folder based dataset set the Googleresearch_streaming_kws paramters to --data_dir /data --wanted_words up,down --split_data 0 and cancel any variations effects as they are already done.

You can try and my basic adaption and install instructions from https://github.com/StuartIanNaylor/g-kws

There is a sample background_noise folder here with additional samples where you should add your own silence files, the 4 silence files where just copies to add a higher proportion of silence as background_noise. Overwrite with ours and add any non spoken noise you may think will help with your environ.
https://drive.google.com/file/d/1qyV2hsM8ODbfyFHdc_L0PrfEOcdWqr_F/view?usp=sharing


