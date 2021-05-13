import sox
import random
import glob
import argparse
import os
import tempfile
import math

def get_voice_params(file, silence_maximum_amplitude,file_min_silence_duration=0.2):

  stat = sox.file_info.stat(file)
  file_maximum_amplitude = stat['Maximum amplitude']
  file_duration = stat['Length (seconds)']

  percent_silence_threshold = (silence_maximum_amplitude / file_maximum_amplitude) * 100

  tmp1 = tempfile.NamedTemporaryFile(suffix='.wav')
  tmp2 = tempfile.NamedTemporaryFile(suffix='.wav')

  tfm1 = sox.Transformer()
  tfm1.silence(location=-1, min_silence_duration=file_min_silence_duration, silence_threshold=percent_silence_threshold, buffer_around_silence=True)
  tfm1.build(file, tmp1.name)
  tfm1.clear_effects()

  stat = sox.file_info.stat(tmp1.name)
  voice_end = stat['Length (seconds)']

  tfm1.silence(location=1, min_silence_duration=file_min_silence_duration, silence_threshold=percent_silence_threshold, buffer_around_silence=True)
  tfm1.build(tmp1.name, tmp2.name)
  tfm1.clear_effects()

  voice_stat = sox.file_info.stat(tmp2.name)
  voice_start = voice_end - voice_stat['Length (seconds)']

  return file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat

def augment(file, cycle):

  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat = get_voice_params(file, silence_maximum_amplitude)
  voice_mean_norm = voice_stat['Mean    norm']
  print(file_maximum_amplitude, file_duration, voice_start, voice_end, "voice_mean_norm=" + str(voice_mean_norm))
  print(voice_stat)
  
  x = 0
  while x < 21:
    background_noise_file = background_noise_files[int(background_noise_count * random.random())][0]
    background_start = (sox.file_info.duration(background_noise_file) - args.background_duration) * random.random() 

    tmp1 = tempfile.NamedTemporaryFile(suffix='.wav')
    tfm1 = sox.Transformer()
    tfm1.trim(start_time=background_start, end_time=background_start + args.background_duration)
    tfm1.build(background_noise_file, tmp1.name)
    tfm1.clear_effects()

    background_stat = sox.file_info.stat(tmp1.name)
    background_mean_norm = background_stat['Mean    norm']
    print(background_start, "background_mean_nor=" + str(background_mean_norm))
    print(background_stat)

    background_target = voice_mean_norm * args.background_ratio
    background_gain = background_target / background_mean_norm
    print("background_target=" + str(background_target),"background_gain=" + str(background_gain))

    tmp2 = tempfile.NamedTemporaryFile(suffix='.wav')
    tfm1.vol(gain=background_gain, gain_type='amplitude')
    tfm1.build(tmp1.name, tmp2.name)

    non_voice = 1 - voice_stat['Length (seconds)']
  
    if non_voice >= voice_start:
      trim_start = voice_start * random.random() 
    else:
      trim_start = voice_start - (non_voice * random.random())
  
    destfile = os.path.splitext(os.path.basename(file))[0] + '-' + str(cycle) + '-' + str(x) + '.wav'
    pitch = random.uniform(abs(args.pitch / 2) * -1, abs(args.pitch / 2))
    tempo = random.uniform(1 - abs(args.tempo / 2), 1 + abs(args.tempo / 2))
    attenuation = random.uniform(1 - abs(args.attenuation), 1)
    cbn1 = sox.Combiner()
    cbn1.set_globals(verbosity=1)
    cbn1.set_input_format(file_type=['wav', 'wav'])
    cbn1.pitch(pitch)
    cbn1.tempo(tempo, 's')
    cbn1.vol(attenuation, gain_type='amplitude')
    cbn1.trim(trim_start, trim_start + 1)
    cbn1.build([tmp2.name, file], destfile, 'mix')

    x += 1


parser = argparse.ArgumentParser()
parser.add_argument('-b', '--background_dir', type=str, default='_background_noise_', help='background noise directory')
parser.add_argument('-r', '--rec_dir', type=str, default='rec', help='recorded samples directory')
parser.add_argument('-R', '--background_ratio', type=float, default=0.2, help='background ratio to foreground')
parser.add_argument('-d', '--background_duration', type=float, default=2.5, help='background split duration')
parser.add_argument('-p', '--pitch', type=float, default=2.0, help='pitch semitones range')
parser.add_argument('-t', '--tempo', type=float, default=0.2, help='tempo percentage range (0.2 = -+ 10%)')
parser.add_argument('-D', '--destination', type=str, default='dataset', help='destination directory')
parser.add_argument('-a', '--attenuation', type=float, default=0.2, help='attenuation range')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-T', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
parser.add_argument('-S', '--silence_percent', type=float, default=0.3, help='dataset silence percentage')
parser.add_argument('-n', '--notkw_percent', type=float, default=0.5, help='dataset notkw percentage')
args = parser.parse_args()

silence_files = glob.glob(args.rec_dir + '/silence*.wav')
silence_file = silence_files[0]
stat = sox.file_info.stat(silence_file)
silence_maximum_amplitude = stat['Maximum amplitude'] 

background_noise_files = []
# If the _background_noise_ dir exists we will add an element for each second of the noise file duration
# Then we will random shuffle that array
# Users can control each noise file % of noise by simply adding files or increasing duration
if os.path.exists(args.background_dir):
  background_files = glob.glob(args.background_dir + '/*.wav')
  for background_file in background_files:
    stat = sox.file_info.stat(background_file)
    background_file_duration = stat['Length (seconds)']
    background_item = []
    background_item.append(background_file)
    count = 0
    while count < int(background_file_duration / args.background_duration):
      background_noise_files.append(background_item)
      count += args.background_duration

random.shuffle(background_noise_files)
background_noise_count = len(background_noise_files)

kw_files = glob.glob(args.rec_dir + '/kw*.wav')
random.shuffle(kw_files)


if not os.path.exists(args.destination):
  os.makedirs(args.destination) 

min_samples = 1000

if args.notkw_percent > args.silence_percent:
  needed_samples = min_samples / args.silence_percent
else:
  needed_samples = min_samples / args.notkw_percent
  
cycles = math.ceil(needed_samples / (len(kw_files) * 20))

count = 0
while count < cycles:
  for kw_file in kw_files:
    augment(kw_file, count)
  count += 1





    
     