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
parser.add_argument('-b', '--background_vol', type=float, default=0.5, help='Background noise ratio')
parser.add_argument('-B', '--background_percent', type=float, default=0.8, help='Background noise percentage')
parser.add_argument('-t', '--testing_percent', type=float, default=0.1, help='dataset testing percent')
parser.add_argument('-v', '--validation_percent', type=float, default=0.1, help='dataset validation percentage')
parser.add_argument('-S', '--silence_percent', type=float, default=0.3, help='dataset silence percentage')
parser.add_argument('-n', '--notkw_percent', type=float, default=0.5, help='dataset notkw percentage')
args = parser.parse_args()

def add_variation(filename, cycle, background=None):
  stat = sox.file_info.stat(filename)
  duration = stat['Length (seconds)']
  silencewav = glob.glob(args.source + '/silence' + '/silence*.wav')

  #np1 = np.arange(start=-1.0, stop=1.1, step=0.10)
  np1 = np.arange(start=-2.0, stop=2.2, step=0.20)
  #np2 = np.arange(start=0.9, stop=1.11, step=0.01)
  np2 = np.arange(start=0.8, stop=1.22, step=0.02)
  np3 = np.arange(start=0.0, stop=2.1, step=0.10)
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
    tfm1.gain(gain_offset, False, True)      
    tfm1.tempo(tempo_offset, 's')
    tfm1.pad(pad)
    num = '000'
    num = num[0 :  - len(str(x))]
    suffix = num + str(x)
    destfile = os.path.splitext(os.path.basename(filename))[0] + '-' + cycle + '-' + suffix + '.wav'
    tfm1.build_file(filename, args.destination + '/' + 'temp.wav')
    
    if random.random() < args.background_percent:
      stat = sox.file_info.stat(args.destination + '/' + 'temp.wav')
      foreground_norm = stat['Mean    norm']
    
      noisefile = int(random.random() * len(background))
      stat = sox.file_info.stat(background[noisefile])
      background_norm = stat['Mean    norm']
    
      vol_adjust = ((foreground_norm / background_norm) * args.background_vol) * random.random()
    
      tfm2 = sox.Transformer()
      tfm2.vol(vol_adjust, 'amplitude')
      tfm2.build_file(background[noisefile], args.destination + '/' + 'temp2.wav')
    
      stat = sox.file_info.stat(args.destination + '/' + 'temp2.wav')
    
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
    
def add_silence(filename, cycle):

    tfm1 = sox.Transformer()
    gain_offset = (random.random() * 10) - 5
    tfm1.gain(gain_offset, False, True)
    destfile = os.path.splitext(os.path.basename(filename))[0] + '-' + cycle + '.wav'
    tfm1.build_file(filename, args.destination + '/' + destfile)
    

kwwav = glob.glob(args.source + '/kw' + '/kw*.wav')
background = glob.glob(args.source + '/background' + '/*.wav')
random.shuffle(kwwav)
random.shuffle(background)


if not os.path.exists(args.destination):
  os.makedirs(args.destination) 

min_samples = 1000

if args.notkw_percent > args.silence_percent:
  needed_samples = min_samples / args.silence_percent
else:
  needed_samples = min_samples / args.notkw_percent
  
cycles = math.ceil(needed_samples / (len(kwwav) * 20))

print(cycles,len(kwwav)) 

count = 0
while count < cycles:
  for files in kwwav:
    add_variation(files, str(count), background)
  count += 1

kwwav = glob.glob(args.destination + '/kw*.wav')
random.shuffle(kwwav)

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

notkwwav = glob.glob(args.source + '/notkw' + '/notkw*.wav')
background = glob.glob(args.source + '/background' + '/*.wav')
random.shuffle(notkwwav)
random.shuffle(background)

if not os.path.exists(args.destination):
  os.makedirs(args.destination) 
total_kw = validation_percent
min_samples = total_kw * args.notkw_percent
cycles = math.ceil(min_samples / (len(notkwwav) * 20))

print(cycles,len(notkwwav)) 

count = 0
while count < cycles:
  for files in notkwwav:
    add_variation(files, str(count), background)
  count += 1
  
notkwwav = glob.glob(args.destination + '/notkw*.wav')
random.shuffle(notkwwav)

train_percent = int((total_kw * args.notkw_percent) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = notkwwav[0 : train_percent]

test_percent = int((total_kw * args.notkw_percent) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = notkwwav[train_percent + 1 : test_percent]
print(train_percent + 1, test_percent)

validation_percent = int((total_kw * args.notkw_percent) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = notkwwav[test_percent + 1 : validation_percent]
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



silencewav = glob.glob(args.source + '/silence' + '/silence*.wav')
silencewav = silencewav + glob.glob(args.source + '/background' + '/*.wav')
random.shuffle(silencewav)

min_samples = total_kw * args.silence_percent
cycles = math.ceil(min_samples / (len(silencewav) * 20))

print(cycles,len(silencewav))

count = 0
while count < cycles:
  for files in silencewav:
    add_silence(files, str(count))
  count += 1
  
silencewav = glob.glob(args.destination + '/*.wav')
random.shuffle(silencewav)

train_percent = int((total_kw * args.silence_percent) * (1 - args.testing_percent - args.validation_percent))
print('train percent', train_percent)
train = silencewav[0 : train_percent]

test_percent = int((total_kw * args.silence_percent) * args.testing_percent) + train_percent
print('test percent', test_percent)
test = silencewav[train_percent + 1 : test_percent]
print(train_percent + 1, test_percent)

validation_percent = int((total_kw * args.silence_percent) * args.validation_percent) + test_percent
print('validation percent', validation_percent)
validation = silencewav[test_percent + 1 : validation_percent]
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
