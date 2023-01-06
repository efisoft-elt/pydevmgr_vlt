from enum import Enum
from pydevmgr_vlt.devices.vltiodev.stat import VltIoDevStat as Stat
from pydevmgr_vlt.devices.vltiodev.ctrl  import VltIoDevCtrl as Ctrl

from pydevmgr_vlt.base import VltDevice, register
from pydevmgr_core import upload, BaseNodeAlias1, ParentWeakRef
from typing import Callable, Optional, Union, Iterable, Dict, List
from pydantic import BaseModel

Base = VltDevice




class VltioDevConfig(Base.Config):
    class CtrlConfig(Base.Config.CtrlConfig):
        pass
    
    Ctrl = Ctrl.Config
    Stat = Stat.Config
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure (redefine the ctrl_config)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ctrl_config : CtrlConfig= CtrlConfig()
    
    ctrl: Ctrl = Ctrl()
    stat: Stat = Stat()
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ChannelType(str, Enum):
    AI = "ai"
    DI = "di"
    AO = "ao"
    DO = "do"

@register
class VltChannel(ParentWeakRef, BaseNodeAlias1):
    class Config:
        channel_number: int = 0
        channel_type: ChannelType = ChannelType.AI
    
    def nodes(self):
        ch_type = self.channel_type.value 
        if ch_type.value.endswith("o"):
            interface = self.get_parent().ctrl
        else:
            interface = self.get_parent().stat 
        yield getattr( interface, f"{ch_type}_{self.channel_number}")
   
@register
class VltAiChannel(ParentWeakRef, BaseNodeAlias1):
    class Config:
        channel_number: int = 0
    def nodes(self):
        yield getattr( self.get_parent().stat,  f"ai_{self.channel_number}")   
        
@register
class VltDiChannel(ParentWeakRef, BaseNodeAlias1):
    class Config:
        channel_number: int = 0
    def nodes(self):
        yield getattr( self.get_parent().stat,  f"di_{self.channel_number}")   

@register
class VltAoChannel(ParentWeakRef, BaseNodeAlias1):
    class Config:
        channel_number: int = 0
    def nodes(self):
        yield getattr( self.get_parent().ctrl,  f"ao_{self.channel_number}")   
    
@register
class VltDoChannel(ParentWeakRef, BaseNodeAlias1):
    class Config:
        channel_number: int = 0
    def nodes(self):
        yield getattr( self.get_parent().ctrl,  f"do_{self.channel_number}")   


@register
class VltIoDev(Base):
    """ ELt Standard VltioDev device """
    Config = VltioDevConfig
    Ctrl = Ctrl
    Stat = Stat
    
    AiChannel = VltAiChannel 
    AoChannel = VltAoChannel 
    DiChannel = VltDiChannel 
    DoChannel = VltDoChannel 

    class Data(Base.Data):
        Ctrl = Ctrl.Data
        Stat = Stat.Data
        
        ctrl: Ctrl = Ctrl()
        stat: Stat = Stat()
    
    def init(self):
        """ init the iodev  """
        upload({
            self.ctrl.execute: True, 
            self.ctrl.command: self.ctrl.COMMAND.INITIALISE
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
        n_f = { getattr(ctrl, "do_{}".format(i)):f for i,f in it }
        
        n_f.update( {ctrl.execute:True, ctrl.command :self.ctrl.COMMAND.ACTIVATE} )
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
        n_f = { getattr(ctrl, "ao_{}".format(i)):f for i,f in it }
        
        n_f.update( {ctrl.execute:True, ctrl.command :self.ctrl.COMMAND.ACTIVATE} )
        upload(n_f)
    

    def get_do_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr( self.ctrl, f'do_{n}') for n in num]
        else:
            return getattr( self.ctrl, f'do_{num}')

    def get_ao_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr( self.ctrl, f'ao_{n}') for n in num]
        else:
            return getattr( self.ctrl, f'ao_{num}')

    def get_ai_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr(self.stat, f'ai_{n}') for n in num]
        else:
            return getattr(self.stat, f'ai_{num}')
     
    def get_di_node(self, num: Union[int,Iterable]):
        if hasattr(num, "__iter__"):
            return [ getattr( self.stat, f'di_{n}') for n in num]
        else:
            return getattr( self.stat, f'di_{num}')

if __name__ == "__main__":
    VltIoDev()
    print("OK")
