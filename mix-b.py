import sox
import random
import glob
import argparse
import os
import tempfile
import math
import json

def get_voice_params(rec_file, silence_maximum_amplitude):
  
  tfm1 = sox.Transformer()
  stat = tfm1.stat(rec_file)
  file_maximum_amplitude = float(stat['Maximum amplitude'] )
  file_duration = float(stat['Length (seconds)'])
  
  percent_silence_threshold = silence_maximum_amplitude * (100 + args.silence_headroom)
  
  tfm1.silence(location=-1, min_silence_duration=args.file_min_silence_duration, silence_threshold=percent_silence_threshold, buffer_around_silence=True)
  tfm1.build(rec_file, '/tmp/temp1.wav')
  tfm1.clear_effects()
  stat = tfm1.stat('/tmp/temp1.wav')
  voice_end = float(stat['Length (seconds)'])

  tfm2 = sox.Transformer()
  tfm2.silence(location=1, min_silence_duration=args.file_min_silence_duration, silence_threshold=percent_silence_threshold, buffer_around_silence=True)
  tfm2.build('/tmp/temp1.wav', '/tmp/temp2.wav')
  tfm2.clear_effects()
  voice_stat = tfm2.stat('/tmp/temp2.wav')
  voice_stats = tfm2.stats('/tmp/temp2.wav')

  voice_start = voice_end - float(voice_stat['Length (seconds)'])

  return file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats
  
def augment(rec_file, silence_maximum_amplitude, cycle, overfit_ratio=1):
    
  dest_file = os.path.splitext(os.path.basename(rec_file))[0]
  dest_cbm = []
  frg_amplitude = []
  pitch = random.uniform(abs((args.pitch / 2) * overfit_ratio) * -1, abs(args.pitch / 2) * overfit_ratio)
  tfm1 = sox.Transformer()
  tfm1.pitch(pitch)
  tfm1.build(rec_file, '/tmp/pitch.wav')
  tfm1.clear_effects()
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/pitch.wav', silence_maximum_amplitude)
  print(file_maximum_amplitude, file_duration, voice_start, voice_end)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)  
  if trim_start < 0:
    trim_start = 0  
  tfm1.trim(trim_start, trim_start + 1)
  tfm1.build('/tmp/pitch.wav', '/tmp/cbm1.wav') 
  tfm1.clear_effects()
  frg_stat = tfm1.stat('/tmp/cbm1.wav')
  frg_amplitude.append(float(frg_stat['Maximum amplitude']))
  dest_cbm.append(args.destination + '/' + dest_file + str(cycle) + '-pitch.wav')
  
  tempo = random.uniform(1 - abs((args.tempo / 4) * overfit_ratio), 1 + (abs(args.tempo / 2) * overfit_ratio))
  tfm2 = sox.Transformer()
  tfm2.tempo(tempo, 's')
  tfm2.build(rec_file, '/tmp/tempo.wav')
  tfm2.clear_effects()
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/tempo.wav', silence_maximum_amplitude)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)
  if trim_start < 0:
    trim_start = 0
  tfm2.trim(trim_start, trim_start + 1)
  tfm2.build('/tmp/tempo.wav', '/tmp/cbm2.wav') 
  tfm2.clear_effects()
  frg_stat = tfm2.stat('/tmp/cbm2.wav')
  frg_amplitude.append(float(frg_stat['Maximum amplitude']))
  dest_cbm.append(args.destination + '/' + dest_file + str(cycle) + '-tempo.wav')
  
  pitch = random.uniform(abs((args.pitch / 2) * overfit_ratio) * -1, abs(args.pitch / 2) * overfit_ratio)
  tempo = random.uniform(1 - abs((args.tempo / 4)  * overfit_ratio), 1 + abs((args.tempo / 2) * overfit_ratio))  
  tfm3 = sox.Transformer()
  tfm3.pitch(pitch)
  tfm3.tempo(tempo, 's')
  tfm3.build(rec_file, '/tmp/pitch-tempo.wav')
  tfm3.clear_effects()
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/pitch-tempo.wav', silence_maximum_amplitude)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)
  if trim_start < 0:
    trim_start = 0
  tfm3.trim(trim_start, trim_start + 1)
  tfm3.build('/tmp/pitch-tempo.wav', '/tmp/cbm3.wav')
  tfm3.clear_effects()
  frg_stat = tfm3.stat('/tmp/cbm3.wav')
  frg_amplitude.append(float(frg_stat['Maximum amplitude']))
  dest_cbm.append(args.destination + '/' + dest_file + str(cycle) + '-pitch-tempo.wav')
  
  cbn1 = sox.Combiner()
  cbm_count = 1
  while cbm_count < 4:
    if random.random() <= args.background_percent:
      background_noise_file = background_noise_files[int(background_noise_count * random.random())][0]
      background_start = (sox.file_info.duration(background_noise_file) - 1) * random.random()

      tfm1.trim(start_time=background_start, end_time=background_start + 1)
      tfm1.build(background_noise_file, '/tmp/bkg-' + str(cbm_count) + '.wav')
      tfm1.clear_effects()
  
      bkg_stat = tfm1.stat('/tmp/bkg-' + str(cbm_count) + '.wav')
      bkg_amplitude = float(bkg_stat['Maximum amplitude'] )
      print(frg_amplitude[cbm_count - 1], args.background_ratio, bkg_amplitude)
      if abs(bkg_amplitude) == 0:
        target_amplitude = abs(frg_amplitude[cbm_count - 1]) * args.background_ratio
      else:
        target_amplitude = (abs(frg_amplitude[cbm_count - 1]) * args.background_ratio) / abs(bkg_amplitude)
    
      tfm2.vol(target_amplitude, gain_type='amplitude')
      tfm2.build('/tmp/bkg-' + str(cbm_count) + '.wav', '/tmp/amp-' + str(cbm_count) + '.wav')
      tfm2.clear_effects()
    
      cbn1.set_input_format(file_type=['wav', 'wav'])
      cbn1.build(['/tmp/cbm' + str(cbm_count) + '.wav', '/tmp/amp-' + str(cbm_count) + '.wav'], dest_cbm[cbm_count - 1], 'mix')
      cbn1.clear_effects()
    else:
      os.popen('cp ' + '/tmp/cbm' + str(cbm_count) + '.wav' + ' ' + dest_cbm[cbm_count - 1])
    cbm_count += 1
  return frg_amplitude
  
