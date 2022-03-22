
from pydevmgr_vlt.vltmotor import StatInterface
from .vltdevice import VltDevice
from pydevmgr_core import BaseParser, record_class, upload, NodeAlias, NodeVar
from pydevmgr_ua import Int32
from enum import Enum 
from typing import Union, List, Dict, Iterable


N_AI, N_DI, N_NI, N_TI  = [8]*4 
N_AO, N_DO, N_NO, N_TO  = [8]*4

class STATUS(int, Enum):
    OK = 0
    ERROR = 1



class COMMAND(int, Enum):
    NONE = 0
    INITIALISE = 1
    ACTIVATE = 2

@record_class
class IoDevCommand(BaseParser):
    class Config(BaseParser.Config):
        type = "IoDevCommand"
    @staticmethod
    def parse(value, config):
        if isinstance(value, str):
            value =  getattr(COMMAND, value)
        return Int32(value)

NP = VltDevice.Node.prop





class VltIoDevStatInterface(VltDevice.StatInterface):
    class Config(VltDevice.StatInterface.Config):
        type = "VltIoDevStatInterface"
    
    initialised = NP('initialised', suffix= 'stat.bInitialised' )
    last_command = NP('last_command', suffix= 'stat.nLastCommand' )
    error_code = NP('error_code', suffix= 'stat.nErrorCode' )
    error_text = NP('error_text', suffix= 'stat.sErrorText' )
    status = NP('status', suffix= 'stat.nStatus' )   
    # Other Nodes arre added bellow 
    
    @NodeAlias.prop( 'di_all', [f'di_{i}' for i in range(N_DI) ] )
    def di_all(self, *flags):
        return flags
    @NodeAlias.prop( 'ai_all', [f'ai_{i}' for i in range(N_AI)] )
    def ai_all(self, *values):
        return values
    @NodeAlias.prop( 'ni_all', [f'ni_{i}' for i in range(N_NI)] )
    def ni_all(self, *values):
        return values
    @NodeAlias.prop( 'ti_all', [f'ti_{i}' for i in range(N_TI)] )
    def ti_all(self, *values):
        return values

    class Data(VltDevice.StatInterface.Data):
        initialised : NodeVar[bool] = False
        last_command: NodeVar[COMMAND] = COMMAND.NONE
        error_code: NodeVar[int] = 0 
        error_text: NodeVar[str] = ""
        status: NodeVar[STATUS] = STATUS.OK
        di_all: NodeVar[list] = []
        ai_all: NodeVar[list] = []
        ni_all: NodeVar[list] = []
        ti_all: NodeVar[list] = []


# ADD all the DI, NI, etc nodes 
for i in range(N_DI):
    setattr( VltIoDevStatInterface, f'di_{i}', NP(f'di_{i}', suffix= f'stat.arr_DI[{i}].bValue') )
for i in range(N_AI):
    setattr( VltIoDevStatInterface, f'ai_{i}', NP(f'ai_{i}', suffix= f'stat.arr_AI[{i}].lrValue') )
for i in range(N_NI):
    setattr( VltIoDevStatInterface, f'ni_{i}', NP(f'ni_{i}', suffix= f'stat.arr_NI[{i}].nValue') )
for i in range(N_TI):
    setattr( VltIoDevStatInterface, f'ti_{i}', NP(f'ti_{i}', suffix= f'stat.arr_TI[{i}].sValue') )

    

class VltIoDevCtrlInterface(VltDevice.CtrlInterface):
    class Config(VltDevice.CtrlInterface.Config):
        type = "VltIoDevCtrlInterface"

    execute = NP('execute', suffix= 'ctrl.bExecute', parser= 'bool' )
    command = NP('command', suffix= 'ctrl.nCommand', parser= 'IoDevCommand' )
    

# ADD all the DI, NI, etc nodes 
for i in range(N_DO):
    setattr( VltIoDevCtrlInterface, f'do_{i}', NP(f'do_{i}', suffix= f'ctrl.arr_DO[{i}].bValue') )
