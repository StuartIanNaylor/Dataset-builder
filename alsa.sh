#!/bin/bash
sudo mv -f /etc/asound.conf /etc/asound.old
echo "/etc/asound.conf will be renamed /etc/asound.old if exists"
arecord -l

echo 'The above is a list of recording cards'
read -p "Select the card index to use (0 - X) : " index

echo 'OK plug in your mic and we will test the current mic volume'
echo "You may want to check the 'alsamixer -c $index' press F5 for capture and check levels 1st, you can ctrl+c to exit"
echo "'sudo alsactl store $index' will persist those settings through reboot"
read -p "Press enter : Then repeat your KW @near 0.3m approx as you would normally (start 10 sec rec time)" var
sleep 1
arecord -D plughw:$index -d 10 -V mono -r 16000 -f S16_LE -c 1 vol.wav
echo
stat=$(sox vol.wav -n stats  2>&1 | grep "Pk lev dB" | sed 's/[^0-9.-]*//g')
echo
echo $stat

softvol=$(echo "x = $stat; scale = 0; x / 1" | bc -l)
echo $softvol
maxdb=$(echo ${softvol#-}.0)
echo $maxdb

echo "#pcm default to allow auto software plughw converion" | sudo tee -a /etc/asound.conf > /dev/null
echo "pcm.!default {" | sudo tee -a /etc/asound.conf > /dev/null
echo "  type asym" | sudo tee -a /etc/asound.conf > /dev/null
echo "  playback.pcm \"play\"" | sudo tee -a /etc/asound.conf > /dev/null
echo "  capture.pcm \"agc\"" | sudo tee -a /etc/asound.conf > /dev/null
echo "}" | sudo tee -a /etc/asound.conf > /dev/null
echo "#pcm is pluhw so auto software conversion can take place" | sudo tee -a /etc/asound.conf > /dev/null
echo "#pcm hw: is direct and faster but likely will not support sampling rate" | sudo tee -a /etc/asound.conf > /dev/null
echo "pcm.play {" | sudo tee -a /etc/asound.conf > /dev/null
echo "  type plug" | sudo tee -a /etc/asound.conf > /dev/null
echo "  slave {" | sudo tee -a /etc/asound.conf > /dev/null
echo "    pcm \"plughw:$index,0\"" | sudo tee -a /etc/asound.conf > /dev/null
echo "  }" | sudo tee -a /etc/asound.conf > /dev/null
echo "}" | sudo tee -a /etc/asound.conf > /dev/null
echo | sudo tee -a /etc/asound.conf > /dev/null
echo "#pcm is pluhw so auto software conversion can take place" | sudo tee -a /etc/asound.conf > /dev/null
echo "#pcm hw: is direct and faster but likely will not support sampling rate" | sudo tee -a /etc/asound.conf > /dev/null
echo "pcm.cap {" | sudo tee -a /etc/asound.conf > /dev/null
echo "  type plug" | sudo tee -a /etc/asound.conf > /dev/null
echo "  slave {" | sudo tee -a /etc/asound.conf > /dev/null
echo "    pcm \"plughw:$index,0\"" | sudo tee -a /etc/asound.conf > /dev/null
echo "    }" | sudo tee -a /etc/asound.conf > /dev/null
echo "}" | sudo tee -a /etc/asound.conf > /dev/null
echo | sudo tee -a /etc/asound.conf > /dev/null
echo "pcm.agc {" | sudo tee -a /etc/asound.conf > /dev/null
echo " type speex" | sudo tee -a /etc/asound.conf > /dev/null
echo " slave.pcm \"gain\"" | sudo tee -a /etc/asound.conf > /dev/null
echo " agc off" | sudo tee -a /etc/asound.conf > /dev/null
echo " agc_level 2000" | sudo tee -a /etc/asound.conf > /dev/null
echo " denoise off" | sudo tee -a /etc/asound.conf > /dev/null
echo "}" | sudo tee -a /etc/asound.conf > /dev/null
echo | sudo tee -a /etc/asound.conf > /dev/null
echo "pcm.gain {" | sudo tee -a /etc/asound.conf > /dev/null
echo " type softvol" | sudo tee -a /etc/asound.conf > /dev/null
echo "   slave {" | sudo tee -a /etc/asound.conf > /dev/null
echo "   pcm \"cap\"" | sudo tee -a /etc/asound.conf > /dev/null
echo "   }" | sudo tee -a /etc/asound.conf > /dev/null
echo " control {" | sudo tee -a /etc/asound.conf > /dev/null
echo "   name \"Mic Gain\"" | sudo tee -a /etc/asound.conf > /dev/null
echo "   count 2" | sudo tee -a /etc/asound.conf > /dev/null
echo "   card $index" | sudo tee -a /etc/asound.conf > /dev/null
echo "   }" | sudo tee -a /etc/asound.conf > /dev/null
echo " min_dB -40.0" | sudo tee -a /etc/asound.conf > /dev/null
echo " max_dB $maxdb" | sudo tee -a /etc/asound.conf > /dev/null
echo " resolution 80" | sudo tee -a /etc/asound.conf > /dev/null
echo "}" | sudo tee -a /etc/asound.conf > /dev/null
echo | sudo tee -a /etc/asound.conf > /dev/null
echo "#sudo apt-get install asound2-plugins" | sudo tee -a /etc/asound.conf > /dev/null
echo "#will use lower load but poorer linear resampling otherwise" | sudo tee -a /etc/asound.conf > /dev/null
echo "defaults.pcm.rate_converter \"speexrate\"" | sudo tee -a /etc/asound.conf > /dev/null

arecord -d 1 -r 16000 -f S16_LE -c 1 /dev/null
amixer -c1 cset numid=10 79
sudo alsactl store 1

