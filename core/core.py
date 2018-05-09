# -*- coding: utf-8 -*-
"""
module author: Jojo <jolievfx@gmail.com>
"""
import maya.cmds as cmds

def get_current_scene_file():
    return cmds.file(q=True, sn=True)
