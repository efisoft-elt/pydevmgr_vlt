

import pytest 
from pydevmgr_vlt import VltIoDev

def test_custom_channel():

    class MySensor(VltIoDev):
        class Config(VltIoDev.Config):
            
            temp = VltIoDev.AiChannel.Config( channel_number = 3)
            interlock = VltIoDev.DiChannel.Config( channel_number = 3)
            switch = VltIoDev.DoChannel.Config( channel_number = 3)
            intensity = VltIoDev.AoChannel.Config( channel_number = 3)

    my_sensor = MySensor()
    assert list(my_sensor.temp.nodes())[0] == my_sensor.stat.ai_3
    assert list(my_sensor.interlock.nodes())[0] == my_sensor.stat.di_3
    assert list(my_sensor.switch.nodes())[0] == my_sensor.ctrl.do_3
    assert list(my_sensor.intensity.nodes())[0]  == my_sensor.ctrl.ao_3

