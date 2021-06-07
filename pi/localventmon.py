#!/usr/bin/env python

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

# loop for menu
def menu_loop():
    while True:          
        print_menu()    
        choice = input("please select from the above menu [1-" + str(len(menuStrings)) + "]: ")
        choice = int(choice) 
        if choice == 1:     
            print("\n", 5 * "-", menuStrings[choice - 1], 5 * "-")  
            start_ventmon() 
        elif choice == 2:
            print("\n", 5 * "-", menuStrings[choice - 1], 5 * "-")  
            ## You can add your code or functions here
        elif choice == 3:
            print("\n", 5 * "-", menuStrings[choice - 1], 5 * "-")  
            print("Menu 3 has been selected")
            ## You can add your code or functions here
        elif choice == 4:
            print("\n", 5 * "-", menuStrings[choice - 1], 5 * "-")  
            print("Menu 3 has been selected")
            ## You can add your code or functions here
        elif choice == 5:
            print("\n", 5 * "-", menuStrings[choice - 1], 5 * "-")  
            ## You can add your code or functions here
            break;
        else:
            # Any integer inputs other than values 1-5 we print an error message
            input("EROR: please enter a number between 1 and " + str(len(menuStrings)) + "\n")


# kick off ventmon process
def start_ventmon():
    if check_serial() == True:
        start_docker()
        start_javascript()
        start_browser()
    else:
        print("ERROR: no VentMon connected")


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
        dockerClient.containers.run(name='logger', image='pirds-logger', detach='True', remove='True', ports=port_bindings, volumes=volume_binding) 
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
            dockerClient.containers.run(name='logger', image='pirds-logger', detach='True', remove='True', ports=port_bindings, volumes=volume_binding)  


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

    time.sleep(15)



# open browser 
def start_browser():
    os.system("chromium-browser http://localhost:8081 &")
    time.sleep(10)


# main
def main():
    menu_loop()

if __name__ == "__main__":
    main()


