from pydevmgr_core.base.dataclass import set_data_model
from pydevmgr_vlt.base import VltDevice, register
from pydevmgr_core import  NodeVar
from pydevmgr_ua import UaInt32, UaInt16
from valueparser import Parser
from enum import Enum 
from typing import Optional 
from pydevmgr_vlt.devices.vltmotor.positions import PositionsConfig
from pydevmgr_vlt.devices._tools import _inc 

Base = VltDevice.Ctrl

N = Base.Node # Base Node
NC = N.Config
NV = NodeVar # used in Data 

to_int16 = UaInt16().parse 
to_int32 = UaInt32().parse

class MOTOR_COMMAND(int, Enum):
    NONE = _inc(0)
    INITIALISE = _inc()
    SET_POSITION = _inc()
    MOVE_ABSOLUTE = _inc()
    MOVE_RELATIVE = _inc()
    MOVE_VELOCITY = _inc()
    NEW_VELOCITY = _inc()
    NEW_POSITION = _inc()
    CLEAR_NOVRAM = _inc()

@register
class MotorCommand(Parser):
    @staticmethod
    def __parse__(value, config):
        if isinstance(value, str):
            value =  getattr(MOTOR_COMMAND, value)
        return to_int32(value)


class DIRECTION(int, Enum):
    POSITIVE = _inc(1)
    SHORTEST = _inc()
    NEGATIVE = _inc()
    CURRENT  = _inc()



@set_data_model
class VltMotorCtrl(Base):
    COMMAND = MOTOR_COMMAND
    DIRECTION = DIRECTION
    
    class Config(Base.Config):
        command:    NC  =  NC(  suffix=  'ctrl.nCommand',  vtype=int,   parser=  MotorCommand  )
        direction:  NC  =  NC(  suffix=  'ctrl.nDirection',vtype=(DIRECTION, DIRECTION.POSITIVE),   parser=DIRECTION     )
        position:   NC  =  NC(  suffix=  'ctrl.lrPosition',  vtype=float,  parser=  'UaDouble'   )
        velocity:   NC  =  NC(  suffix=  'ctrl.lrVelocity',  vtype=float, parser=  'UaDouble'    )
        stop:       NC  =  NC(  suffix=  'ctrl.bStop',        vtype=bool, parser=  bool          )
        reset:      NC  =  NC(  suffix=  'ctrl.bResetError',  vtype=bool, parser=  bool          )
        disable:    NC  =  NC(  suffix=  'ctrl.bDisable',     vtype=bool, parser=  bool          )
        enable:     NC  =  NC(  suffix=  'ctrl.bEnable',      vtype=bool, parser=  bool          )
        execute:    NC  =  NC(  suffix=  'ctrl.bExecute',     vtype=bool, parser=  bool          )

if __name__=="__main__":
    VltMotorCtrl()
