#!/bin/sh
W1MOD="dtoverlay=w1-gpio"
grep -qxF $W1MOD boot/config.txt || echo $W1MOD >> boot/config.txt

# Install pigpio
sudo apt install pigpio python3-pigpio
systemctl enable pigpiod
systemctl start pigpiod
