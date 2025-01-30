import serial
import asyncio
import threading
from crccheck.crc import Crc16Modbus as c16
from crccheck.crc import Crc8MaximDow as c8

class serial_worker():
    buffer=b''
    send_buffer=[]

    def __init__(self, device, rate):
        self.ser=serial.Serial(device, rate)
        self.simple_commands={
            'read':b'\x02'*4, #команда чтения пакета
            'start':b'\x0a'*4, #команда старт
            'stop':b'\x15'*4, #команда стоп
            'reset':b'\x20'*4, #команда обнуления
            'test':b'\x2a'*4, #команда переключ в реж испытания
            'check':b'\x30'*4, #команда переключ в реж проверка
            'right':b''*4, #команда движ вправо
            'left':b''*4, #команда движ влево
            'warm-on':b''*4, #команда вкл нагрев
            'warm-off':b''*4, #команда выкл нагрев
            'cold-on':b''*4, #команда вкл охлад
            'cold-off':b''*4, #команда выкл охлад
            #'':b'', #команда
        }
        self.tasker()
    
    def tasker(self):
        threading.Thread(target=self.start_read_serial_data).start()
        
    def start_read_serial_data(self):
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.read_serial_data())

    async def read_serial_data(self):
        while True:
            data = self.ser.read_all()
            if data:
                self.buffer+=data
                #print(data)
            if len(self.send_buffer)>0:
                self.send_bytes(self.send_buffer[0])
                self.send_buffer=self.send_buffer[1:]



    def crc8(self, array):
        return c8.calc(array)

    def crc16(self, array):
        a=hex(c16.calc(array))[2:]
        a=a[2:]+a[:2]
        return int(a,16)

    def numtobytes(self,num):
        return bytes([int(("00"+hex(num)[2:])[-4:][:2],16),int(("00"+hex(num)[2:])[-4:][2:],16)])


    def send_bytes(self,b):
        self.ser.write(b)

    def send_command(self,command):
        if len(command)<=9:
            crc=bytes.fromhex( ('0' +  hex(self.crc8(command.encode("ASCII")))[2:] ) [-2:] )
        else:
            crc=bytes.fromhex( ('000' +  hex(self.crc16(command.encode("ASCII")))[2:] ) [-4:] )
        self.send_buffer.append(command.encode("ASCII")+crc)



s=serial_worker("/dev/ttyS3",115200)

#a=[hex(i) for i in list(open("eeprom1.bin","rb").read())]
a=[0x01, 0xbe, 0x40, 0x11, 0x5a, 0x36, 0x00, 0xe1, 0x01, 0xb7, 0x62, 0xf7, 0x08, 0x00, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
#a=[0x41, 0x54, 0x5a, 0x0a, 0x0d, 0x00, 0x00]
#print(s.crc8(bytes(a)))
#print(hex(s.crc16(bytes(a))))
a=[0x71,0x77,0x65]
a='''
qwe
e
wq
e
'''

a='start\x0a\x0d'
s.send_command(a)
#s.send_bytes(a.encode("ASCII"))
#s.send_bytes(b'\x00\x00')

print(s.numtobytes(12))

while True:
    a=input()
    s.send_command(a)