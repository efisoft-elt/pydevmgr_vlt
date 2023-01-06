from pydevmgr_vlt.base import VltDevice, register
from pydevmgr_core import  NodeVar
from pydevmgr_ua import UaInt32
from valueparser import BaseParser
from enum import Enum 
from pydevmgr_vlt.devices.vltmotor.init_seq import INITSEQ

Base = VltDevice.Cfg

N = Base.Node # Base Node
NC = N.Config
NV = NodeVar # used in Data 

to_int32 = UaInt32().parse


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
    return to_int32(axis_type)

# a parser class for axis type
@register
class AxisType(BaseParser):
    @staticmethod
    def __parse__(value, config):
        return axis_type(value)   




class VltMotorCfg(Base):
    AXIS_TYPE = AXIS_TYPE
    INITSEQ = INITSEQ
    class Config(Base.Config):
        scale_factor:       NC  =  NC(  suffix=  'cfg.lrScaleFactor'                )
        accel:              NC  =  NC(  suffix=  'cfg.lrAccel'                      )
        decel:              NC  =  NC(  suffix=  'cfg.lrDecel'                      )
        jerk:               NC  =  NC(  suffix=  'cfg.lrJerk'                       )
        backlash:           NC  =  NC(  suffix=  'cfg.lrBacklash'                   )
        velocity:           NC  =  NC(  suffix=  'cfg.lrDefaultVelocity'            )
        max_pos:            NC  =  NC(  suffix=  'cfg.lrMaxPosition'                )
        min_pos:            NC  =  NC(  suffix=  'cfg.lrMinPosition'                )
        tolerence:          NC  =  NC(  suffix=  'cfg.lrTolerance'                  )
        tolerence_enc:      NC  =  NC(  suffix=  'cfg.lrToleranceEnc'               )
        axis_type:          NC  =  NC(  suffix=  'cfg.nTypeAxis',                   parser=  'AxisType'  )
        tout_init:          NC  =  NC(  suffix=  'cfg.tTimeoutInit',                parser=  'UaInt32'   )
        tout_move:          NC  =  NC(  suffix=  'cfg.tTimeoutMove',                parser=  'UaInt32'   )
        tout_switch:        NC  =  NC(  suffix=  'cfg.tTimeoutSwitch',              parser=  'UaInt32'   )
        brake:              NC  =  NC(  suffix=  'cfg.bUseBrake'                    )
        low_brake:          NC  =  NC(  suffix=  'cfg.bActiveLowBrake'              )
        active_low_lstop:   NC  =  NC(  suffix=  'cfg.bArrActiveLow[0].bActiveLow'  )
        active_low_lhw:     NC  =  NC(  suffix=  'cfg.bArrActiveLow[1].bActiveLow'  )
        active_low_ref:     NC  =  NC(  suffix=  'cfg.bArrActiveLow[2].bActiveLow'  )
        active_low_index:   NC  =  NC(  suffix=  'cfg.bArrActiveLow[3].bActiveLow'  )
        active_low_uhw:     NC  =  NC(  suffix=  'cfg.bArrActiveLow[4].bActiveLow'  )
        active_low_ustop:   NC  =  NC(  suffix=  'cfg.bArrActiveLow[5].bActiveLow'  )
        init_seq1_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[1].nAction',    parser=  'UaInt32'   )
        init_seq1_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[1].lrValue1'    )
        init_seq1_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[1].lrValue2'    )
        init_seq2_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[2].nAction',    parser=  'UaInt32'   )
        init_seq2_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[2].lrValue1'    )
        init_seq2_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[2].lrValue2'    )
        init_seq3_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[3].nAction',    parser=  'UaInt32'   )
        init_seq3_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[3].lrValue1'    )
        init_seq3_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[3].lrValue2'    )
        init_seq4_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[4].nAction',    parser=  'UaInt32'   )
        init_seq4_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[4].lrValue1'    )
        init_seq4_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[4].lrValue2'    )
        init_seq5_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[5].nAction',    parser=  'UaInt32'   )
        init_seq5_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[5].lrValue1'    )
        init_seq5_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[5].lrValue2'    )
        init_seq6_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[6].nAction',    parser=  'UaInt32'   )
        init_seq6_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[6].lrValue1'    )
        init_seq6_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[6].lrValue2'    )
        init_seq7_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[7].nAction',    parser=  'UaInt32'   )
        init_seq7_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[7].lrValue1'    )
        init_seq7_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[7].lrValue2'    )
        init_seq8_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[8].nAction',    parser=  'UaInt32'   )
        init_seq8_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[8].lrValue1'    )
        init_seq8_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[8].lrValue2'    )
        init_seq9_action:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[9].nAction',    parser=  'UaInt32'   )
        init_seq9_value1:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[9].lrValue1'    )
        init_seq9_value2:   NC  =  NC(  suffix=  'cfg.strArrInitSeq[9].lrValue2'    )
        init_seq10_action:  NC  =  NC(  suffix=  'cfg.strArrInitSeq[10].nAction',   parser=  'UaInt32'   )
        init_seq10_value1:  NC  =  NC(  suffix=  'cfg.strArrInitSeq[10].lrValue1'   )
        init_seq10_value2:  NC  =  NC(  suffix=  'cfg.strArrInitSeq[10].lrValue2'   )

    class Data(Base.Data):

        scale_factor:       NV[float]  =  1.0
        accel:              NV[float]  =  30.0
        decel:              NV[float]  =  30.0
        jerk:               NV[float]  =  100.0
        brake:              NV[bool]   =  False
        backlash:           NV[float]  =  0.0
        axis_type:          NV[int]    =  0
        velocity:           NV[float]  =  0.0
        max_pos:            NV[float]  =  0.0
        min_pos:            NV[float]  =  0.0
        tolerence:          NV[float]  =  1.0
        tolerence_enc:      NV[int]    =  100
        tout_init:          NV[int]    =  0
        tout_move:          NV[int]    =  0
        tout_switch:        NV[int]    =  0
        low_brake:          NV[bool]   =  False
        active_low_lstop:   NV[bool]   =  False
        active_low_lhw:     NV[bool]   =  False
        active_low_ref:     NV[bool]   =  False
        active_low_index:   NV[bool]   =  False
        active_low_uhw:     NV[bool]   =  False
        active_low_ustop:   NV[bool]   =  False
        init_seq1_action:   NV[int]    =  0
        init_seq1_value1:   NV[float]  =  0.0
        init_seq1_value2:   NV[float]  =  0.0
        init_seq2_action:   NV[int]    =  0
        init_seq2_value1:   NV[float]  =  0.0
        init_seq2_value2:   NV[float]  =  0.0
        init_seq3_action:   NV[int]    =  0
        init_seq3_value1:   NV[float]  =  0.0
        init_seq3_value2:   NV[float]  =  0.0
        init_seq4_action:   NV[int]    =  0
        init_seq4_value1:   NV[float]  =  0.0
        init_seq4_value2:   NV[float]  =  0.0
        init_seq5_action:   NV[int]    =  0
        init_seq5_value1:   NV[float]  =  0.0
        init_seq5_value2:   NV[float]  =  0.0
        init_seq6_action:   NV[int]    =  0
        init_seq6_value1:   NV[float]  =  0.0
        init_seq6_value2:   NV[float]  =  0.0
        init_seq7_action:   NV[int]    =  0
        init_seq7_value1:   NV[float]  =  0.0
        init_seq7_value2:   NV[float]  =  0.0
        init_seq8_action:   NV[int]    =  0
        init_seq8_value1:   NV[float]  =  0.0
        init_seq8_value2:   NV[float]  =  0.0
        init_seq9_action:   NV[int]    =  0
        init_seq9_value1:   NV[float]  =  0.0
        init_seq9_value2:   NV[float]  =  0.0
        init_seq10_action:  NV[int]    =  0
        init_seq10_value1:  NV[float]  =  0.0
        init_seq10_value2:  NV[float]  =  0.0

