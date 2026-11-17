"""Fail if edge-finishing BREP results are invalid or source update was lost."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from frame_monitor.geometry import first_arm,second_arm
from frame_monitor.parts import thumbwheel,camera_bezel,base_plate
from frame_monitor.wrist import adapter,shell
for name,fn in [('arm1',first_arm),('arm2',second_arm),
                ('knob',thumbwheel),('bezel',camera_bezel),
                ('mount',base_plate),('wrist',adapter),('shell',shell)]:
    shape=fn()
    assert shape.isValid() and len(shape.Solids())==1,name
    print('PASS finished',name,round(shape.Volume(),2))
assert first_arm().Volume()>4476,'first arm internal rounds missing'
assert second_arm().Volume()>8108,'second arm internal rounds missing'
assert thumbwheel().Volume()<2250,'knob bevels missing'
assert shell().Volume()<17420,'shell exterior fillets missing'
