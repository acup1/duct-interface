import serial
from time import time,sleep
import asyncio
import threading
import struct
from crccheck.crc import Crc16Modbus as c16
from crccheck.crc import Crc8MaximDow as c8
import traceback

def dw2float(dw_array):
    dw_array=[byte for byte in dw_array]
    assert (len(dw_array) == 4)
    dw = int.from_bytes(dw_array, byteorder='little',signed=False)
    s = -1 if (dw >> 31) == 1 \
        else 1                                    # Знак
    e = ( dw >> 23 ) & 0xFF;                      # Порядок
    m = ((dw & 0x7FFFFF ) | 0x800000) if e != 0 \
        else ((dw & 0x7FFFFF ) << 1)              # Мантисса
    m1 = m*(2**(-23))                             # Мантисса в float
    return s*m1*(2**(e-127))

def wtf(a):
    assert (len(a) == 2)
    return int(a.hex()[2:]+a.hex()[:2],16)


def bytes_to_float(bytes_data):
    return int.from_bytes(bytes_data, "little", signed="True")
    return int(str(bytes_data[::-1])[4:-1].replace("\\x",""),16)/100

class serial_worker():
    buffer=b''
    send_buffer=[]
    x=d1=d2=d3=time=temp=0
    mode=1
    rezhim_parametrv=False
    parameter_number=parameter_value=0
    zapros_parameter_number=0
    ACP=[0 for _ in range(8)]
    xx=0
    changed_param={}

    KL=KR=ES=HO=CO=LO=0

    def __init__(self, device, rate, spam=True, echo=True):
        self.dev=device
        self.rate=rate
        self.spam=spam
        self.echo=echo
        self.err_count=0
        self.Running=True
        self.package_crc=False
        self.ser=serial.Serial(self.dev, self.rate)
        self.tasker()
        self.bx=[]
        self.bd1=[]
        self.bd2=[]
        self.bd3=[]
        self.send_command("SETNR\x0a\x0d")

    def clear_buffer(self):
        self.bx=[]
        self.bd1=[]
        self.bd2=[]
        self.bd3=[]
    
    def tasker(self):
        threading.Thread(target=self.start_read_serial_data).start()
        
    def start_read_serial_data(self):
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.read_serial_data())

    async def read_serial_data(self):
        timer=time()
        while self.Running:
            try:
                data = self.ser.read_all()
                if data:
                    self.package_crc=(self.crc(data[:-2])==data[-2:] or self.crc(data[:-2])==data[-2:][-1])
                    if self.package_crc:
                        self.err_count=0
                        self.mode=data[0]%128
                        if len(data)==54:
                            #print("ok")
                            self.x=int(bytes_to_float(data[4:8]))/10
                            self.d1=dw2float(data[8:12])
                            self.d2=dw2float(data[12:16])
                            self.d3=dw2float(data[16:20])
                            if self.mode==5:
                                self.bx.append(self.x)
                                self.bd1.append(self.d1)
                                self.bd2.append(self.d2)
                                self.bd3.append(self.d3)

                            self.md1=dw2float(data[24:28])
                            self.md2=dw2float(data[28:32])
                            self.md3=dw2float(data[32:36])
                            self.time=bytes_to_float(data[40:44])/1000
                            self.temp=bytes_to_float(data[46:48])/10

                            ds=("0"*8+bin(int(bytes([data[50]]).hex(),16))[2:])[-8:]
                            
                            self.KL=1 if int(ds[-1]) else 0
                            self.KR=1 if int(ds[-2]) else 0
                            self.ES=1 if int(ds[-3]) else 0
                            self.HO=1 if int(ds[-4]) else 0
                            self.CO=1 if int(ds[-5]) else 0
                            self.LO=1 if int(ds[-6]) else 0

                        elif len(data)==30:
                            if self.mode==7:
                                ds=("0"*8+bin(int(bytes([data[2]]).hex(),16))[2:])[-8:]
                                self.KL=1 if int(ds[-1]) else 0
                                self.KR=1 if int(ds[-2]) else 0
                                self.ES=1 if int(ds[-3]) else 0
                                self.HO=1 if int(ds[-4]) else 0
                                self.CO=1 if int(ds[-5]) else 0
                                self.LO=1 if int(ds[-6]) else 0
                                #print(bytes_to_float(data[24:28]))
                                self.xx=bytes_to_float(data[24:28])
                                #print(self.xx)
                                #print(data[3],data[4:6])
                                self.parameter_number=int(data[3])
                                self.parameter_value=wtf(data[4:6])
                                for x in range(6,19,2):
                                    self.ACP[(x-6)//2]=wtf(data[x:x+2])

                                if len(self.changed_param.keys())>0:
                                    for i in list(self.changed_param.keys()):
                                        if i==self.parameter_number:
                                            if self.changed_param[i][0]!=self.parameter_value and self.changed_param[i][1]<10:
                                                self.send_param(i,self.changed_param[i][0])
                                                self.changed_param[i][1]+=1
                                            else:
                                                del self.changed_param[i]
                                            
                                #print("param:")
                                #print(self.parameter_number,self.parameter_value)
                    else:
                        self.err_count+=1
                        print("crc err", self.err_count)
                        print(data)
                        print()

                if len(self.send_buffer)>0:
                    self.send_bytes(self.send_buffer[0])
                    self.send_buffer=self.send_buffer[1:]
                await asyncio.sleep(.2)
                if len(self.send_buffer)==0 and self.spam:
                    if self.rezhim_parametrv:
                        if len(self.changed_param.keys())==0:
                            c="PR".encode()+bytes([0])+'00\n\r'.encode()
                        else:
                            c="PR".encode()+bytes([list(self.changed_param.keys())[0]])+'00\n\r'.encode()
                        self.send_bytes(c+self.crc(c))
                    else:
                        #if time()-timer>=.2:
                        #    self.send_bytes('read\x0a\x0d\x00'.encode("ASCII")+self.crc('read\x0a\x0d\x00'))
                        #    timer=time()
                        self.send_command('READ\x0a\x0d\x00')
            except Exception as e:
                traceback.print_exc()
                self.ser=serial.Serial(self.dev, self.rate)



    def crc8(self, array):
        return c8.calc(array)

    def crc16(self, array):
        a=hex(c16.calc(array))[2:]
        return int(a,16)
        a=a[2:]+a[:2]
        return int(a,16)

    def numtobytes(self,num):
        if not (0 <= num <= 65535):
            raise ValueError("Number must be between 0 and 65535")
        
        byte1 = (num >> 8) & 0xFF
        byte2 = num & 0xFF
        
        return bytes([byte1, byte2])
        return bytes([int(("00"+hex(num)[2:])[-4:][:2],16),int(("00"+hex(num)[2:])[-4:][2:],16)])

    def send_param(self,n,x):
        #print(b"pw"+bytes([n])+self.numtobytes(x)+b"\x0a\x0d")
        self.changed_param[n]=[x,0]
        self.send_command((b"PW"+bytes([n])+self.numtobytes(x)+b"\x0a\x0d"))

    def read_param(self,n):
        #self.zapros_parameter_number=n
        self.send_command((b"PR"+bytes([n])+b'00\n\r'))

    def send_bytes(self,b):
        self.ser.write(b)

    def crc(self,command):
        if str(type(command))=="<class 'bytes'>":pass
        else:command=command.encode("ASCII")
        if len(command)<=9:
            crc=bytes.fromhex( ('0' +  hex(self.crc8(command))[2:] ) [-2:] )
        else:
            crc=bytes.fromhex( ('000' +  hex(self.crc16(command))[2:] ) [-4:] )
        return crc

    def send_command(self,command):
        try:
            if self.echo:
                print("sended:",command.encode("ASCII"))
        except:pass

        if str(type(command))=="<class 'bytes'>":pass
        else:command=command.encode("ASCII")
        c=command+self.crc(command)
        if c not in self.send_buffer:
            self.send_buffer.append(c)

if __name__=="__main__":
    s=serial_worker("/dev/ttyS3",115200, spam=False)
    def help():
        print('''
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
возможности:                     ┃
q            exit                ┃
h            help                ┃
↵            read                ┃
1            start               ┃
2            stop                ┃
3            normal              ┃
4            params              ┃
pr N         read param          ┃
pw N VAL     write param         ┃
ввод любой команды или её начала ┃
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
''')
    help()
    while True:
        a=str(input("cmd: "))
        if a=="q":
            s.Running=False
            break
        if a=="h":
            help()
        elif a=="":
            s.send_command('READ\x0a\x0d\x00')
            sleep(.1)
            print("crc:",s.package_crc, sep="\t")
            print("mode:",s.mode, sep="\t")
            if s.mode!=7:
                print("x:",s.x, sep="\t")
                print("d1:",s.d1, sep="\t")
                print("d2:",s.d2, sep="\t")
                print("d3:",s.d3, sep="\t")
                print("max d1:",s.md1, sep="\t")
                print("max d2:",s.md2, sep="\t")
                print("max d3:",s.md3, sep="\t")
                print("time:",s.time, sep="\t")
                print("temp:",s.temp, sep="\t")
            else:
                print("N:",s.parameter_number, sep="\t")
                print("val:",s.parameter_value, sep="\t")

        elif a=="1":
            s.send_command('STA____')
            sleep(.1)
            print("crc:",s.package_crc, sep="\t")
        elif a=="2":
            s.send_command('STO____')
            sleep(.1)
            print("crc:",s.package_crc, sep="\t")
        elif a=="3":
            s.send_command('SE_N___')
            sleep(.1)
            print("crc:",s.package_crc, sep="\t")
            print("mode:",s.mode, sep="\t")
        elif a=="4":
            s.send_command('SE_P___')
            sleep(.1)
            print("crc:",s.package_crc, sep="\t")
            print("mode:",s.mode, sep="\t")
        elif ("pr" in a) and len(a.split())==2:
            n=int(a.split()[1])
            s.read_param(n)
            sleep(.1)
            while s.parameter_number!=n:pass
            print("crc:",s.package_crc, sep="\t")
            print("N:",s.parameter_number, sep="\t")
            print("val:",s.parameter_value, sep="\t")
        else:
            s.send_command((a+7*"_")[:7])
            sleep(.1)
            print("crc:",s.package_crc, sep="\t")
        print()
