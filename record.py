#!/usr/bin/env python3
import argparse
import sounddevice as sd
import tempfile
import queue
import sys
import soundfile as sf
import os
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy

parser = argparse.ArgumentParser()
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
q = queue.Queue()

if args.list:
 print(sd.query_devices())
 exit()
 
if args.device:
  sd.default.device = args.device
  
def record(section, message):  
  try:
    if args.directory == None:
      args.directory = "rec"
      
    if not os.path.exists(args.directory):
      os.makedirs(args.directory)
      
    filename = tempfile.mktemp(prefix=str(section) + '_', suffix='.wav', dir=args.directory)

    # Make sure the file is opened before recording anything:
    with sf.SoundFile(filename, mode='x', samplerate=args.samplerate, channels=args.channels, subtype=args.subtype) as file:
        with sd.InputStream(samplerate=args.samplerate, device=args.device, channels=args.channels, callback=callback):
            print('#' * 80)
            print(message +' ' + section)
            print('#' * 80)
            while True:
                file.write(q.get())
  except KeyboardInterrupt:
    print('\nRecording finished: ' + repr(filename))
    q.queue.clear()
  except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
  
def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())
    
    
print('You can check mic levels with "arecord -D plughw:1 -V mono -r 16000 -f S16_LE -c 1 /dev/null"')
vinput = input("Do you wish to exit and check mic levels?:(y/n)\n")
if vinput.lower() == 'y':
  exit()
    
if not args.section:
  record("silence", 'after 1-2 minutes press Ctrl+C to stop recording')
  record("kw", 'repeat kw for 1-2 minutes press Ctrl+C to stop recording')
  record("notkw", 'press Ctrl+C to stop recording')
elif args.section == "silence":
  record("silence", 'after 1-2 minutes press Ctrl+C to stop recording')
elif args.section == "kw":
  record("kw", 'repeat kw for 1-2 minutes press Ctrl+C to stop recording')  
elif args.section == "notkw":
  record("notkw", 'press Ctrl+C to stop recording')


  
print("Hello")
