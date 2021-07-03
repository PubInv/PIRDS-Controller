#!/usr/bin/env python
# TODO list
# 3. figure out how to improve timing of browser / js without using wait()


import os
import signal
import subprocess
import serial
import docker
import time
import re
import os.path 
import shutil
import requests
from difflib import Differ 

# installation paths
pihome = '/home/pi'
vent_home = '/home/pi/VentMon'
vent_display = '/home/pi/VentMon/vent-display'
pirds_controller = '/home/pi/VentMon/PIRDS-Controller'
pirds_docker = '/home/pi/VentMon/PIRDS-docker-local'

# constants 
serialFd = "/dev/ttyUSB0"
serialBaudrate = 500000

# docker stuff
port_bindings = {'8081/tcp' : 80, '6111/udp' : 6111}
volume_binding = {'/home/pi/VentMon/PIRDS-docker-local/logger_src/data' : {'bind': '/data', 'mode': 'rw'}}


# top menu    
menuStrings = ["START local VentMon", "STOP local VentMon", "change serial port info", "install local VentMon", "check for updates", "quit"]

# print the menu options
def print_menu(): 
    os.system("clear")     
    print(30 * "-" , "VENTMON LOCAL" , 30 * "-")
    for i in range(0, len(menuStrings)):
      print(i + 1, menuStrings[i]) 
    print(75 * "-") 


# kick off ventmon process
def start_ventmon():
    if check_serial() == True:
        start_docker()
        start_javascript()
        start_browser()
    else:
        print("ERROR: no VentMon connected")
        print("please ensure you've followed the steps in menu options 1 and 4")
        wait_for_continue_input()


# stop local VentMon
def stop_ventmon():
  print("stopping VentMon processes")
  os.system("cd ~")
  os.system("pkill -9 node")
  os.system("docker stop logger")


# change the device file desciptor
def change_serial_info():
  global serialFd
  print("current serial port is: " + serialFd)
  serialfd_temp = 'set()'
  while serialfd_temp == 'set()':
   serialfd_temp = get_serial_info() 

  serialFd = serialfd_temp
  print("new serial port is: " + serialFd)
  wait_for_continue_input()


# get the string containing the serial port info
def get_serial_info():
  # ask the user to unplug then re-plug the VentMon
  print("please make sure that your VentMon is NOT connected via USB")
  wait_for_continue_input()
  print("checking serial connections")
  os.system("ls -1 /dev/tty* > devOut_a.txt")
  print("please CONNECT your VentMon via USB")
  wait_for_continue_input()
  time.sleep(5)
  print("checking serial connections")
  os.system("ls -1 /dev/tty* > devOut_b.txt")
  # find the difference in available devices 
  with open('devOut_a.txt') as fileA:
    fileA_text = fileA.readlines() 
  with open('devOut_b.txt') as fileB:
    fileB_text = fileB.readlines()

  setA = set(fileA_text)
  setB = set(fileB_text)

  diff = setB.difference(setA)
  strDiff = str(diff)

  diff = setB.difference(setA)
  strDiff = str(diff)

  a = strDiff.replace('\\n', '')
  b = a.replace('{', '')
  c = b.replace('}', '')
  d = c.replace("'", '')
  
  os.system("rm devOut_*")

  return d


# check for updates on git
def check_for_updates():
  print("THIS FUNCTIONALITY HAS NOT BEEN IMPLEMENTED")
  print("function to check for repo updates")


# setup installation
def install_ventmon():
  # update and upgrade
  os.system("sudo apt-get update")
  os.system("sudo apt-get upgrade")
  # check for git
  if shutil.which("git") == None:
    os.system("sudo apt-get install git")

  # setup repos
  if os.path.isdir(vent_home) == False: 
    os.mkdir(vent_home)
    os.chdir(vent_home)
  else:
    print(vent_home, " already exists")

  # vent-display
  if os.path.isdir(vent_display) == False:
    os.chdir(vent_home)
    os.system("git clone https://github.com/PubInv/vent-display.git")
  else:
    print(vent_display, "already exists, updating repo...")
    os.chdir(vent_display)
    os.system("git pull origin master")

  # PIRDS-Controller
  if os.path.isdir(pirds_controller) == False:
    os.chdir(vent_home)
    os.system("git clone https://github.com/PubInv/PIRDS-Controller.git")
  else:
    print(pirds_controller, "already exists, updating repo...")
    os.chdir(pirds_controller)
    os.system("git pull origin main")

  # PIRDS-docker-local
  if os.path.isdir(pirds_docker) == False:
    os.chdir(vent_home)
    os.system("git clone https://github.com/PubInv/PIRDS-docker-local.git")
  else:
    print(pirds_docker, "already exists, updating repo...")
    os.chdir(pirds_docker)
    os.system("git pull origin main")
  
  # install docker
  if shutil.which("docker") == None:
   os.system("curl -fsSL https://get.docker.com -o get-docker.sh")
   os.system("sudo sh get-docker.sh")
   os.system("sudo dpkg --configure -a")
   os.system("sudo usermod -aG docker pi")
   os.system("sudo reboot")
  else:
   print("docker is already installed")

  # download new libseccomp2
  if os.path.exists("/home/pi/Downloads/libseccomp2_2.5.1-1_armhf.deb") == False:
    url = "http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.1-1_armhf.deb"
    r = requests.get(url, allow_redirects=True)
    os.system("cd ~/Downloads/")
    os.system("sudo dpkg -i libseccomp2_2.x.x-1+b1_armhf.deb")
  else:
   print("libseccomp is ready to go")

  # javascript
  if shutil.which("node") == None:
    os.chdir(vent_home)
    os.system("curl -sL https://deb.nodesource.com/setup_14.x | sudo bash -")
    os.system("sudo apt-get install -y nodejs")
    os.system("sudo apt-get install npm")
  else:
    print("node is already installed")
    
  # check to see if the necessayr node packages are installed
  yargsInstall = subprocess.run(["npm", "ls", "yargs", "--json"], capture_output=True, text=True).stdout
  corsInstall = subprocess.run(["npm", "ls", "cors", "--json"], capture_output=True, text=True).stdout
  expressInstall = subprocess.run(["npm", "ls", "express", "--json"], capture_output=True, text=True).stdout
  serialportInstall = subprocess.run(["npm", "ls", "serialport", "--json"], capture_output=True, text=True).stdout
  if yargsInstall == "{}\n":
    os.chdir(vent_home)
    os.system("npm install yargs")
  if corsInstall == "{}\n":
    os.chdir(vent_home)
    os.system("npm install cors")
  if expressInstall == "{}\n":
    os.chdir(vent_home)
    os.system("npm install express")
  if serialportInstall == "{}\n":
    os.chdir(vent_home)
    os.system("npm install serialport")
  else:
    print("node packages are installed")
  
  print("installation is complete")
  wait_for_continue_input()
                         

