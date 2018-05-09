# -*- coding: utf-8 -*-
"""
module author: Jojo <jolievfx@gmail.com>
"""
import pprint
import os
import glob

import pymel.core as pm
from hz.naming_api import NamingAPI


def get_all_published_versions(file_path, task=None):
    """
    Get all publish version from task
    :param str file_path: path
    :param str task: task which want to get all versions
    :return:
    """
    naming = NamingAPI.parser(file_path)
    naming.version = '*'
    current_task = naming.parser(file_path).task
    naming.task = task if task else current_task
    match_path = naming.get_publish_full_path()
    version_list = []
    for path in glob.glob(match_path):
        # print path
        version = naming.parser(path).version
        if version not in version_list:
            version_list.append(version)
    return version_list


