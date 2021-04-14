import sox
import numpy as np
import argparse
import glob
import os

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

stat = sox.file_info.stat(args.source + '/' + args.filename)
amplitude = stat['Maximum amplitude']
print(stat)

threshold = (silence / amplitude) * 100

parent_dir = os.getcwd()
path = os.path.join(parent_dir, args.destination)

if not os.path.exists(path):
  os.makedirs(path)

os.system("cp " + args.source + '/' + args.filename + " " + args.source + '/temp.wav')
os.system("sox " + args.source + '/temp.wav ' + args.destination + "/" + args.filename + " silence 1 " \
+ str(args.duration) + " " + str(threshold) + "% 1 " + str(args.duration) + " " + str(threshold) + "% : newfile : restart")
#Fudge as : newfile : restart creates an extra null file
list_of_files = sorted(glob.glob(path + '/*.wav')) 
os.remove(list_of_files[len(list_of_files)-1]) 
