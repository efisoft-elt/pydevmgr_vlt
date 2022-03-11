from .vltdevice import VltDevice
from pydevmgr_core import record_class, BaseParser , upload,  NodeAlias, NodeAlias1, NodeVar
from ._tools import _inc, NegNode
from pydevmgr_ua import Int32, Int16
from pydantic import BaseModel , validator, root_validator
from typing import List, Dict, Any, Optional, Union 
from enum import Enum
from collections import OrderedDict



class VltMotorCtrlConfig(BaseModel):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    velocity : float = 0.1 # mendatory because used as default for movement
    min_pos :           Optional[float] = 0.0
    max_pos :           Optional[float] = 0.0 
    axis_type :         Union[None,int,str] = "LINEAR" # LINEAR , CIRCULAR, CIRCULAR_OPTIMISED
    active_low_lstop :  Optional[bool] = False
    active_low_lhw :    Optional[bool] = False
    active_low_ref :    Optional[bool] = True
    active_low_index :  Optional[bool] = False
    active_low_uhw :    Optional[bool] = True
    active_low_ustop :  Optional[bool] = False
    brake :             Optional[bool] = False
    low_brake :         Optional[bool] = False
    backlash :          Optional[float] = 0.0
    tout_init :         Optional[int] = 30000
    tout_move :         Optional[int] = 12000
    tout_switch :       Optional[int] = 10000
    
    scale_factor : Optional[float] = 1.0
    accel: Optional[float] = 30.0
    decel: Optional[float] = 30.0
    jerk:  Optional[float] = 100.0
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    @validator('axis_type')
    def validate_axis_type(cls, ax):
        if isinstance(ax, str):
            try:
                getattr(AXIS_TYPE, ax)
            except AttributeError:
                raise ValueError(f"Unknown axis_type {ax!r}")
        if isinstance(ax, int):            
            # always return a string??
            ax = AXIS_TYPE(ax).name        
        return ax

    
class PositionsConfig(BaseModel):
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    posnames : List = []
    tolerance: float = 1.0
    positions: Dict = OrderedDict()  # adding a dictionary for positions. Presfered than leaving it as extra 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:        
        extra = 'allow' # needed for the poses 
        validate_assignment = True
    @root_validator()
    def collect_positions(cls, values):     
        """ collectect the positions from the extras """ 
        positions = values['positions']
        for name in values['posnames']:
            if name not in positions:
                try:
                    positions[name] = float( values[name] ) 
                except (KeyError, TypeError):
                    raise ValueError(f'posname {name!r} is not defined or not a float')   
        return values 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        d = {'posnames': self.posnames, 'tolerance':self.tolerance}
        for p in self.posnames:
            d[p] = self.positions[p]
        return d


# ################################  
class SeqStepConfig(BaseModel):
    """ Data  Model for step configuration """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    index: int =  0    
    value1: float = 0.0
    value2: float = 0.0
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:                
        validate_assignment = True
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        return self.dict(exclude={"index"})


class InitialisationConfig(BaseModel):
    """ Config Model for the initialisation sequence """
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    sequence : List[str] = []
    END          : SeqStepConfig = SeqStepConfig(index=0)
    FIND_INDEX   : SeqStepConfig = SeqStepConfig(index=1)
    FIND_REF_LE  : SeqStepConfig = SeqStepConfig(index=2)
    FIND_REF_UE  : SeqStepConfig = SeqStepConfig(index=3)
    FIND_LHW     : SeqStepConfig = SeqStepConfig(index=4)
    FIND_UHW     : SeqStepConfig = SeqStepConfig(index=5)  
    DELAY        : SeqStepConfig = SeqStepConfig(index=6)
    MOVE_ABS     : SeqStepConfig = SeqStepConfig(index=7)
    MOVE_REL     : SeqStepConfig = SeqStepConfig(index=8)
    CALIB_ABS    : SeqStepConfig = SeqStepConfig(index=9)
    CALIB_REL    : SeqStepConfig = SeqStepConfig(index=10)
    CALIB_SWITCH : SeqStepConfig = SeqStepConfig(index=11)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~
    class Config:                
        validate_assignment = True        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Validator Functions
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @validator('END', 'FIND_INDEX', 'FIND_REF_LE', 'FIND_REF_UE', 'FIND_LHW', 'FIND_UHW', 
               'DELAY', 'MOVE_ABS', 'MOVE_REL', 'CALIB_ABS', 'CALIB_REL' , 'CALIB_SWITCH')
    def force_index(cls, v, field):
        """ need to write the index """        
        v.index = getattr(INITSEQ, field.name)
        return v

    @validator('sequence')
    def validate_initialisation(cls,sequence):   
        """ Validate the list of sequence """ 
        for s in sequence:
            try:
                cls.__fields__[s]
            except KeyError:
                raise ValueError(f'unknown sequence step named {s!r}')
        return sequence
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self):
        d = {'sequence':self.sequence}
        for seq in self.sequence:
            d[seq] = getattr(self, seq).cfgdict()            
        return d
