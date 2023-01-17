from pydevmgr_core.base.dataclass import set_data_model
from pydevmgr_vlt.base import VltDevice
from pydevmgr_core import Defaults, NodeVar,  nodealias
from pydevmgr_core.nodes import Opposite
from enum import Enum 
from typing import Optional 
from pydevmgr_vlt.devices.vltmotor.positions import PositionsConfig

Base = VltDevice.Stat

N = Base.Node # Base Node
NC = N.Config
ND = Defaults[NC] # this typing var says that it is a Node object holding default values 
NV = NodeVar # used in Data 




class STATE(int, Enum):
    IDLE = 20
    RESET_AXIS = 30
    SET_POS = 40
    INIT = 50
    SAVE_TO_NOVRAM = 55
    CLEAR_NOVRAM = 57
    MOVE_ABS = 60
    MOVE_OPTIMISED = 61
    MOVE_VEL = 70
    CTRL_BRAKE = 75
    STOP = 80



@set_data_model
class VltMotorStat(Base):
    STATE = STATE 
    class Config(Base.Config):
        mot_positions:          PositionsConfig  =  PositionsConfig()
        state:                  ND               =  NC(suffix='nState',                     vtype=int    )
        pos_target:             ND               =  NC(suffix='stat.lrPosTarget',           vtype=float  )
        pos_actual:             ND               =  NC(suffix='stat.lrPosActual',           vtype=float  )
        vel_actual:             ND               =  NC(suffix='stat.lrVelActual',           vtype=float  )
        vel_target:             ND               =  NC(suffix='stat.lrVelTarget',           vtype=float  )
        axis_status:            ND               =  NC(suffix='stat.nAxisStatus',           vtype=int    )
        backlash_step:          ND               =  NC(suffix='stat.nBacklashStep',         vtype=int    )
        last_command:           ND               =  NC(suffix='stat.nLastCommand',          vtype=int    )
        error_code:             ND               =  NC(suffix='stat.nErrorCode',            vtype=int    )
        error_text:             ND               =  NC(suffix='stat.sErrorText',            vtype=str    )
        init_step:              ND               =  NC(suffix='stat.nInitStep',             vtype=int    )
        init_action:            ND               =  NC(suffix='stat.nInitAction',           vtype=int    )
        info_data1:             ND               =  NC(suffix='stat.nInfoData1',            vtype=int    )
        info_data2:             ND               =  NC(suffix='stat.nInfoData2',            vtype=int    )
        local:                  ND               =  NC(suffix='stat.bLocal',                vtype=bool   )
        enabled:                ND               =  NC(suffix='stat.bEnabled',              vtype=bool   )
        initialised:            ND               =  NC(suffix='stat.bInitialised',          vtype=bool   )
        ref_switch:             ND               =  NC(suffix='stat.bRefSwitch',            vtype=bool   )
        at_max_position:        ND               =  NC(suffix='stat.bAtMaxPosition',        vtype=bool   )
        at_min_position:        ND               =  NC(suffix='stat.bAtMinPosition',        vtype=bool   )
        limit_switch_positive:  ND               =  NC(suffix='stat.bLimitSwitchPositive',  vtype=bool   )
        limit_switch_negative:  ND               =  NC(suffix='stat.bLimitSwitchNegative',  vtype=bool   )
        brake_active:           ND               =  NC(suffix='stat.bBrakeActive',          vtype=bool   )
        max_position:           ND               =  NC(suffix='stat.lrMaxPositionValue',    vtype=float  )
        min_position:           ND               =  NC(suffix='stat.lrMinPositionValue',    vtype=float  )
        mode:                   ND               =  NC(suffix='stat.nMode',                 vtype=int    )
        axis_ready:             ND               =  NC(suffix='stat.bAxisReady',            vtype=bool   )
        moving_abs:             ND               =  NC(suffix='stat.bMovingAbs',            vtype=bool   )
        moving_vel:             ND               =  NC(suffix='stat.bMovingVel',            vtype=bool   )
        changing_vel:           ND               =  NC(suffix='stat.bChangingVel',          vtype=bool   )
        

    @nodealias("error_code", "error_text")
    def check(self, erc, ert)->bool:
        """ This node always return True but raise an error in case of device in error """
        if erc:
            raise RuntimeError(f"Error {erc}: {ert}")
        return True

    @nodealias("state")
    def state_txt(self, state)->str:
        return self.STATE(state).name 

    @nodealias("state", "check")
    def movement_finished(self, state, c)->bool:
        return state not in [self.STATE.MOVE_ABS, self.STATE.MOVE_OPTIMISED, self.STATE.MOVE_VEL, self.STATE.INIT]

    @nodealias( "initialised", "check")
    def initialisation_finished(self, initialised, c)->bool:
        return initialised

    @nodealias( "enabled", "check")
    def enable_finished(self, enabled, c) ->bool:
        return enabled
    
    not_initialised = Opposite.Config(node="initialised", vtype=bool)

    @nodealias("pos_actual")
    def pos_name(self, pos_actual)->str:
        if not self.config.mot_positions: return ''
        positions = self.config.mot_positions
        tol = positions.tolerance
        for pname, pos in positions.positions.items():
            if abs( pos-pos_actual)<tol:
                return pname
        return ''

        
    # we need the mot_position from te parent (a Motor Device)
    # just add it to the dictionary create by  the super
    @classmethod
    def new(cls, parent, name, config):
        new = super().new(parent, name, config)

        try:
            mot_positions = parent.config.positions
        except AttributeError:
            mot_positions = {}
        new.config.mot_positions = mot_positions
        return new


if __name__ == "__main__":
    VltMotorStat().mot_positions 

