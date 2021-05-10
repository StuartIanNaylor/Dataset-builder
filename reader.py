import glob
import time
import os
import argparse
import sounddevice as sd
import soundfile as sf
import tempfile
from cfonts import render, say

parser = argparse.ArgumentParser()
parser.add_argument("-T", "--delay", help="Word delay time secs", type=float, default=2.5)
parser.add_argument("-L", "--language", help="Language en, fr, de, sp", type=str, default="en")
parser.add_argument("-d", "--device", help="recording device index", type=int)
parser.add_argument("-l", "--list", help="list recording devices", action="store_true")
parser.add_argument("-s", "--section", help="record section only", choices=["silence", "kw", "notkw"])
parser.add_argument('-r', '--samplerate', type=int, default=16000, help='sampling rate')
parser.add_argument('-c', '--channels', type=int, default=1, help='number of input channels')
parser.add_argument('-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
parser.add_argument('-D', '--directory', type=str, help='directory to save in')
args = parser.parse_args()

sd.default.samplerate = args.samplerate
sd.default.channels = args.channels

if args.list:
 print(sd.query_devices())
 exit()
 
if args.device:
  sd.default.device = args.device

def record(section, duration):  
  if args.directory == None:
    args.directory = "rec"
      
  if not os.path.exists(args.directory):
    os.makedirs(args.directory)
      
  filename = tempfile.mktemp(prefix=str(section) + '_', suffix='.wav', dir=args.directory)

  # Make sure the file is opened before recording anything:
  with sf.SoundFile(filename, mode='x', samplerate=args.samplerate, channels=args.channels, subtype=args.subtype) as file:
    myrecording = sd.rec(int(duration * args.samplerate))
    sd.wait()
    file.write(myrecording)


print("Setup up you mic @ 0.3m and test volumes are as high as possible")
print("After entering your keyword read out the words from the screen")
keyword = input("Please enter your keyword and press enter:\n")

sentence_count = 0
sentences = glob.glob(args.language + '*.txt')
for sentence in sentences:
  sentence_count += 1
  if sentence_count > 2:
    cont = input("Add more words for accuracy? (y/n):\n")
    sentence_count = 0
    if not cont == "y":
      break

  f1=open(sentence, "r")
  fl =f1.readlines()
  for x in fl:
    os.system('clear')
    output = render(x, font='huge', align='center')
    print(output)
    record("notkw",args.delay)
    os.system('clear')
    output = render(keyword, font='huge', align='center')
    print(output)
    record("kw", args.delay)
  
os.system('clear')
print("We are now going to record a minute of voice silence")
print("Try to make no noise for the minute as we record")
cont = input("Press enter to record voice silence:\n")
time.sleep(1)
record("silence", 60)