# ################################

class VltMotorConfig(VltDevice.Config):
    CtrlConfig = VltMotorCtrlConfig
    PositionsConfig = PositionsConfig
    InitialisationConfig = InitialisationConfig
    

    type = "VltMotor"
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Data Structure 
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    type: str = "Motor"
    initialisation : InitialisationConfig = InitialisationConfig()
    positions      : PositionsConfig = PositionsConfig()
    ctrl_config    : CtrlConfig = CtrlConfig()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Method to save back the configuration     
    def cfgdict(self, exclude=set()):
        
        d = super().cfgdict(exclude=exclude)
        for a in ('initialisation', 'positions'):
            if a not in exclude:
                d[a] = getattr(self, a).cfgdict()   
        return d






##### ############
# Sequence
class INITSEQ(int, Enum):
    END = 0
    FIND_INDEX = 1
    FIND_REF_LE = 2
    FIND_REF_UE = 3
    FIND_LHW = 4
    FIND_UHW = 5

    DELAY = 6
    MOVE_ABS = 7
    MOVE_REL = 8
    CALIB_ABS = 9
    CALIB_REL = 10
    CALIB_SWITCH = 11

for E,v1,v2 in [
    ( INITSEQ.END,  "", "" ),
    ( INITSEQ.FIND_INDEX, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_REF_LE, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_REF_UE, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_LHW, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.FIND_UHW, "Fast Vel", "Slow Vel" ),
    ( INITSEQ.DELAY, "Delay [ms]", "" ),
    ( INITSEQ.MOVE_ABS, "Vel", "Pos" ),
    ( INITSEQ.MOVE_REL, "Vel", "Pos" ),
    ( INITSEQ.CALIB_ABS, "Pos", "" ),
    ( INITSEQ.CALIB_REL, "Pos", "" ),
    ( INITSEQ.CALIB_SWITCH, "Pos", "" ),
]:
    setattr(E, "var1", v1)
    setattr(E, "var2", v2)
del E,v1,v2



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

@record_class
class MotorCommand(BaseParser):
    class Config(BaseParser.Config):
        type = "MotorCommand"
    @staticmethod
    def parse(value, config):
        if isinstance(value, str):
            value =  getattr(MOTOR_COMMAND, value)
        return Int32(value)

class DIRECTION(int, Enum):
    POSITIVE = _inc(1)
    SHORTEST = _inc()
    NEGATIVE = _inc()
    CURRENT  = _inc()

@record_class
class Direction(BaseParser):
    class Config(BaseParser.Config):
        type = "Direction"
    @staticmethod
    def parse(value, config):
        if isinstance(value, str):
            value =  getattr(DIRECTION, value)
        return Int16(value)




class AXIS_TYPE(int, Enum):
    LINEAR = 1
    CIRCULAR =2
    CIRCULAR_OPTIMISED = 3



