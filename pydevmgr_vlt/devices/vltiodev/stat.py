
from pydevmgr_core import  NodeAlias, Defaults, NodeVar, nodealias
from pydevmgr_vlt.base import VltDevice
from pydevmgr_vlt.devices.vltiodev.ctrl import COMMAND
from pydantic import create_model 

from enum import Enum
Base = VltDevice.Stat

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 
#                      _              _   
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ 
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __|
# | (_| (_) | | | \__ \ || (_| | | | | |_ 
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|
# 

N_AI, N_DI, N_NI, N_TI  = [8]*4 



class STATUS(int, Enum):
    OK = 0
    ERROR = 1




    #  ____  _        _     ___       _             __                 
    # / ___|| |_ __ _| |_  |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  
    # \___ \| __/ _` | __|  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \ 
    #  ___) | || (_| | |_   | || | | | ||  __/ |  |  _| (_| | (_|  __/ 
    # |____/ \__\__,_|\__| |___|_| |_|\__\___|_|  |_|  \__,_|\___\___| 


# some dinamicaly created nodes
io_nodes = {}
for i in range(N_DI):
    io_nodes[f'di_{i}'] = (ND, NC(suffix= f'stat.arr_DI[{i}].bValue', vtype=bool))
for i in range(N_AI):
    io_nodes[f'ai_{i}'] = (ND, NC(suffix= f'stat.arr_AI[{i}].lrValue', vtype=float))
for i in range(N_NI):
    io_nodes[f'ni_{i}'] = (ND, NC(suffix= f'stat.arr_NI[{i}].nValue', vtype=int))
for i in range(N_TI):
    io_nodes[f'ti_{i}'] = (ND, NC(suffix= f'stat.arr_TI[{i}].sValue', vtype=str))



class VltIoDevStat(Base):
    STATUS = STATUS
    # Add the constants to this class 
    class Config( create_model("Config",  __base__ = Base.Config, **io_nodes)):
        initialised: ND = NC( suffix= 'stat.bInitialised', vtype=bool )
        last_command: ND = NC( suffix= 'stat.nLastCommand', vtype=int )
        error_code: ND = NC( suffix= 'stat.nErrorCode', vtype=int )
        error_text: ND = NC( suffix= 'stat.sErrorText', vtype=str)
        status: ND = NC( suffix= 'stat.nStatus', vtype=(STATUS, STATUS.OK), output_parser=STATUS)
    
    @nodealias( *[f'di_{i}' for i in range(N_DI) ] )
    def di_all(self, *flags)->tuple:
        return flags
    @nodealias( *[f'ai_{i}' for i in range(N_AI)] )
    def ai_all(self, *values)->tuple:
        return values
    @nodealias( *[f'ni_{i}' for i in range(N_NI)] )
    def ni_all(self, *values)->tuple:
        return values
    @nodealias( *[f'ti_{i}' for i in range(N_TI)] )
    def ti_all(self, *values)->tuple:
        return values

       

if __name__ == "__main__":
    VltIoDevStat( )
