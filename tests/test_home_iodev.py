

from pydevmgr_vlt import VltIoDev
from pydevmgr_core import wait, DataLink  
import time 



io = VltIoDev( "m1", address="opc.tcp://192.168.1.11:4840", prefix="MAIN.IODev1")


if __name__ == "__main__":
    try:
        io.connect()
        io.set_do( [True, False] ) 
        print(io.stat.di_1.get())
        
        data = VltIoDev.StatInterface.Data()
        dl = DataLink( io.stat, data )
        dl.download()
        print(data)
    finally:
        io.disconnect()