def single_silence(rec_file, count, repeat=False, overfit_ratio=1):
    destfile = args.destination + "/" + os.path.splitext(os.path.basename(rec_file))[0] + '-' + str(count) + '.wav'
    tfm1 = sox.Transformer()
    if repeat == True:
      count = int(sox.file_info.duration(rec_file) * random.random())
    if count + 1 > int(sox.file_info.duration(rec_file)):
      count = 0
    print(destfile, count)
    pitch = random.uniform(abs((args.pitch / 2) * overfit_ratio) * -1, abs(args.pitch / 2) * overfit_ratio)
    tempo = random.uniform(1 - abs((args.tempo / 4)  * overfit_ratio), 1 + abs((args.tempo / 2) * overfit_ratio))
    
    tfm1.pitch(pitch)
    tfm1.tempo(tempo)
    tfm1.trim(count, count + 1)
    tfm1.build(rec_file, '/tmp/silence.wav') 
    tfm1.clear_effects()
    silence_stat = tfm1.stat('/tmp/silence.wav')
    silence_amplitude = abs(float(silence_stat['Maximum amplitude'] ))
    if abs(silence_amplitude) == 0:
      target_amplitude = kw_avg_amplitude
    else:
      target_amplitude = kw_avg_amplitude / silence_amplitude
    tfm1.trim(0, 1)
    tfm1.vol(target_amplitude, gain_type='amplitude')
    tfm1.build('/tmp/silence.wav', destfile)
      
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--background_dir', type=str, default='_background_noise_', help='background noise directory')
parser.add_argument('-r', '--rec_dir', type=str, default='rec', help='recorded samples directory')
parser.add_argument('-R', '--background_ratio', type=float, default=0.20, help='background ratio to foreground')
parser.add_argument('-d', '--background_duration', type=float, default=2.5, help='background split duration')
parser.add_argument('-p', '--pitch', type=float, default=4.0, help='pitch semitones range')
parser.add_argument('-t', '--tempo', type=float, default=0.8, help='tempo percentage range')
parser.add_argument('-D', '--destination', type=str, default='dataset', help='destination directory')
parser.add_argument('-a', '--foreground_attenuation', type=float, default=0.4, help='foreground random attenuation range')
parser.add_argument('-A', '--background_attenuation', type=float, default=0.4, help='background random attenuation range')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-T', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
parser.add_argument('-S', '--silence_percent', type=float, default=0.1, help='dataset silence percentage')
parser.add_argument('-n', '--notkw_percent', type=float, default=0.1, help='dataset notkw percentage')
parser.add_argument('-s', '--file_min_silence_duration', type=float, default=0.1, help='Min length of silence')
parser.add_argument('-H', '--silence_headroom', type=float, default=1.0, help='silence threshold headroom ')
parser.add_argument('-m', '--min_samples', type=int, default=100, help='minimum resultant samples')
parser.add_argument('-N', '--norm_silence', type=bool, default=True, help='normalise silence files')
parser.add_argument('-o', '--overfit-ratio', type=float, default=0.20, help='reduces pitch & tempo variation')
args = parser.parse_args()

