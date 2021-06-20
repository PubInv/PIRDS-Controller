#!/usr/bin/env python
# TODO list
# 1. fix the python-docker API run command (need to ask Rob)
# 2. implement serial port change function
# 2. figure out how to improve timing without using wait()


import os
import signal
import subprocess
import serial
import docker
import time

# constants 
serialFd = "/dev/ttyUSB0"
serialBaudrate = 500000

# docker stuff
port_bindings = {'8081/tcp' : 80, '6111/udp' : 6111}
volume_binding = {'/home/pi/VentMon/PIRDS-docker-local/logger_src/data' : {'bind': '/data', 'mode': 'rw'}}


# top menu    
menuStrings = ["START local VentMon", "STOP local VentMon", "change serial port info", "check for updates", "quit"]
def print_menu():      
    print(30 * "-" , "VENTMON LOCAL" , 30 * "-")
    print("1. " , menuStrings[0]) 
    print("2. " , menuStrings[1])
    print("3. " , menuStrings[2])
    print("4. " , menuStrings[3])
    print("5. " , menuStrings[4])
    print(67 * "-") 


# kick off ventmon process
def start_ventmon():
    if check_serial() == True:
        start_docker()
        start_javascript()
        start_browser()
    else:
        print("ERROR: no VentMon connected")
  

# stop local VentMon
def stop_ventmon():
  os.system("cd ~")
  os.system("pkill -9 node")
  os.system("docker stop logger")


# change the device file desciptor
def change_serial_info():

  print("function to change serial info")


# check for updates on git
def check_for_updates():

  print("function to check for repo updates")


# exit the menu loop
def exit_menu():
  print("exiting local VentMon menu")
  exit()


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
    menuFunctions = (start_ventmon, stop_ventmon, change_serial_info, check_for_updates, exit_menu)
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
        print("FIXME!")
        print(ser.is_open)
    return ser.is_open


# start docker 
def start_docker():
    dockerClient = docker.from_env()
    # check to see if we have any containers running (only expect one to be running)
    if len(dockerClient.containers.list()) == 0:
        print("starting docker image...")
        dockerClient.images.build(path="/home/pi/VentMon/PIRDS-docker-local", tag="pirds-logger")
        os.system("docker run -d --rm --name logger -p 8081:80 -p 6111:6111/udp -v `pwd`/logger_src/data:/data pirds-logger")
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
            os.system("docker run -d --rm --name logger -p 8081:80 -p 6111:6111/udp -v `pwd`/logger_src/data:/data pirds-logger")
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
    # os.chdir("/home/pi/VentMon/vent-display")
    os.system("node /home/pi/VentMon/vent-display/serialserver.js --uaddress=127.0.0.1 --sport=/dev/ttyUSB0 --uport=6111 &")
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


