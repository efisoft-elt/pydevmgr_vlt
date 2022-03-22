
from pydevmgr_vlt import VltMotor
from pydevmgr_core import wait , DataLink
import time 



m1 = VltMotor( "m1", address="opc.tcp://192.168.1.11:4840", prefix="MAIN.Motor001", 

        ctrl_config = VltMotor.Config.CtrlConfig( backlash=0.3, max_pos=10.0, min_pos=-10.0, axis_type="CIRCULAR")
)




if __name__ == "__main__":
    try:
        m1.connect()
        m1.configure()
        
  
        data = VltMotor.Data()
        dl = DataLink(m1, data)
        dl.download()
        print(data)

        print(m1.stat.pos_actual.get())
    
        wait( m1.enable() )
        wait(  m1.init() )
        #m1.reset()
        wait( m1.move_abs(4, 14.0), lag=0.5 )
        print(m1.stat.pos_actual.get())
        wait( m1.move_abs(-4, 14.0), lag=0.5 )
        print(m1.stat.pos_actual.get())
        wait( m1.move_rel( 4, 14.0), lag=0.5 )
        print(m1.stat.pos_actual.get())
        m1.move_vel( 1 )
        time.sleep(1)
        print(m1.stat.pos_actual.get())
        m1.move_vel( -1 )
        time.sleep(1)
        print(m1.stat.pos_actual.get())
        m1.stop()


    finally:
        m1.disconnect()
