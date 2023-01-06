from pydevmgr_core import  NodeAlias1, Defaults, NodeVar
from pydevmgr_vlt.base import VltDevice
from pydevmgr_vlt.devices._tools import _inc

from enum import Enum
Base = VltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 


class VltioDevCfg(Base):
    pass

