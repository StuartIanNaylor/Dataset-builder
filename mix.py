import sox
import numpy as np
import argparse
import glob
import os
import re
import math 
import random

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', type=str, default='splits', help='source directory')
parser.add_argument('-d', '--destination', type=str, default='dataset', help='destination directory')
parser.add_argument('-S', '--silence', type=str, default='rec', help='silence reference file')
parser.add_argument('-b', '--background_vol', type=float, default=0.5, help='Background noise ratio')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-t', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
args = parser.parse_args()

def add_silence_pad(filename, cycle, background=None):
  stat = sox.file_info.stat(filename)
  duration = stat['Length (seconds)']
  silencewav = glob.glob(args.source + '/silence' + '/silence*.wav')

  np1 = np.arange(start=-1.0, stop=1.1, step=0.10)
  np2 = np.arange(start=0.9, stop=1.11, step=0.01)
  np3 = np.arange(start=0.9, stop=1.11, step=0.01)
  np4 = np.arange(start=-5.0, stop=5.5, step=0.5)

  np.random.shuffle(np1)
  np.random.shuffle(np2)
  np.random.shuffle(np3)
  np.random.shuffle(np4)
  random.shuffle(silencewav)

  x = 0

  while x < 21:
    tfm1 = sox.Transformer()
    pitch_offset = np1[x]
    tempo_offset = np2[x]
    pad_offset = np3[x]
    gain_offset = np4[x]
    
    pad = (1 - duration)
    pad = abs(pad * pad_offset) / 2
 
    tfm1.pitch(pitch_offset)
    tfm1.gain(gain_offset, False)      
    tfm1.tempo(tempo_offset, 's')
    tfm1.pad(pad)
    num = '000'
    num = num[0 :  - len(str(x))]
    suffix = num + str(x)
    destfile = os.path.splitext(os.path.basename(filename))[0] + '-' + cycle + '-' + suffix + '.wav'
    tfm1.build_file(filename, args.destination + '/' + 'temp.wav')
    
    #percent = random.random()
    if random.random() < args.background_percent:
      stat = sox.file_info.stat(args.destination + '/' + 'temp.wav')
      foreground_norm = stat['Mean    norm']
      print("Destfile ", stat)
    
      noisefile = int(random.random() * len(background))
      stat = sox.file_info.stat(background[noisefile])
      background_norm = stat['Mean    norm']
      print("Background ", stat)
    
      vol_adjust = ((foreground_norm / background_norm) * args.background_vol) * random.random()
      print("Vol_adjust", vol_adjust)    
    
      tfm2 = sox.Transformer()
      tfm2.vol(vol_adjust, 'amplitude')
      tfm2.build_file(background[noisefile], args.destination + '/' + 'temp2.wav')
    
      stat = sox.file_info.stat(args.destination + '/' + 'temp2.wav')
      print("Vol_adjust", stat)
    
      cbn1 = sox.Combiner()
      cbn1.set_input_format(file_type=['wav', 'wav', 'wav'])
      cbn1.build([args.destination + '/' + 'temp.wav', args.destination + '/' + 'temp2.wav', silencewav[x]], args.destination + '/' + destfile, 'mix')

      os.remove(args.destination + '/' + 'temp.wav')
      os.remove(args.destination + '/' + 'temp2.wav')
    else:
      cbn1 = sox.Combiner()
      cbn1.set_input_format(file_type=['wav', 'wav'])
      cbn1.build([args.destination + '/' + 'temp.wav', silencewav[x]], args.destination + '/' + destfile, 'mix')
      
      os.remove(args.destination + '/' + 'temp.wav')

    x = x + 1


kwwav = glob.glob(args.source + '/kw' + '/kw*.wav')
background = glob.glob(args.source + '/background' + '/*.wav')

if not os.path.exists(args.destination):
  os.makedirs(args.destination) 

if len(kwwav) < 50:
 cycles = math.ceil(50 / len(kwwav))
 print(cycles,len(kwwav)) 

count = 0
while count < cycles:
  for files in kwwav:
    add_silence_pad(files, str(count), background)
  count += 1

kwwav = glob.glob(args.destination + '/kw*.wav')

train_percent = int(len(kwwav) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = kwwav[0 : train_percent]

test_percent = int(len(kwwav) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = kwwav[train_percent + 1 : test_percent]
print(train_percent + 1, test_percent)

validation_percent = int(len(kwwav) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = kwwav[test_percent + 1 : validation_percent]
print(test_percent + 1, validation_percent)

if not os.path.exists(args.destination + '/training'):
  os.makedirs(args.destination + '/training') 

for files in train:
  os.system('mv ' + files + ' ' +  args.destination + '/training/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/testing'):
  os.makedirs(args.destination + '/testing') 
  
for files in test:
  os.system('mv ' + files + ' ' +  args.destination + '/testing/' + os.path.basename(files))
  
if not os.path.exists(args.destination + '/validation'):
  os.makedirs(args.destination + '/validation') 
  
for files in validation:
  os.system('mv ' + files + ' ' +  args.destination + '/validation/' + os.path.basename(files))
  
os.system('mv ' +  args.destination + '/kw*.wav ' +  args.destination + '/training/')

