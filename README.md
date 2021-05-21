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

Start with `python3 reader.py` you can do a `python3 reader.py -h` if you wish to change any parameters from default
For the notkw try and find sentences that contain as many phones and alophones in as short as sentence as possible.
It doesn't actually have to make grammatic sense just choice words but currently there is just a collection of
6 'sentence files' which are prompted in steps of 2 to read more for accuracy.

Always try and record on the device of use and maybe record 2 batches 'close' 0 - 0.3m from mic and far => 3m.
If your mic is insensitive reduce the distance the proximity effect of unidirectionals and room echo will benefit 
from recording those sounds patterns but if not just record a single batch 'close' to the mic of use.
You can start with just 2 sentences recorded a close <0.3m to the mic as the datset is designed to be replaced through use.
So its a starter dataset and the fractional accuracy increases may not be worth the effort.

Examples of phonetic pangrams can be found at http://clagnut.com/blog/2380/#English_phonetic_pangrams and the more the 
variation of sounding in phones and allophones the better.

The results will be stored in /rec and you may want to do a quick quality check.

Also whilst speaking the words try to voice them as individual words than as sentences and try different innotations.
Happy, sad, bored, tired, alert try to vary your innoation but try to stay natural than maybe operatic renditions also.


The reader will prompt you for your KW and alternate betwwen KW & '!KW words' to try and make things less monotonous.
Silence is used as a threhold reference and also as a background file so if you can be patient try to keep silent for
the last operation of 60 seconds of silence.
Whatever you normal room silence is without sparadic noises, bangs, coughs or key presses.

You might want to review those files with audacity or some other editor just to check also some soundcards are worse then others for start and end 'clicks'

The dataset expects a folder of background_noise where an example is created below and also your silence files are added to.
Before you do to add more variation to background-noise create a '_background_noise_' dir and add some applicable noise files an example zip can downloaded from 
https://drive.google.com/file/d/1mV_opi70qu-mCLid7CsB4BJDoX5nfdOi/view?usp=sharing 

This selection may also be usefull.

https://drive.google.com/file/d/11IAG4wrbDHuMPVjvj5NQXnohO7lXNeCa/view?usp=sharing

https://drive.google.com/file/d/1yFNr3ruezx0XDB0fTxsytR7eK3CjV8fZ/view?usp=sharing


Finally run `python3 mix.py` again you can do a `python3 mix.py -h` if you wish to change from default parameters.
This will mix background noises into your word samples whilst also mixing in silence at the level of record to pad out your word splits.
Background noise is a random range based on the amplitude of the word sample where 1.0 means if random.random() does produce a 1 then 
background noise and word volume will be the same the default is 0.5

Finally you will then have a /dataset directory containing /testing, /training & / validation directories that default to a proportional split of 10% testing and 10% validation.
In those folders the wanted-words directories of /kw, /notkw & /silence where /notkw & /silence are percentages of /kw.
The minimum samples is set `--min_samples` where validation and testing need approx 200 samples to lessen the probability of look and provide reasonable validation to a dataset.
Lowering to the minimum due to batch size of 100 will increase slightly the return chance of early validation results without true classification process.
Increasing min_samples makes a more robust validation and testing cycle but approx 200 seems enough.

