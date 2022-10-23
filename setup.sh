#!/bin/sh

echo "dtoverlay=w1-gpio" >> /boot/config.txt


# Install pigpio
sudo apt install pigpio python3-pigpio
systemctl enable pigpiod
systemctl start pigpiod

