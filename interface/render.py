import threading,asyncio
from time import time

class render():
    def __init__(self,main,serial):
        self.main=main
        self.serial=serial
        threading.Thread(target=self.start_plotter).start()

    def start_plotter(self):
        loop=asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.plotter())


    async def plotter(self):
        main=self.main
        s=self.serial
        n=0
        #while True:pass

        while True:
            try:
                #print(int(time())%2)
                #if int(time())%5==0:
                main.lcd5.display(str(int(s.time)))
                main.lcd6.display(f"{float(s.temp):.1f}")
                #main.lcd4.display(0)
                main.lcd4.display(f"{float(s.x):.2f}")
                #print(s.x,main.lcd4.value())
                if main.testing_mode==False and s.mode==b'\x05':
                    s.send_command("stop\x0a\x0d\x00")
                
                if main.show_maxes:
                    main.lcd1.display(f"{float(max(s.bd1+[0])):.2f}")
                    main.lcd2.display(f"{float(max(s.bd2+[0])):.2f}")
                    main.lcd3.display(f"{float(max(s.bd3+[0])):.2f}")
                else:
                    main.lcd1.display(f"{float(s.bd1[-1]):.2f}")
                    main.lcd2.display(f"{float(s.bd2[-1]):.2f}")
                    main.lcd3.display(f"{float(s.bd3[-1]):.2f}")

                k=2
                if main.can_draw:
                    main.d1data[0]=s.bx[::k] 
                    main.d1data[1]=s.bd1[::k]

                    main.d2data[0]=s.bx[::k] 
                    main.d2data[1]=s.bd2[::k]

                    main.d3data[0]=s.bx[::k] 
                    main.d3data[1]=s.bd3[::k]
                    main.plot()
                    main.can_draw=False
                     
                if n%1==0:
                    main.processEvents()
                n+=1
                await asyncio.sleep(0.3)
            except: pass