This is just a hacky script as the Googleresearch_streaming_kws (https://github.com/google-research/google-research/tree/master/kws_streaming) 
auto dataset controls do not match the levels of background_noise and kw or notkw so it limits the ability to vary 
kw & notkw volume and also limits the range of background noise as otherwise background_noise will be in the forgeground of non background_noise classifactions.
You can use the Googleresearch_streaming_kws but with these scripts louder volumes of background noise can be used and should be more accurate.
Also the variation effects to create a 1000 or more samples from as low as an initial 20 can be used with Googleresearch_streaming_kws auto dataset byt just a copy and paste.

To use a folder based dataset set the Googleresearch_streaming_kws paramters to --data_dir /data --wanted_words up,down --split_data 0 and cancel any variations effects as they are already done.

You can try and my basic adaption and install instructions from https://github.com/StuartIanNaylor/g-kws

There is a sample background_noise folder here with additional samples where you should add your own silence files, the 4 silence files where just copies to add a higher proportion of silence as background_noise. Overwrite with ours and add any non spoken noise you may think will help with your environ.
https://drive.google.com/file/d/1mV_opi70qu-mCLid7CsB4BJDoX5nfdOi/view?usp=sharing and here 

https://drive.google.com/file/d/1qmbm7yur8GfICOvyUfvBY6c7vXV8yVem/view?usp=sharing

https://drive.google.com/file/d/1pa58ERBdp4UijRUGEDBQjFv7jIKUROqx/view?usp=sharing
```
python3 mix.py --help
usage: mix.py [-h] [-b BACKGROUND_DIR] [-r REC_DIR] [-R BACKGROUND_RATIO] [-d BACKGROUND_DURATION] [-p PITCH] [-t TEMPO] [-D DESTINATION]
              [-a FOREGROUND_ATTENUATION] [-A BACKGROUND_ATTENUATION] [-B BACKGROUND_PERCENT] [-T TESTING_PERCENT] [-v VALIDATION_PERCENT]
              [-S SILENCE_PERCENT] [-n NOTKW_PERCENT] [-s FILE_MIN_SILENCE_DURATION] [-H SILENCE_HEADROOM] [-m MIN_SAMPLES]

optional arguments:
  -h, --help            show this help message and exit
  -b BACKGROUND_DIR, --background_dir BACKGROUND_DIR
                        background noise directory
  -r REC_DIR, --rec_dir REC_DIR
                        recorded samples directory
  -R BACKGROUND_RATIO, --background_ratio BACKGROUND_RATIO
                        background ratio to foreground
  -d BACKGROUND_DURATION, --background_duration BACKGROUND_DURATION
                        background split duration
  -p PITCH, --pitch PITCH
                        pitch semitones range
  -t TEMPO, --tempo TEMPO
                        tempo percentage range
  -D DESTINATION, --destination DESTINATION
                        destination directory
  -a FOREGROUND_ATTENUATION, --foreground_attenuation FOREGROUND_ATTENUATION
                        foreground random attenuation range
  -A BACKGROUND_ATTENUATION, --background_attenuation BACKGROUND_ATTENUATION
                        background random attenuation range
  -B BACKGROUND_PERCENT, --background_percent BACKGROUND_PERCENT
                        Background noise percentage
  -T TESTING_PERCENT, --testing_percent TESTING_PERCENT
                        dataset testing percent
  -v VALIDATION_PERCENT, --validation_percent VALIDATION_PERCENT
                        dataset validation percentage
  -S SILENCE_PERCENT, --silence_percent SILENCE_PERCENT
                        dataset silence percentage
  -n NOTKW_PERCENT, --notkw_percent NOTKW_PERCENT
                        dataset notkw percentage
  -s FILE_MIN_SILENCE_DURATION, --file_min_silence_duration FILE_MIN_SILENCE_DURATION
                        Min length of silence
  -H SILENCE_HEADROOM, --silence_headroom SILENCE_HEADROOM
                        silence threshold headroom
  -m MIN_SAMPLES, --min_samples MIN_SAMPLES
                        minimum resultant samples
```

Probably the important parameter is `--background_ratio` this sets the is ratio of the max_amplitude of background_noise to the kw & !kw voiced samples.
It is amplitude and not RMS so percieved loudness can seem different and is a set value.
This set the background_noise initial level and then a range of attenuation is randomly applied `--background_attenuation`
This sets the final ratio between background noise and kw & !kw samples.
`--foreground_attenuation` is the final volume of the overall sample and both attenuations are ranges from the max_ampltude=1.

The pitch is pitch changes in semitones and tempo is a non pitch changing duration modifier both allow variance to cope with room, mic proximity & Doppler effect.
A certain amount of samples are added without background noise as `--background_percent` default = 80% leaves 20% without background_noise.
Its likely background attenuation need not go above 0.8 as that is represented by clean samples.
You can use the background attenuation & background precent to vary the weight and range of background noise as lowering the attenuation will limit the range and not quantity.
Foreground attenuation is open to choice but again when starting to get above 70-80% you are making very low volume samples that may be of little use.

For extracting out the original 'rec' samples the silence recording is used as a datum for trimming silence for end sample use.
`--silence_headroom` adds an extra element of tolerance above the max amplitude of silence if you need to fine tune because voice is being corrupted in extraction.

The background_noise files and recorded silence files are added to a 'silence' classification which is a catchall for non voiced items (noise).
It uses the same parameters as KW & !KW but they are applied direct to the samples that directory includeds.
The volume of samples included will be the initial setpoint and the duration equates to its percentage of the overall duration sum.
So choice and length of background noise samples can effect how that provides inference to KW.

The defaults can be read from the parser argument
```
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--background_dir', type=str, default='_background_noise_', help='background noise directory')
parser.add_argument('-r', '--rec_dir', type=str, default='rec', help='recorded samples directory')
parser.add_argument('-R', '--background_ratio', type=float, default=0.6, help='background ratio to foreground')
parser.add_argument('-d', '--background_duration', type=float, default=2.5, help='background split duration')
parser.add_argument('-p', '--pitch', type=float, default=1.5, help='pitch semitones range')
parser.add_argument('-t', '--tempo', type=float, default=0.2, help='tempo percentage range')
parser.add_argument('-D', '--destination', type=str, default='dataset', help='destination directory')
parser.add_argument('-a', '--foreground_attenuation', type=float, default=0.7, help='foreground random attenuation range')
parser.add_argument('-A', '--background_attenuation', type=float, default=0.7, help='background random attenuation range')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-T', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
parser.add_argument('-S', '--silence_percent', type=float, default=0.3, help='dataset silence percentage')
parser.add_argument('-n', '--notkw_percent', type=float, default=0.5, help='dataset notkw percentage')
parser.add_argument('-s', '--file_min_silence_duration', type=float, default=0.1, help='Min length of silence')
parser.add_argument('-H', '--silence_headroom', type=float, default=5.0, help='silence threshold headroom ')
parser.add_argument('-m', '--min_samples', type=int, default=200, help='minimum resultant samples')
```
The defaults for background ratio and the attenuations is a good starting point and increasing the ratio can help with noise for fractional minimal accuracy loss.
You environment will set optimal parameters but as the dataset is a starter dataset the defaults maybe high enough try those and then maybe @ 0.8 background ratio and test results.


A rough Background_noise example has been given conatining some random sounds you will need to collect and make your own for your own environment.

https://github.com/jim-schwoebel/download_audioset

https://homepages.tuni.fi/toni.heittola/datasets.html

https://github.com/karolpiczak/ESC-50

http://pdsounds.tuxfamily.org/

https://urbansounddataset.weebly.com/

https://github.com/microsoft/MS-SNSD

http://www.eduardofonseca.net/FSDnoisy18k/#download

https://drive.google.com/file/d/1mV_opi70qu-mCLid7CsB4BJDoX5nfdOi/view?usp=sharing

https://drive.google.com/file/d/1qmbm7yur8GfICOvyUfvBY6c7vXV8yVem/view?usp=sharing

https://drive.google.com/file/d/1pa58ERBdp4UijRUGEDBQjFv7jIKUROqx/view?usp=sharing

Background noise is added to the silence classification using recorded volume as the start point you should use audacity to test you mics record levels and normalise to -3dB less (0.707946) and also maybe another set at half that volume again to vary your silence collection.