for i in range(N_AO):
    setattr( VltIoDevCtrlInterface, f'ao_{i}', NP(f'ao_{i}', suffix= f'ctrl.arr_AO[{i}].lrValue') )
for i in range(N_NO):
    setattr( VltIoDevCtrlInterface, f'no_{i}', NP(f'no_{i}', suffix= f'ctrl.arr_NO[{i}].nValue') )
for i in range(N_TO):
    setattr( VltIoDevCtrlInterface, f'to_{i}', NP(f'to_{i}', suffix= f'ctrl.arr_TO[{i}].sValue') )

del NP


# __     ___ _   ___      ____             
# \ \   / / | |_|_ _|___ |  _ \  _____   __
#  \ \ / /| | __|| |/ _ \| | | |/ _ \ \ / /
#   \ V / | | |_ | | (_) | |_| |  __/\ V / 
#    \_/  |_|\__|___\___/|____/ \___| \_/  
                                         


@record_class
class VltIoDev(VltDevice):
    COMMAND = COMMAND
    StatInterface =  VltIoDevStatInterface
    CtrlInterface = VltIoDevCtrlInterface

    stat = StatInterface.prop("stat")
    ctrl = CtrlInterface.prop("ctrl")
    
    class Config(VltDevice.Config):
        type = "VltIoDev"
    
    class Data(VltDevice.Data):
        StatData = StatInterface.Data
        stat: StatData = StatData()


    def init(self):
        """ init the iodev  """
        upload({
            self.ctrl.execute: True, 
            self.ctrl.command: self.COMMAND.INITIALISE
            })
        return self.stat.initialised
    
    def set_do(self, flags: Union[List[bool], Dict[int,bool]]):
        """ set digital output flags 
        
        Args:
            flags (list, or dict): list of bool or a dictionary of digital output index (starting from 0) and flag pair
             
        Exemple::

            io.set_do( [False]*8 ) # set all to zero 
            io.set_do( [True, False] ) # set do_0 and do_1 to True and False respectively (others are unchaged)
            io.set_do( {3:True, 4:True} ) # set do_4 and do_4 to True (others are unchanged)
        """
        if not isinstance(flags, dict):
            it = enumerate(flags)
        else:
            it = flags.items()

        ctrl = self.ctrl 
        n_f = { ctrl.get_node( "do_{}".format(i) ):f for i,f in it }
        
        n_f.update( {ctrl.execute:True, ctrl.command :self.COMMAND.ACTIVATE} )
        upload(n_f)
    
    def set_ao(self, values: Union[List[bool], Dict[int,bool]]):
        """ set degital output values 
        
        Args:
            flags (list, or dict): list of float or a dictionary of analog output index (starting from 0) and value  pair
             
        Exemple::

            io.set_ao( [0.0]*8 ) # set all to zero 
            io.set_ao( [32, 64] ) # set do_0 and do_1 to 32 and 64 respectively (others are unchaged)
            io.set_ao( {3:128, 4:128} ) # set do_4 and do_4 to 128 (others are unchanged)
        """

        if not isinstance(values, dict):
            it = enumerate(values)
        else:
            it = values.items()

        ctrl = self.ctrl 
        n_f = { ctrl.get_node( "do_{}".format(i) ):f for i,f in it }
        
        n_f.update( {ctrl.execute:True, ctrl.command :self.COMMAND.ACTIVATE} )
        upload(n_f)
    

    def get_do_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ self.ctrl.nodes[f'do_{n}'] for n in num]
        else:
            return self.ctrl.nodes[f'do_{num}']

    def get_ao_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ self.ctrl.nodes[f'ao_{n}'] for n in num]
        else:
            return self.ctrl.nodes[f'ao_{num}']

    def get_ai_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ self.stat.nodes[f'ai_{n}'] for n in num]
        else:
            return self.stat.nodes[f'ai_{num}']
     
    def get_di_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ self.stat.nodes[f'di_{n}'] for n in num]
        else:
            return self.stat.nodes[f'di_{num}']


        
            