# exit the menu loop
def exit_menu():
  print("exiting local VentMon menu")
  exit()


# wait for user to type c to continue setup
def wait_for_continue_input():
    while True:    
        try:
            cont = input("\nplease type c to continue ")
            if cont == "c": 
                return True
        except (ValueError, TypeError):
            pass


# handle menu input from user
def get_menu_choice():
    while True:    
        try:
            number = int(input("please select from the above menu [1-" + str(len(menuStrings)) + "]: "))
            if 1 <= number <= len(menuStrings):
                return number
        except (ValueError, TypeError):
            pass

  
# loop for menu
def menu_loop():
  menuFunctions = (start_ventmon, stop_ventmon, change_serial_info, install_ventmon, check_for_updates, exit_menu)
  while True:          
    print_menu()   
    choice = get_menu_choice() 
    print("\n", 5 * "-", menuStrings[choice - 1], 5 * "-") 
    menuFunctions[choice - 1]() 


# check whether ventmont is active on expected serial port
def check_serial():
    print("checking serial port: " , serialFd)
    ser = serial.Serial()
    ser.baudrate = serialBaudrate
    ser.port = serialFd
    # print(ser)
    try:
        ser.open()
    except:
        print("please return to main menu and selct option 4")
        print(ser.is_open)
    return ser.is_open


# start docker 
def start_docker():
    dockerClient = docker.from_env()
    # check to see if we have any containers running (only expect one to be running)
    if len(dockerClient.containers.list()) == 0:
        print("starting docker image...")
        dockerClient.images.build(path="/home/pi/VentMon/PIRDS-docker-local", tag="pirds-logger")
        os.system("docker run -d --rm --name logger -p 8081:80 -p 6111:6111/udp -v /home/pi/VentMon/PIRDS-docker-local/logger_src/data:/data pirds-logger")
        # dockerClient.containers.run(name='logger', image='pirds-logger', detach='True', remove='True', ports=port_bindings, volumes=volume_binding) 
    else:
        # get the container with the logger image and check whether it's running
        container = dockerClient.containers.get('logger')
        containerState = container.attrs['State']
        if container.attrs['State']['Status'] == "running":
            print("docker image is already running...")
        else:
            # if the contaier has been run, but is not currently running stop and re-start it
            print("re-starting docker image...")
            container.stop()
            dockerClient.images.build(path="/home/pi/VentMon/PIRDS-docker-local/", tag="pirds-logger")
            os.system("docker run -d --rm --name logger -p 8081:80 -p 6111:6111/udp -v `/home/pi/VentMon/PIRDS-docker-local/logger_src/data:/data pirds-logger")
            # dockerClient.containers.run(name='logger', image='pirds-logger', detach='True', remove='True', ports=port_bindings, volumes=volume_binding)  


# start vent display js
def start_javascript():
    print("starting javascript...")
    
    pidOutput = subprocess.run(["pidof", "node"], capture_output=True, text=True).stdout
    if len(pidOutput) != 0:
      print("node was already running")
      print("pid of node process: " + pidOutput.strip('\n'))
      print("killing existing node process")
      os.kill(int(pidOutput), signal.SIGTERM)
      print("restarting node process")
    
    # start the javascript
    os.system("node /home/pi/VentMon/vent-display/serialserver.js --uaddress=127.0.0.1 --sport=" + serialFd + " --uport=6111 &")
    os.chdir("/home/pi/VentMon/")

    pidOutput = subprocess.run(["pidof", "node"], capture_output=True, text=True).stdout
    print("pid of node process: " + pidOutput.strip('\n'))

    time.sleep(10)


# open browser 
def start_browser():
    os.system("chromium-browser --kiosk http://localhost:8081 &")
    time.sleep(10)


# main
def main():
    menu_loop()

if __name__ == "__main__":
    main()


