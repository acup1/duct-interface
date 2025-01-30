import serial

serport = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
while True:
    while serport.inWaiting() > 0:
        c = serport.read()
        print(c)