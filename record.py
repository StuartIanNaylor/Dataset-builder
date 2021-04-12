import argparse
import sounddevice as sd

parser = argparse.ArgumentParser()
parser.add_argument("--device", help="Recording device index")
parser.add_argument("--list", help="List recording devices", action="store_true")
args = parser.parse_args()

sd.default.samplerate = 16000
sd.default.channels = 1


if args.list:
 print(sd.query_devices())
 exit()
 
if args.device:
  sd.default.device = args.device
