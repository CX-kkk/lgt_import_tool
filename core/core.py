# -*- coding: utf-8 -*-
"""
module author: Jojo <jolievfx@gmail.com>
"""
import maya.cmds as cmds
import pymel.core as pm


def get_current_scene_file():
    return cmds.file(q=True, sn=True)


def load_plug_in(load_list):
    plug_dict = {}
    for plug in load_list:
        plug_dict[plug] = pm.pluginInfo(plug, q=True, loaded=True)
    for key in plug_dict:
        if not plug_dict[key]:
            pm.loadPlugin(key)
