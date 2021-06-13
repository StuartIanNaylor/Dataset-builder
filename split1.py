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
  volume = random.uniform(1 - (args.amplitude_foreground * overfit_ratio), 1 + (args.amplitude_foreground * overfit_ratio))
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
  tfm1.vol(volume)
  tfm1.trim(trim_start, trim_start + 1)
  tfm1.build('/tmp/pitch.wav', args.destination + '/' + dest_file + str(cycle) + '-pitch.wav') 
  tfm1.clear_effects()
  
  tempo = random.uniform(1 - abs((args.tempo / 4) * overfit_ratio), 1 + (abs(args.tempo / 2) * overfit_ratio))
  volume = random.uniform(1 - (args.amplitude_foreground * overfit_ratio), 1 + (args.amplitude_foreground * overfit_ratio))
  tfm2 = sox.Transformer()
  tfm2.tempo(tempo, 's')
  tfm2.build(rec_file, '/tmp/tempo.wav')
  tfm2.clear_effects()
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/tempo.wav', silence_maximum_amplitude)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)
  if trim_start < 0:
    trim_start = 0
  tfm2.vol(volume)
  tfm2.trim(trim_start, trim_start + 1)
  tfm2.build('/tmp/tempo.wav', args.destination + '/' + dest_file + str(cycle) + '-tempo.wav') 
  tfm2.clear_effects()

  
  pitch = random.uniform(abs((args.pitch / 2) * overfit_ratio) * -1, abs(args.pitch / 2) * overfit_ratio)
  tempo = random.uniform(1 - abs((args.tempo / 4)  * overfit_ratio), 1 + abs((args.tempo / 2) * overfit_ratio))
  volume = random.uniform(1 - (args.amplitude_foreground * overfit_ratio), 1 + (args.amplitude_foreground * overfit_ratio))
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
  tfm3.vol(volume)
  tfm3.trim(trim_start, trim_start + 1)
  tfm3.build('/tmp/pitch-tempo.wav', args.destination + '/' + dest_file + str(cycle) + '-pitch-tempo.wav')
  tfm3.clear_effects()

  
  reverb_index = int(9.99 * random.random())
  volume = random.uniform(1 - (args.amplitude_foreground * overfit_ratio), 1 + (args.amplitude_foreground * overfit_ratio))
  tfm4 = sox.Transformer()
  tfm4.reverb(room_scale = reverb_values[reverb_index][0], pre_delay = reverb_values[reverb_index][1], reverberance = reverb_values[reverb_index][2], high_freq_damping = reverb_values[reverb_index][3], wet_gain  = reverb_values[reverb_index][4], stereo_depth = reverb_values[reverb_index][5])
  tfm4.build(rec_file, '/tmp/reverb.wav')
  tfm4.clear_effects()
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/reverb.wav', silence_maximum_amplitude)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)
  if trim_start < 0:
    trim_start = 0
  tfm4.vol(volume)
  tfm4.trim(trim_start, trim_start + 1)
  tfm4.build('/tmp/reverb.wav', args.destination + '/' + dest_file + str(cycle) + '-reverb.wav')
  tfm4.clear_effects()
  
  reverb_index = int(9.99 * random.random())
  volume = random.uniform(1 - (args.amplitude_foreground * overfit_ratio), 1 + (args.amplitude_foreground * overfit_ratio))
  pitch = random.uniform(abs((args.pitch / 2) * overfit_ratio) * -1, abs(args.pitch / 2) * overfit_ratio)
  tempo = random.uniform(1 - abs((args.tempo / 4)  * overfit_ratio), 1 + abs((args.tempo / 2) * overfit_ratio))  
  tfm5 = sox.Transformer()
  tfm5.pitch(pitch)
  tfm5.tempo(tempo, 's')
  tfm5.reverb(room_scale = reverb_values[reverb_index][0], pre_delay = reverb_values[reverb_index][1], reverberance = reverb_values[reverb_index][2], high_freq_damping = reverb_values[reverb_index][3], wet_gain  = reverb_values[reverb_index][4], stereo_depth = reverb_values[reverb_index][5])
  tfm5.build(rec_file, '/tmp/all.wav')
  tfm5.clear_effects()
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/all.wav', silence_maximum_amplitude)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)
  if trim_start < 0:
    trim_start = 0
  tfm5.vol(volume)
  tfm5.trim(trim_start, trim_start + 1)
  tfm5.build('/tmp/all.wav', args.destination + '/' + dest_file + str(cycle) + '-all.wav')
  tfm5.clear_effects()

  tfm6 = sox.Transformer()
  volume = random.uniform(1 - (args.amplitude_foreground * overfit_ratio), 1 + (args.amplitude_foreground * overfit_ratio))
  os.popen('cp ' + rec_file + ' /tmp/orig.wav')
  file_maximum_amplitude, file_duration, voice_start, voice_end, voice_stat, voice_stats = get_voice_params('/tmp/orig.wav', silence_maximum_amplitude)
  non_voice = 1 - (voice_end - voice_start)
  trim_start = voice_start - (non_voice / 2)
  if trim_start < 0:
    trim_start = 0
  tfm6.vol(volume)
  tfm6.trim(trim_start, trim_start + 1)
  tfm6.build('/tmp/orig.wav', args.destination + '/' + dest_file + str(cycle) + '-orig.wav')
  tfm6.clear_effects()
  
  
    
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--background_dir', type=str, default='_background_noise_', help='background noise directory')
parser.add_argument('-r', '--rec_dir', type=str, default='rec', help='recorded samples directory')
parser.add_argument('-R', '--background_ratio', type=float, default=0.20, help='background ratio to foreground')
parser.add_argument('-d', '--background_duration', type=float, default=2.5, help='background split duration')
parser.add_argument('-p', '--pitch', type=float, default=4.0, help='pitch semitones range')
parser.add_argument('-t', '--tempo', type=float, default=0.8, help='tempo percentage range')
parser.add_argument('-D', '--destination', type=str, default='dataset', help='destination directory')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-T', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
parser.add_argument('-S', '--silence_percent', type=float, default=0.1, help='dataset silence percentage')
parser.add_argument('-n', '--notkw_percent', type=float, default=0.1, help='dataset notkw percentage')
parser.add_argument('-s', '--file_min_silence_duration', type=float, default=0.1, help='Min length of silence')
parser.add_argument('-H', '--silence_headroom', type=float, default=1.0, help='silence threshold headroom ')
parser.add_argument('-m', '--min_samples', type=int, default=100, help='minimum resultant samples')
parser.add_argument('-o', '--overfit_ratio', type=float, default=0.1, help='reduces pitch & tempo variation of KW')
parser.add_argument('-k', '--keyword_qty', type=int, default=1, help='Keywords recorded')
parser.add_argument('-a', '--amplitude_foreground', type=float, default=0.1, help='+- foreground amplitude variance')
parser.add_argument('-A', '--amplitude_background', type=float, default=0.1, help='+- backgroundground amplitude variance')
args = parser.parse_args()