def axis_type(axis_type):
    """ return always a axis_type int number from a number or a string
    
    Raise a ValueError if the input string does not match axis type
    Example:
        axis_type('LINEAR') == 1
        axis_type(1) == 1
    """
    if isinstance(axis_type, str):
        try:
            axis_type = getattr(AXIS_TYPE, axis_type) 
        except AttributeError:
            raise ValueError(f'Unknown AXIS type {axis_type!r}')
    return Int32(axis_type)

# a parser class for axis type
@record_class
class AxisType(BaseParser):
    class Config(BaseParser.Config):
        type: str = "AxisType"
    @staticmethod
    def parse(value, config):
        return axis_type(value)   





# 
#   __                  _   _                 
#  / _|_   _ _ __   ___| |_(_) ___  _ __  ___ 
# | |_| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# |  _| |_| | | | | (__| |_| | (_) | | | \__ \
# |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
# 

def init_sequence_to_cfg(initialisation, INITSEQ=INITSEQ):
    """ from a config initialisation dict return a dictionary of key/value for .cfg interface """            
    
    
    # set the init sequence    
    cfg_dict = {} 
    
    init_dict = initialisation.dict(exclude_none=True, exclude_unset=True)
    if not "sequence" in init_dict:        
        return cfg_dict
    
    # reset all sequence variable
    for i in range(1,11):
        cfg_dict["init_seq{}_action".format(i)] = INITSEQ.END.value
        cfg_dict["init_seq{}_value1".format(i)] = 0.0
        cfg_dict["init_seq{}_value2".format(i)] = 0.0
        
    for stepnum, step_name in enumerate(initialisation.sequence, start=1):
        step = getattr(initialisation, step_name)
        cfg_dict["init_seq%d_action"%stepnum] = step.index
        cfg_dict["init_seq%d_value1"%stepnum] = step.value1
        cfg_dict["init_seq%d_value2"%stepnum] = step.value2    
    return cfg_dict


#  ___       _             __                     
# |_ _|_ __ | |_ ___ _ __ / _| __ _  ___ ___  ___ 
#  | || '_ \| __/ _ \ '__| |_ / _` |/ __/ _ \/ __|
#  | || | | | ||  __/ |  |  _| (_| | (_|  __/\__ \
# |___|_| |_|\__\___|_|  |_|  \__,_|\___\___||___/
                                                

NP = VltDevice.Node.prop

