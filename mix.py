import sox
import random
import glob
import argparse
import os
import tempfile
import math

def get_voice_params(file, silence_maximum_amplitude):

  stat = sox.file_info.stat(file)
  file_maximum_amplitude = stat['Maximum amplitude'] 
  file_duration = stat['Length (seconds)']
  
  percent_silence_threshold = silence_maximum_amplitude * 105
  print (percent_silence_threshold, silence_maximum_amplitude, file_maximum_amplitude)

  
  tfm2 = sox.Transformer()
  tfm2.silence(location=-1, min_silence_duration=args.file_min_silence_duration, silence_threshold=percent_silence_threshold)
  tfm2.build(file, '/tmp/temp2.wav')
  tfm2.clear_effects()
  stat = sox.file_info.stat('/tmp/temp2.wav')
  voice_end = stat['Length (seconds)'] 

  tfm3 = sox.Transformer()
  tfm3.silence(location=1, min_silence_duration=args.file_min_silence_duration, silence_threshold=percent_silence_threshold)
  tfm3.build('/tmp/temp2.wav', '/tmp/temp3.wav')
  tfm3.clear_effects()
  voice_stat = sox.file_info.stat('/tmp/temp3.wav')
  voice_start = voice_end - voice_stat['Length (seconds)']

  return file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat

def augment(file, cycle):
  print(file)
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat = get_voice_params(file, silence_maximum_amplitude)
  voice_mean_norm = voice_stat['Mean    norm']
  print(file_maximum_amplitude, file_duration, voice_start, voice_end, "voice_mean_norm=" + str(voice_mean_norm))
  
  x = 0
  while x < 21:
    if len(background_noise_files) > 0:
      background_noise_file = background_noise_files[int(background_noise_count * random.random())][0]
      background_start = (sox.file_info.duration(background_noise_file) - args.background_duration) * random.random() 

      tmp1 = tempfile.NamedTemporaryFile(suffix='.wav')
      tfm1 = sox.Transformer()
      tfm1.trim(start_time=background_start, end_time=background_start + args.background_duration)
      tfm1.build(background_noise_file, tmp1.name)
      tfm1.clear_effects()

      background_stat = sox.file_info.stat(tmp1.name)
      background_mean_norm = background_stat['Mean    norm']
      attenuation = random.uniform(1 - abs(args.background_attenuation), 1)
      background_target = voice_mean_norm * args.background_ratio
      background_gain = (background_target / background_mean_norm) * attenuation
      #print("background_target=" + str(background_target),"background_gain=" + str(background_gain))

      tmp2 = tempfile.NamedTemporaryFile(suffix='.wav')
      tfm1.vol(gain=background_gain, gain_type='amplitude')
      tfm1.build(tmp1.name, tmp2.name)
      tfm1.clear_effects()
      
    
    destfile = args.destination + "/" + os.path.splitext(os.path.basename(file))[0] + '-' + str(cycle) + '-' + str(x) + '.wav'
    pitch = random.uniform(abs(args.pitch / 2) * -1, abs(args.pitch / 2))
    tempo = random.uniform(1 - abs(args.tempo / 2), 1 + abs(args.tempo / 2))
    attenuation = random.uniform(1 - abs(args.foreground_attenuation), 1)
    non_voice = 1 - (voice_stat['Length (seconds)'] / tempo)
    if non_voice >= voice_start:
      trim_start = voice_start * random.random() 
    else:
      trim_start = voice_start - (non_voice * random.random())
  

    if random.random() <= args.background_percent and len(background_noise_files) > 0:
      cbn1 = sox.Combiner()
      cbn1.set_input_format(file_type=['wav', 'wav'])
      cbn1.pitch(pitch)
      cbn1.tempo(tempo, 's')
      cbn1.vol(attenuation, gain_type='amplitude')
      cbn1.trim(trim_start, trim_start + 1)
      cbn1.build([tmp2.name, file], destfile, 'mix')
    else:
      tfm2 = sox.Transformer()
      tfm2.pitch(pitch)
      tfm2.tempo(tempo, 's')
      tfm2.vol(attenuation, gain_type='amplitude')
      tfm2.trim(trim_start, trim_start + 1)
      tfm2.build(file, destfile)

    x += 1