if not os.path.exists(args.destination):
  os.makedirs(args.destination)
else:
  print('Destination folder exists')
  exit()
  
with open(args.destination + '/args.txt', 'w') as f:
    json.dump(args.__dict__, f, indent=2)

silence_files = glob.glob(args.rec_dir + '/silence*.wav')
silence_file = silence_files[0]
#Some soundcards can ramp and click at start
tfm1 = sox.Transformer()
tfm1.trim(start_time=0.2)
tfm1.build(silence_file, '/tmp/sil_temp.wav')
tfm1.clear_effects()
stat = tfm1.stat('/tmp/sil_temp.wav')
silence_maximum_amplitude = float(stat['Maximum amplitude'])

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

if args.testing_percent >= args.validation_percent:
  needed_samples = args.min_samples / args.validation_percent
else:
  needed_samples = args.min_samples / args.testing_percent

if args.notkw_percent >= args.silence_percent:
  needed_samples = needed_samples / args.silence_percent
else:
  needed_samples = needed_samples / args.notkw_percent
  
cycles = math.ceil((needed_samples / 3) / len(kw_files))
print(needed_samples, cycles, len(kw_files))

count = 0
kw_amplitude = []
kw_count = 0
kw_sum = 0
while count < cycles:
  for kw_file in kw_files:
    kw_amplitude = augment(kw_file, silence_maximum_amplitude, count, args.overfit_ratio)
    kw_count += 1
    kw_sum = kw_sum + kw_amplitude[0] + kw_amplitude[1] + kw_amplitude[2]
  count += 1
kw_avg_amplitude = kw_sum / (kw_count * 3)
print(kw_avg_amplitude)

kw_files = glob.glob(args.destination + '/kw*.wav')
random.shuffle(kw_files)

train_percent = int(len(kw_files) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = kw_files[0 : train_percent]

test_percent = int(len(kw_files) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = kw_files[train_percent + 1 : test_percent]
print(str(train_percent + 1) + ':' +str(test_percent))

validation_percent = int(len(kw_files) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = kw_files[test_percent + 1 : validation_percent]
print(str(test_percent + 1) + ':' + str(validation_percent))

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

cycles = math.ceil((needed_samples / 3) / len(notkw_files))
print(needed_samples, cycles, len(notkw_files))

count = 0
while count < cycles:
  for notkw_file in notkw_files:
    augment(notkw_file, silence_maximum_amplitude, count)
  count += 1

notkw_files = glob.glob(args.destination + '/notkw*.wav')
random.shuffle(notkw_files)

train_percent = int((total_kw * args.notkw_percent) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = notkw_files[0 : train_percent]

test_percent = int((total_kw * args.notkw_percent) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = notkw_files[train_percent + 1 : test_percent]
print(str(train_percent + 1) + ':' + str(test_percent))

validation_percent = int((total_kw * args.notkw_percent) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = notkw_files[test_percent + 1 : validation_percent]
print(str(test_percent + 1) + ':' + str(validation_percent))

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

needed_samples = math.ceil(total_kw * args.silence_percent)
print("Total duration =" + str(total_duration), needed_samples, len(silence_files))

if total_duration >= needed_samples:
#if we have enough duration then they will be split and added in proportion to length
  file_count = 0
  cycle_count = 1
  while file_count < needed_samples:
    for silence_file in silence_files:
      if int(sox.file_info.duration(silence_file)) > cycle_count:
        single_silence(silence_file, cycle_count, False)
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
print(str(train_percent + 1) + ':' + str(test_percent))

validation_percent = int((total_kw * args.silence_percent) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = silence_files[test_percent + 1 : validation_percent]
print(str(test_percent + 1) + ':' + str(validation_percent))
 
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