@record_class
class StatInterface(VltDevice.StatInterface):
    STATE = STATE
    class Config(VltDevice.StatInterface.Config):
        type = "VltMotorStat"
    state = NP('state', suffix= 'nState' )
    pos_target = NP('pos_target', suffix= 'stat.lrPosTarget' )
    pos_actual = NP('pos_actual', suffix= 'stat.lrPosActual' )
    vel_actual = NP('vel_actual', suffix= 'stat.lrVelActual' )
    vel_target = NP('vel_target', suffix= 'stat.lrVelTarget' )
    axis_status = NP('axis_status', suffix= 'stat.nAxisStatus' )
    backlash_step = NP('backlash_step', suffix= 'stat.nBacklashStep' )
    last_command = NP('last_command', suffix= 'stat.nLastCommand' )
    error_code = NP('error_code', suffix= 'stat.nErrorCode' )
    error_text = NP('error_text', suffix= 'stat.sErrorText' )
    init_step = NP('init_step', suffix= 'stat.nInitStep' )
    init_action = NP('init_action', suffix= 'stat.nInitAction' )
    info_data1 = NP('info_data1', suffix= 'stat.nInfoData1' )
    info_data2 = NP('info_data2', suffix= 'stat.nInfoData2' )
    local = NP('local', suffix= 'stat.bLocal' )
    enabled = NP('enabled', suffix= 'stat.bEnabled' )
    initialised = NP('initialised', suffix= 'stat.bInitialised' )
    ref_switch = NP('ref_switch', suffix= 'stat.bRefSwitch' )
    at_max_position = NP('at_max_position', suffix= 'stat.bAtMaxPosition' )
    at_min_position = NP('at_min_position', suffix= 'stat.bAtMinPosition' )
    limit_switch_positive = NP('limit_switch_positive', suffix= 'stat.bLimitSwitchPositive' )
    limit_switch_negative = NP('limit_switch_negative', suffix= 'stat.bLimitSwitchNegative' )
    brake_active = NP('brake_active', suffix= 'stat.bBrakeActive' )
    max_position = NP('max_position', suffix= 'stat.lrMaxPositionValue' )
    min_position = NP('min_position', suffix= 'stat.lrMinPositionValue' )
    mode = NP('mode', suffix= 'stat.nMode' )
    axis_ready = NP('axis_ready', suffix= 'stat.bAxisReady' )
    moving_abs = NP('moving_abs', suffix= 'stat.bMovingAbs' )
    moving_vel = NP('moving_vel', suffix= 'stat.bMovingVel' )
    changing_vel = NP('changing_vel', suffix= 'stat.bChangingVel' )
    


    @NodeAlias.prop("check", nodes=["error_code", "error_text"])
    def check(self, erc, ert):
        """ This node always return True but raise an error in case of device in error """
        if erc:
            raise RuntimeError(f"Error {erc}: {ert}")
        return True

    @NodeAlias1.prop("state_txt", node="state")
    def state_txt(self, state):
        return self.STATE(state).name 

    @NodeAlias.prop("movement_finished", nodes=["state", "check"])
    def movement_finished(self, state, c):
        return state not in [STATE.MOVE_ABS, STATE.MOVE_OPTIMISED, STATE.MOVE_VEL, STATE.INIT]

    @NodeAlias.prop("initialisation_finished", nodes=["initialised", "check"])
    def initialisation_finished(self, initialised, c):
        return initialised

    @NodeAlias.prop("enable_finished", nodes=["enabled", "check"])
    def enable_finished(self, enabled, c):
        return enabled
    
    _mot_positions = None# will be overwriten by Motor 
    @NodeAlias1.prop("pos_name", node="pos_actual")
    def pos_name(self, pos_actual):
        if not self._mot_positions: return ''
        positions = self._mot_positions
        tol = positions.tolerance
        for pname, pos in positions.positions.items():
            if abs( pos-pos_actual)<tol:
                return pname
        return ''
   
    
    
    not_initialised = NegNode.prop("not_initialised", node="initialised")

    class Data(VltDevice.StatInterface.Data):
        state :NodeVar[int] = 0 
        pos_target : NodeVar[float] = 0.0 
        pos_actual : NodeVar[float] = 0.0 
        vel_actual : NodeVar[float] = 0.0 
        vel_target : NodeVar[float] = 0.0 
        axis_status :NodeVar[int] = 0 
        backlash_step :NodeVar[int] = 0
        last_command : NodeVar[int] = 0
        error_code: NodeVar[int] = 0
        error_text: NodeVar[str] = ""
        init_step: NodeVar[int] = 0
        init_action : NodeVar[int] = 0
        info_data1  : NodeVar[int] = 0
        info_data2  : NodeVar[int] = 0
        local : NodeVar[bool] = False
        enabled  : NodeVar[bool] = False
        initialised  : NodeVar[bool] = False
        ref_switch  : NodeVar[bool] = False
        at_max_position  : NodeVar[bool] = False
        at_min_position  : NodeVar[bool] = False
        limit_switch_positive  : NodeVar[bool] = False
        limit_switch_negative  : NodeVar[bool] = False
        brake_active  : NodeVar[bool] = False
        max_position  : NodeVar[float] = 0.0 
        min_position  : NodeVar[float] = 0.0 
        mode  : NodeVar[int] = 0
        axis_ready  : NodeVar[bool] = False
        moving_abs  : NodeVar[bool] = False
        moving_vel  : NodeVar[bool] = False
        changing_vel  : NodeVar[bool] = False
        

       