def single_silence(file, count, repeat=False):
    destfile = args.destination + "/" + os.path.splitext(os.path.basename(file))[0] + '-' + str(count) + '.wav'
    if repeat == True:
      count = 0
    pitch = random.uniform(abs(args.pitch / 2) * -1, abs(args.pitch / 2))
    tempo = random.uniform(1 - abs(args.tempo / 2), 1 + abs(args.tempo / 2))
    attenuation = random.uniform(1 - abs(args.foreground_attenuation), 1)
    tfm1 = sox.Transformer()
    tfm1.pitch(pitch)
    tfm1.tempo(tempo, 's')
    tfm1.vol(attenuation, gain_type='amplitude')
    tfm1.trim(count, count + 1)
    tfm1.build(file, destfile)  
    
    
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--background_dir', type=str, default='_background_noise_', help='background noise directory')
parser.add_argument('-r', '--rec_dir', type=str, default='rec', help='recorded samples directory')
parser.add_argument('-R', '--background_ratio', type=float, default=0.4, help='background ratio to foreground')
parser.add_argument('-d', '--background_duration', type=float, default=2.5, help='background split duration')
parser.add_argument('-p', '--pitch', type=float, default=1.5, help='pitch semitones range')
parser.add_argument('-t', '--tempo', type=float, default=0.2, help='tempo percentage range')
parser.add_argument('-D', '--destination', type=str, default='dataset', help='destination directory')
parser.add_argument('-a', '--foreground_attenuation', type=float, default=0.3, help='foreground random attenuation range')
parser.add_argument('-A', '--background_attenuation', type=float, default=0.4, help='background random attenuation range')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-T', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
parser.add_argument('-S', '--silence_percent', type=float, default=0.3, help='dataset silence percentage')
parser.add_argument('-n', '--notkw_percent', type=float, default=0.5, help='dataset notkw percentage')
parser.add_argument('-s', '--file_min_silence_duration', type=float, default=0.1, help='Min length of silence')
args = parser.parse_args()

silence_files = glob.glob(args.rec_dir + '/silence*.wav')
silence_file = silence_files[0]
#Some soundcards can ramp and click at start
tmp1 = tempfile.NamedTemporaryFile(suffix='.wav')
tfm1 = sox.Transformer()
tfm1.trim(start_time=0.2)
tfm1.build(silence_file, tmp1.name)
tfm1.clear_effects()

stat = sox.file_info.stat(tmp1.name)
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


if args.testing_percent > args.validation_percent:
  min_samples = 200 / args.validation_percent
else:
  min_samples = 200 / args.testing_percent

if args.notkw_percent > args.silence_percent:
  needed_samples = min_samples / args.silence_percent
else:
  needed_samples = min_samples / args.notkw_percent
  
cycles = math.ceil(math.ceil(needed_samples) / 20)
print(needed_samples, cycles, len(kw_files) )
count = 0
while count < cycles:
  for kw_file in kw_files:
    augment(kw_file, count)
    count += 1
    if count > cycles:
      break

kw_files = glob.glob(args.destination + '/kw*.wav')
random.shuffle(kw_files)

