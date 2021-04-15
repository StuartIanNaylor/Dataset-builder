import sox
import numpy as np
import argparse
import glob
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--samplerate', type=int, default=16000, help='sampling rate')
parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument('-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
parser.add_argument('-s', '--source', type=str, default='rec', help='source directory')
parser.add_argument('-d', '--destination', type=str, default='splits', help='destination directory')
parser.add_argument('-f', '--filename', type=str, help='filename')
parser.add_argument('-S', '--silence', type=str, help='silence reference file')
parser.add_argument('-n', '--noise', type=float, default=-40, help='Silence noise threshold')
parser.add_argument('-D', '--duration', type=float, default=0.15, help='Minimum silence duration')
args = parser.parse_args()




if args.silence == None:
  silence = glob.glob(args.source + '/silence*.wav')[0]
  print(silence)
else:
  silence = args.source + '/' + args.silence
  
stat = sox.file_info.stat(silence)
silence = stat['Mean    norm']
print(stat)

parent_dir = os.getcwd()
path = os.path.join(parent_dir, args.destination)

if not os.path.exists(path):
  os.makedirs(path)

def split_silence(filename):
  stat = sox.file_info.stat(args.source + '/' + filename)
  amplitude = stat['Maximum amplitude']
  print(stat)

  threshold = (silence / amplitude) * 100

  os.system("cp " + args.source + '/' + filename + " " + args.source + '/temp.wav')
  os.system("sox " + args.source + '/temp.wav ' + args.destination + "/" + filename + " silence 1 " \
  + str(args.duration) + " " + str(threshold) + "% 1 " + str(args.duration) + " " + str(threshold) + "% : newfile : restart")
  #Fudge as : newfile : restart creates an extra null file
  list_of_files = sorted(glob.glob(path + '/*.wav')) 
  os.remove(list_of_files[len(list_of_files)-1])
  os.remove(args.source + '/temp.wav') 
  
def split1sec(filename, count):
  stat = sox.file_info.stat(args.source + '/' + filename)
  duration = int(stat['Length (seconds)'])
  print(stat)
  while count < duration:
    num = '00000'
    num = num[0 : 5 - len(str(count))]
    suffix = num + str(count)
    destfile = os.path.splitext(filename)[0] + '-' + suffix + '.wav'
    os.system("sox " + args.source + '/' + filename + " " + args.destination + "/" + destfile + ' trim ' + str(count) + ' 1')
    count += 1

def move_files(filename):
  if re.match('kw.', filename):
    kwpath = os.path.join(path, 'kw')
    if not os.path.exists(kwpath):
      os.makedirs(kwpath)
    os.system('mv ' + path + '/kw*.wav ' + kwpath + '/')

  elif re.match('notkw.', filename):
    notkwpath = os.path.join(path, 'notkw')
    if not os.path.exists(notkwpath):
      os.makedirs(notkwpath) 
    os.system('mv ' + path + '/notkw*.wav ' + notkwpath + '/')

  elif re.match('silence.', filename):
    silencepath = os.path.join(path, 'silence')
    if not os.path.exists(silencepath):
      os.makedirs(silencepath) 
    os.system('mv ' + path + '/silence*.wav ' + silencepath + '/')
    
if os.path.exists('_background_noise_'):
  for files in glob.glob('_background_noise_' + '/*.wav'):
    os.system('mv ' + files + ' ' + args.source + '/silence_' + args.source + os.path.basename(files))


if args.filename == None:
  for files in glob.glob(args.source +'/*.wav'):
    _, filename = os.path.split(files)
    print(filename)
    if re.match('silence.', filename):
        count = 0
        split1sec(filename,count)
        move_files(filename)
    else:
        split_silence(filename)
        move_files(filename)
elif re.match('silence.', args.filename):
  count = 0
  split1sec(filename,count)
  move_files(args.filename)
else:
  split_silence(args.filename)
  move_files(args.filename)