@record_class
class CfgInterface(VltDevice.CfgInterface):
    class Config(VltDevice.CfgInterface.Config):
        type = "VltMotorCfg"
    scale_factor = NP('scale_factor', suffix= 'cfg.lrScaleFactor' )
    accel = NP('accel', suffix= 'cfg.lrAccel' )
    decel = NP('decel', suffix= 'cfg.lrDecel' )
    jerk = NP('jerk', suffix= 'cfg.lrJerk' )
    backlash = NP('backlash', suffix= 'cfg.lrBacklash' )
    velocity = NP('velocity', suffix= 'cfg.lrDefaultVelocity' )
    max_pos = NP('max_pos', suffix= 'cfg.lrMaxPosition' )
    min_pos = NP('min_pos', suffix= 'cfg.lrMinPosition' )
    tolerence = NP('tolerence', suffix= 'cfg.lrTolerance' )
    tolerence_enc = NP('tolerence_enc', suffix= 'cfg.lrToleranceEnc' )
    axis_type = NP('axis_type', suffix= 'cfg.nTypeAxis', parser= 'AxisType' )
    tout_init = NP('tout_init', suffix= 'cfg.tTimeoutInit', parser= 'UaInt32' )
    tout_move = NP('tout_move', suffix= 'cfg.tTimeoutMove', parser= 'UaInt32' )
    tout_switch = NP('tout_switch', suffix= 'cfg.tTimeoutSwitch', parser= 'UaInt32' )
    brake = NP('brake', suffix= 'cfg.bUseBrake' )
    low_brake = NP('low_brake', suffix= 'cfg.bActiveLowBrake' )
    active_low_lstop = NP('active_low_lstop', suffix= 'cfg.bArrActiveLow[0].bActiveLow' )
    active_low_lhw = NP('active_low_lhw', suffix= 'cfg.bArrActiveLow[1].bActiveLow' )
    active_low_ref = NP('active_low_ref', suffix= 'cfg.bArrActiveLow[2].bActiveLow' )
    active_low_index = NP('active_low_index', suffix= 'cfg.bArrActiveLow[3].bActiveLow' )
    active_low_uhw = NP('active_low_uhw', suffix= 'cfg.bArrActiveLow[4].bActiveLow' )
    active_low_ustop = NP('active_low_ustop',   suffix= 'cfg.bArrActiveLow[5].bActiveLow' )
    init_seq1_action = NP('init_seq1_action',   suffix= 'cfg.strArrInitSeq[1].nAction', parser= 'UaInt32' )
    init_seq1_value1 = NP('init_seq1_value1',   suffix= 'cfg.strArrInitSeq[1].lrValue1' )
    init_seq1_value2 = NP('init_seq1_value2',   suffix= 'cfg.strArrInitSeq[1].lrValue2' )
    init_seq2_action = NP('init_seq2_action',   suffix= 'cfg.strArrInitSeq[2].nAction', parser= 'UaInt32' )
    init_seq2_value1 = NP('init_seq2_value1',   suffix= 'cfg.strArrInitSeq[2].lrValue1' )
    init_seq2_value2 = NP('init_seq2_value2',   suffix= 'cfg.strArrInitSeq[2].lrValue2' )
    init_seq3_action = NP('init_seq3_action',   suffix= 'cfg.strArrInitSeq[3].nAction', parser= 'UaInt32' )
    init_seq3_value1 = NP('init_seq3_value1',   suffix= 'cfg.strArrInitSeq[3].lrValue1' )
    init_seq3_value2 = NP('init_seq3_value2',   suffix= 'cfg.strArrInitSeq[3].lrValue2' )
    init_seq4_action = NP('init_seq4_action',   suffix= 'cfg.strArrInitSeq[4].nAction', parser= 'UaInt32' )
    init_seq4_value1 = NP('init_seq4_value1',   suffix= 'cfg.strArrInitSeq[4].lrValue1' )
    init_seq4_value2 = NP('init_seq4_value2',   suffix= 'cfg.strArrInitSeq[4].lrValue2' )
    init_seq5_action = NP('init_seq5_action',   suffix= 'cfg.strArrInitSeq[5].nAction', parser= 'UaInt32' )
    init_seq5_value1 = NP('init_seq5_value1',   suffix= 'cfg.strArrInitSeq[5].lrValue1' )
    init_seq5_value2 = NP('init_seq5_value2',   suffix= 'cfg.strArrInitSeq[5].lrValue2' )
    init_seq6_action = NP('init_seq6_action',   suffix= 'cfg.strArrInitSeq[6].nAction', parser= 'UaInt32' )
    init_seq6_value1 = NP('init_seq6_value1',   suffix= 'cfg.strArrInitSeq[6].lrValue1' )
    init_seq6_value2 = NP('init_seq6_value2',   suffix= 'cfg.strArrInitSeq[6].lrValue2' )
    init_seq7_action = NP('init_seq7_action',   suffix= 'cfg.strArrInitSeq[7].nAction', parser= 'UaInt32' )
    init_seq7_value1 = NP('init_seq7_value1',   suffix= 'cfg.strArrInitSeq[7].lrValue1' )
    init_seq7_value2 = NP('init_seq7_value2',   suffix= 'cfg.strArrInitSeq[7].lrValue2' )
    init_seq8_action = NP('init_seq8_action',   suffix= 'cfg.strArrInitSeq[8].nAction', parser= 'UaInt32' )
    init_seq8_value1 = NP('init_seq8_value1',   suffix= 'cfg.strArrInitSeq[8].lrValue1' )
    init_seq8_value2 = NP('init_seq8_value2',   suffix= 'cfg.strArrInitSeq[8].lrValue2' )
    init_seq9_action = NP('init_seq9_action',   suffix= 'cfg.strArrInitSeq[9].nAction', parser= 'UaInt32' )
    init_seq9_value1 = NP('init_seq9_value1',   suffix= 'cfg.strArrInitSeq[9].lrValue1' )
    init_seq9_value2 = NP('init_seq9_value2',   suffix= 'cfg.strArrInitSeq[9].lrValue2' )
    init_seq10_action = NP('init_seq10_action', suffix= 'cfg.strArrInitSeq[10].nAction', parser= 'UaInt32' )
    init_seq10_value1 = NP('init_seq10_value1', suffix= 'cfg.strArrInitSeq[10].lrValue1' )
    init_seq10_value2 = NP('init_seq10_value2', suffix= 'cfg.strArrInitSeq[10].lrValue2' )


    class Data(VltDevice.CfgInterface.Data):

        scale_factor: NodeVar[float] = 1.0
        accel:        NodeVar[float] = 30.0
        decel :       NodeVar[float] = 30.0
        jerk :        NodeVar[float] = 100.0
        brake:            NodeVar[bool] = False    
        backlash:         NodeVar[float] = 0.0
        axis_type:        NodeVar[int] = 0 
        
        velocity:         NodeVar[float] = 0.0
        max_pos:          NodeVar[float] = 0.0      
        min_pos:          NodeVar[float] = 0.0      
        
        tolerence: NodeVar[float] = 1.0
        tolerence_enc: NodeVar[int] = 100
        
        tout_init:          NodeVar[int] = 0 
        tout_move:          NodeVar[int] = 0 
        tout_switch:        NodeVar[int] = 0 


        low_brake:          NodeVar[bool] = False 
        active_low_lstop:   NodeVar[bool] = False 
        active_low_lhw:     NodeVar[bool] = False 
        active_low_ref:     NodeVar[bool] = False 
        active_low_index:   NodeVar[bool] = False 
        active_low_uhw:     NodeVar[bool] = False 
        active_low_ustop:   NodeVar[bool] = False 

   
        init_seq1_action:  NodeVar[int] = 0
        init_seq1_value1:  NodeVar[float] = 0.0
        init_seq1_value2:  NodeVar[float] = 0.0
        
        init_seq2_action:  NodeVar[int] = 0
        init_seq2_value1:  NodeVar[float] = 0.0
        init_seq2_value2:  NodeVar[float] = 0.0
        
        init_seq3_action:  NodeVar[int] = 0
        init_seq3_value1:  NodeVar[float] = 0.0
        init_seq3_value2:  NodeVar[float] = 0.0
        
        init_seq4_action:  NodeVar[int] = 0
        init_seq4_value1:  NodeVar[float] = 0.0
        init_seq4_value2:  NodeVar[float] = 0.0
        
        init_seq5_action:  NodeVar[int] = 0
        init_seq5_value1:  NodeVar[float] = 0.0
        init_seq5_value2:  NodeVar[float] = 0.0

        init_seq6_action:  NodeVar[int] = 0
        init_seq6_value1:  NodeVar[float] = 0.0
        init_seq6_value2:  NodeVar[float] = 0.0

        init_seq7_action:  NodeVar[int] = 0
        init_seq7_value1:  NodeVar[float] = 0.0
        init_seq7_value2:  NodeVar[float] = 0.0

        init_seq8_action:  NodeVar[int] = 0
        init_seq8_value1:  NodeVar[float] = 0.0
        init_seq8_value2:  NodeVar[float] = 0.0

        init_seq9_action:  NodeVar[int] = 0
        init_seq9_value1:  NodeVar[float] = 0.0
        init_seq9_value2:  NodeVar[float] = 0.0

        init_seq10_action:  NodeVar[int] = 0
        init_seq10_value1:  NodeVar[float] = 0.0
        init_seq10_value2:  NodeVar[float] = 0.0    
        