train_percent = int(len(kw_files) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = kw_files[0 : train_percent]

test_percent = int(len(kw_files) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = kw_files[train_percent + 1 : test_percent]
print(train_percent + 1, test_percent)

validation_percent = int(len(kw_files) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = kw_files[test_percent + 1 : validation_percent]
print(test_percent + 1, validation_percent)

if not os.path.exists(args.destination + '/training'):
  os.makedirs(args.destination + '/training') 
if not os.path.exists(args.destination + '/training/kw'):
  os.makedirs(args.destination + '/training/kw') 
  
for files in train:
  os.system('mv ' + files + ' ' +  args.destination + '/training/kw/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/testing'):
  os.makedirs(args.destination + '/testing') 
if not os.path.exists(args.destination + '/testing/kw'):
  os.makedirs(args.destination + '/testing/kw')   
  
for files in test:
  os.system('mv ' + files + ' ' +  args.destination + '/testing/kw/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/validation'):
  os.makedirs(args.destination + '/validation') 
if not os.path.exists(args.destination + '/validation/kw'):
  os.makedirs(args.destination + '/validation/kw')
  
for files in validation:
  os.system('mv ' + files + ' ' +  args.destination + '/validation/kw/' + os.path.basename(files))
  
os.system('rm ' +  args.destination + '/kw*.wav')

notkw_files = glob.glob(args.rec_dir + '/notkw*.wav')
random.shuffle(notkw_files)

total_kw = validation_percent
needed_samples = total_kw * args.notkw_percent

cycles = math.ceil(math.ceil(needed_samples) / 20)
print(needed_samples, cycles, len(kw_files) )
count = 0
while count < cycles:
  for notkw_file in notkw_files:
    augment(notkw_file, count)
    count += 1
    if count > cycles:
      break    
notkw_files = glob.glob(args.destination + '/notkw*.wav')
random.shuffle(notkw_files)

train_percent = int((total_kw * args.notkw_percent) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = notkw_files[0 : train_percent]

test_percent = int((total_kw * args.notkw_percent) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = notkw_files[train_percent + 1 : test_percent]
print(train_percent + 1, test_percent)

validation_percent = int((total_kw * args.notkw_percent) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = notkw_files[test_percent + 1 : validation_percent]
print(test_percent + 1, validation_percent)

if not os.path.exists(args.destination + '/training/notkw'):
  os.makedirs(args.destination + '/training/notkw') 
  
for files in train:
  os.system('mv ' + files + ' ' +  args.destination + '/training/notkw/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/testing/notkw'):
  os.makedirs(args.destination + '/testing/notkw')   
  
for files in test:
  os.system('mv ' + files + ' ' +  args.destination + '/testing/notkw/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/validation/notkw'):
  os.makedirs(args.destination + '/validation/notkw')
  
for files in validation:
  os.system('mv ' + files + ' ' +  args.destination + '/validation/notkw/' + os.path.basename(files))
  
os.system('rm ' +  args.destination + '/notkw*.wav')

silence_files = []
if os.path.exists(args.background_dir):
  silence_files = glob.glob(args.background_dir + '/*.wav')

silence_files = silence_files + glob.glob(args.rec_dir + '/silence*.wav')
random.shuffle(silence_files)

total_duration = 0
for silence_file in silence_files:
  total_duration = total_duration + int(sox.file_info.duration(silence_file))

print("Total duration =" + str(total_duration))
needed_samples = math.ceil(total_kw * args.silence_percent)

if total_duration >= needed_samples:
#if we have enough duration then they will be split and added in proportion to length
  print(needed_samples, len(silence_files))
  file_count = 0
  cycle_count = 1
  while file_count < needed_samples:
    for silence_file in silence_files:
      if int(sox.file_info.duration(silence_file)) > cycle_count:
        single_silence(silence_file, cycle_count)
        file_count += 1
        if file_count > needed_samples:
          break   
    cycle_count += 1
else:
  file_count = 0
  cycle_count = 1
  while file_count < needed_samples:
    for silence_file in silence_files:
      single_silence(silence_file, cycle_count, True)
      file_count += 1
      if file_count > needed_samples:
        break   
    cycle_count += 1
 
silence_files = glob.glob(args.destination + '/*.wav')
random.shuffle(silence_files)

train_percent = int((total_kw * args.silence_percent) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = silence_files[0 : train_percent]

test_percent = int((total_kw * args.silence_percent) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = silence_files[train_percent + 1 : test_percent]
print(train_percent + 1, test_percent)

validation_percent = int((total_kw * args.silence_percent) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = silence_files[test_percent + 1 : validation_percent]
print(test_percent + 1, validation_percent)

if not os.path.exists(args.destination + '/training/silence'):
  os.makedirs(args.destination + '/training/silence') 
  
for files in train:
  os.system('mv ' + files + ' ' +  args.destination + '/training/silence/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/testing/silence'):
  os.makedirs(args.destination + '/testing/silence')   
  
for files in test:
  os.system('mv ' + files + ' ' +  args.destination + '/testing/silence/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/validation/silence'):
  os.makedirs(args.destination + '/validation/silence')
  
for files in validation:
  os.system('mv ' + files + ' ' +  args.destination + '/validation/silence/' + os.path.basename(files))
  
os.system('rm ' +  args.destination + '/*.wav')

