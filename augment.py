import sox
import random
import glob
import argparse
import os

def get_voice_params(rec_file, silence_maximum_amplitude):
  
  tfm1 = sox.Transformer()
  stat = tfm1.stat(rec_file)
  file_maximum_amplitude = float(stat['Maximum amplitude'] )
  file_duration = float(stat['Length (seconds)'])
  
  percent_silence_threshold = silence_maximum_amplitude * (100 + args.silence_headroom)
  
  tfm1.silence(location=-1, min_silence_duration=args.file_min_silence_duration, silence_threshold=percent_silence_threshold, buffer_around_silence=True)
  tfm1.build(rec_file, '/tmp/silence1.wav')
  tfm1.clear_effects()
  stat = tfm1.stat('/tmp/silence1.wav')
  voice_end = float(stat['Length (seconds)'])

  tfm1.silence(location=1, min_silence_duration=args.file_min_silence_duration, silence_threshold=percent_silence_threshold, buffer_around_silence=True)
  tfm1.build('/tmp/silence1.wav', '/tmp/silence2.wav')
  tfm1.clear_effects()
  
  voice_stat = tfm1.stat('/tmp/silence2.wav')
  voice_start = voice_end - float(voice_stat['Length (seconds)'])

  return file_maximum_amplitude, file_duration, voice_start, voice_end