@record_class
class CtrlInterface(VltDevice.CtrlInterface):
    class Config(VltDevice.CtrlInterface.Config):
        type = "VltMotorCtrl"
    command =   NP('command',   suffix= 'ctrl.nCommand',    parser= MotorCommand )
    direction = NP('direction', suffix= 'ctrl.nDirection',  parser= Direction )
    position = NP('position',   suffix= 'ctrl.lrPosition',  parser= 'UaDouble' )
    velocity = NP('velocity',   suffix= 'ctrl.lrVelocity',  parser= 'UaDouble' )
    stop =     NP('stop',       suffix= 'ctrl.bStop',       parser=  bool  )
    reset =    NP('reset',      suffix= 'ctrl.bResetError', parser=  bool  )
    disable =  NP('disable',    suffix= 'ctrl.bDisable',    parser=  bool  )
    enable =   NP('enable',    suffix= 'ctrl.bEnable',      parser=  bool  )
    execute =  NP('execute',   suffix= 'ctrl.bExecute',     parser=  bool  )


# __     ___ _   __  __       _             
# \ \   / / | |_|  \/  | ___ | |_ ___  _ __ 
#  \ \ / /| | __| |\/| |/ _ \| __/ _ \| '__|
#   \ V / | | |_| |  | | (_) | || (_) | |   
#    \_/  |_|\__|_|  |_|\___/ \__\___/|_|   
                                          