if not os.path.exists(args.destination):
  os.makedirs(args.destination)
else:
  print('Destination folder exists')
  exit()
  
f = open(args.rec_dir + '/rec.txt', "r")
args.keyword_qty = int(f.read())
f.close

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

reverb_values = []
reverb_values.append([16, 8, 80, 0, -6, 100])
reverb_values.append([20, 8, 80, 0, -4, 100])
reverb_values.append([23, 9, 65, 25, -3, 100])
reverb_values.append([27, 9, 65, 25, -2, 100])
reverb_values.append([30, 10, 50, 50, -1, 100])
reverb_values.append([40, 10, 50, 50, -1, 100])
reverb_values.append([52, 10, 45, 50, -1, 85])
reverb_values.append([60, 10, 45, 50, -1, 80])
reverb_values.append([75, 10, 40, 50, -1, 60])
reverb_values.append([85, 10, 40, 50, -1, 0])


if args.testing_percent >= args.validation_percent:
  needed_samples = math.ceil(args.min_samples / args.validation_percent)
else:
  needed_samples = math.ceil(args.min_samples / args.testing_percent)

if args.notkw_percent >= args.silence_percent:
  needed_samples = math.ceil(needed_samples / args.silence_percent)
else:
  needed_samples = math.ceil(needed_samples / args.notkw_percent)
  
kw_number = 0
while kw_number < args.keyword_qty:
  kw_files = glob.glob(args.rec_dir + '/kw' + str(kw_number) + '*.wav')
  random.shuffle(kw_files)

  cycles = math.ceil((needed_samples / 7) / len(kw_files))
  print(needed_samples, cycles, len(kw_files))

  count = 0
  kw_amplitude = []
  kw_count = 0
  kw_sum = 0
  while count < cycles:
    for kw_file in kw_files:
      augment(kw_file, silence_maximum_amplitude, count, args.overfit_ratio)
      kw_count += 1  
    count += 1

  kw_files = glob.glob(args.destination + '/kw*.wav')
  random.shuffle(kw_files)


  if not os.path.exists(args.destination + '/kw'  + str(kw_number)):
    os.makedirs(args.destination + '/kw' + str(kw_number)) 
  
  for files in kw_files:
    os.system('mv ' + files + ' ' +  args.destination + '/kw' + str(kw_number) + '/' + os.path.basename(files))
  
  kw_number += 1

notkw_files = glob.glob(args.rec_dir + '/notkw*.wav')
random.shuffle(notkw_files)

notkw_needed_samples = math.ceil(needed_samples * args.notkw_percent)

cycles = math.ceil((notkw_needed_samples / 6) / len(notkw_files))
print(notkw_needed_samples, cycles, len(notkw_files))

count = 0
while count < cycles:
  for notkw_file in notkw_files:
    augment(notkw_file, silence_maximum_amplitude, count)
  count += 1

notkw_files = glob.glob(args.destination + '/notkw*.wav')
random.shuffle(notkw_files)

if not os.path.exists(args.destination + '/notkw'):
  os.makedirs(args.destination + '/notkw') 
  
for files in notkw_files:
  os.system('mv ' + files + ' ' +  args.destination + '/notkw/' + os.path.basename(files))
  


