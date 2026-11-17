#!/usr/bin/env python3
"""Single canonical CLI for ESP32-CAM-MB current parametric CAD.

The older build_v00N.py files remain historical and are not imported by this
active CAD package. Millimeters throughout. No physical fit qualification.
"""
import argparse
from pathlib import Path
from frame_monitor.export import build
from frame_monitor.validate import validate
from frame_monitor.render import render

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description='ESP32-CAM-MB parametric build')
    parser.add_argument('task',choices=('build','validate','render','all'),
                        default='all',nargs='?')
    task=parser.parse_args().task
    if task in ('build','all'):build(ROOT)
    if task in ('validate','all'):validate(ROOT)
    if task in ('render','all'):render(ROOT)
    print('V010 task complete:',task)


if __name__=='__main__':
    main()
