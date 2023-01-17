from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_core.base.dataclass import set_data_model
from valueparser import BaseParser
from pydevmgr_vlt.base import VltDevice, register
from pydevmgr_vlt.devices._tools import _inc
from pydevmgr_ua import UaInt32
from enum import Enum
from pydantic import create_model
Base = VltDevice.Ctrl

N = Base.Node # Base Node
NC = N.Config
NV = NodeVar # used in Data 

to_int32 = UaInt32().parse

class COMMAND(int, Enum):
    NONE = 0
    INITIALISE = 1
    ACTIVATE = 2


N_AO, N_DO, N_NO, N_TO  = [8]*4



@register
class IoDevCommand(BaseParser):
    @staticmethod
    def __parse__(value, config):
        if isinstance(value, str):
            value =  getattr(COMMAND, value)
        return to_int32(value)


# some dinamicaly created nodes
io_nodes = {}
for i in range(N_DO):
    io_nodes[f'do_{i}'] = (NC, NC(suffix= f'ctrl.arr_DO[{i}].bValue', vtype=bool))
for i in range(N_AO):
    io_nodes[f'ao_{i}'] = (NC, NC(suffix= f'ctrl.arr_AO[{i}].lrValue', vtype=float))
for i in range(N_NO):
    io_nodes[f'no_{i}'] = (NC, NC(suffix= f'ctrl.arr_NO[{i}].nValue', vtype=int))
for i in range(N_TO):
    io_nodes[f'to_{i}'] = (NC, NC(suffix= f'ctrl.arr_TO[{i}].sValue', vtype=str))


@set_data_model
class VltIoDevCtrl(Base):
    COMMAND = COMMAND
    class Config(create_model("Config",  __base__ = Base.Config, **io_nodes)):
        execute: NC = NC(suffix= 'ctrl.bExecute', parser= 'bool', vtype=bool )
        command: NC = NC(suffix= 'ctrl.nCommand', parser= COMMAND, vtype=(COMMAND, COMMAND.NONE), output_parser=COMMAND )
        

if __name__ == "__main__":
    ctrl = VltIoDevCtrl()
    ctrl.do_3
    print( ctrl.Data() )
    print("OK")