@record_class
class VltMotor(VltDevice):
    
    Config = VltMotorConfig

    CfgInterface = CfgInterface
    StatInterface = StatInterface
    CtrlInterface = CtrlInterface 
    
    COMMAND = MOTOR_COMMAND
    DIRECTION = DIRECTION
    INITSEQ = INITSEQ
    
    class Data(VltDevice.Data):
        StatData = StatInterface.Data
        CfgData = CfgInterface.Data

        stat: StatData = StatData()
        cfg: CfgData = CfgData()

    cfg  = CfgInterface.prop('cfg')
    ctrl = CtrlInterface.prop('ctrl')

    @StatInterface.prop('stat')    
    def stat(self, interface):
        # need to add the motor_position to the stat interface instance 
        interface._mot_positions = self.config.positions
        
    


    def get_configuration(self, exclude_unset=True,  **kwargs) -> Dict[VltDevice.Node,Any]:
        """  return a node/value pair dictionary ready to be uploaded 
        
        The node/value dictionary represent the device configuration. 
        
        Args:
            **kwargs : name/value pairs pointing to cfg.name node
                      This allow to change configuration on the fly
                      without changing the config file. 
        """
        
        config = self._config 
        
        ctrl_config = config.ctrl_config
        # just update what is in ctrl_config, this should work for motor 
        # one may need to check parse some variable more carefully       
        values = ctrl_config.dict(exclude_none=True, exclude_unset=exclude_unset)
        cfg_dict = {self.cfg.get_node(k):v for k,v in  values.items() }
        cfg_dict[self.ignored] = self.config.ignored 
        cfg_dict.update({self.cfg.get_node(k):v for k,v in  kwargs.items() })
        
        init_cfg = init_sequence_to_cfg(config.initialisation, self.INITSEQ)
        cfg_dict.update({self.cfg.get_node(k):v for k,v in init_cfg.items()})
        
        # transform axis type to number 
        if self.cfg.axis_type in cfg_dict:
            axis_type = cfg_dict[self.cfg.axis_type] 
            cfg_dict[self.cfg.axis_type] =  getattr(AXIS_TYPE, axis_type) if isinstance(axis_type, str) else axis_type
        ###
        # Set the new config value to the device 
        return cfg_dict
    
    @property
    def velocity(self) -> float:
        return self.config.ctrl_config.velocity
   

    def check(self):
        """Check if the device is in error. Raise an error in case it is True """
        return self.stat.check.get()

    def stop(self):
        self.ctrl.stop.set(True)
    
    def reset(self):
        self.ctrl.reset.set(True)
        return self.stat.not_initialised
    
    def enable(self):
        self.ctrl.enable.set(True)
        return self.stat.enable_finished
    
    def disable(self):
        self.ctrl.disable.set(True)
        return self.stat.enabled


    def init(self):
        upload({ 
            self.ctrl.execute : True, 
            self.ctrl.command : self.COMMAND.INITIALISE
            })
        return self.stat.initialisation_finished

    def move_abs(self, pos, vel=None):
        
        vel = self.velocity if vel is None else vel
        upload({
            self.ctrl.execute : True, 
            self.ctrl.position: pos, 
            self.ctrl.velocity: vel, 
            self.ctrl.command : self.COMMAND.MOVE_ABSOLUTE
            })
        return self.stat.movement_finished

    def move_rel(self, pos, vel=None):

        vel = self.velocity if vel is None else vel
        upload({
            self.ctrl.execute : True, 
            self.ctrl.position: pos, 
            self.ctrl.velocity: vel, 
            self.ctrl.command : self.COMMAND.MOVE_RELATIVE
            })
        return self.stat.movement_finished  

    def move_vel(self, vel):
        direction = self.DIRECTION.POSITIVE if vel>0 else self.DIRECTION.NEGATIVE
        vel = abs(vel)
        upload({
            self.ctrl.execute : True, 
            self.ctrl.velocity: vel, 
            self.ctrl.direction: direction, 
            self.ctrl.command: self.COMMAND.MOVE_VELOCITY
            })
        return None
    
    def get_pos_target_of_name(self, name: str) -> float:
        """return the configured target position of a given pos name or raise error"""
        try:
            position = getattr(self.config.positions, name)
        except AttributeError:
            raise ValueError('unknown posname %r'%name)
        return position

    def get_name_of_pos(self, pos_actual: float) -> str:
        """ Retrun the name of a position from a position as input or ''
        
        Example:
            m.get_name_of( m.stat.pos_actual.get() )
        """
        positions = self.config.positions    
        tol = positions.tolerance
        
        for pname, pos in positions.positions.items():
            if abs( pos-pos_actual)<tol:
                return pname
        return ''

    def move_name(self, name, vel=None) -> VltDevice.Node:
        """ move motor to a named position 
        
        Args:
           name (str): named position
           vel (float):   target velocity for the movement
        """
        absPos = self.get_pos_target_of_name(name)
        return self.move_abs(absPos, vel)
        

    def set_pos(self, pos):
        """ Set the curent position value """
        upload({
            self.ctrl.execute : True, 
            self.ctrl.position: pos, 
            self.ctrl.command : self.COMMAND.SET_POSITION
            })

