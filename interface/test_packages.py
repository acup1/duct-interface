import serial
from time import time
import asyncio
import threading
import struct
from crccheck.crc import Crc16Modbus as c16
from crccheck.crc import Crc8MaximDow as c8


class pactest():
    def __init__(self):pass

    def crc8(self, array):
        return c8.calc(array)

    def crc16(self, array):
        a=hex(c16.calc(array))[2:]
        return int(a,16)

    def crc(self,command):
        if str(type(command))=="<class 'bytes'>":pass
        else:command=command.encode("ASCII")
        if len(command)<9:
            crc=bytes.fromhex( ('0' +  hex(self.crc8(command))[2:] ) [-2:] )
        else:
            crc=bytes.fromhex( ('000' +  hex(self.crc16(command))[2:] ) [-4:] )
        return crc

p=pactest()
read='read\x0a\x0d\x00'.encode("ASCII")+p.crc('read\x0a\x0d\x00')

a=b'\x01\x00\x00\x00\x0c\x00\x00\x00\x00\x00\xa0\xc0\x00\x00T\xc2\x00\x00<\xc2\x00\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x10eE\x00\x00\x00\x00\xbb3\x00\x002\x00\xb9\x00\xfa\x00\x00\x00\xb6\xdd'
#print(len(a), p.crc(a[:-2])==a[-2:])

def bytes_to_float(bytes_data):
    return int.from_bytes(bytes_data, "little", signed="True")
    return int(str(bytes_data[::-1])[4:-1].replace("\\x",""),16)/100

print(a[4:8],"-",int(bytes_to_float(a[4:8]))/100)

