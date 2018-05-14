# -*- coding: utf-8 -*-
"""
module author: Jojo <jolievfx@gmail.com>
"""
import glob
import json

from hz.naming_api import NamingAPI


def get_match_path(file_path, task=None):
    naming = NamingAPI.parser(file_path)
    naming.version = '*'
    current_task = naming.parser(file_path).task
    naming.task = task if task else current_task
    match_path = naming.get_publish_full_path()
    return match_path


def get_all_published_versions(file_path, task=None):
    """
    Get all publish version from task
    :param str file_path: path
    :param str task: task which want to get all versions
    :return:
    """
    match_path = get_match_path(file_path, task)
    version_list = []
    naming = NamingAPI.parser(file_path)
    for path in glob.glob(match_path):
        version = naming.parser(path).version
        if version not in version_list:
            version_list.append(version)
    return version_list


def get_certain_version(file_path, version, task):
    """

    :param str file_path:
    :param str version: eg:001
    :return:
    """
    naming = NamingAPI.parser(file_path)
    naming.version = version
    naming.task = task
    match_path = naming.get_publish_full_path()
    return match_path

def read_in_json(file_path):
    with open(file_path, "r") as load_f:
        new_dict = json.load(load_f)
    return new_dict