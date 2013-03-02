'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import logging
import os

from multiprocessing import Process

from eyefiserver import runEyeFi

logger = logging.getLogger(__name__)

QUEUE_NAME = 'eflu.eyefiserver2'

CONFIG_FILE = '/tmp/.eyefiserver2.conf'

STATE = {
    'running': False,
    'parent_conn': None,
    'process': None,
}


def eyefiserver2_gen_config(mac_0, upload_key_0, upload_dir, upload_uid=None, upload_gid=None):
    """Creates the configuration file"""
    template_filename = os.path.join(os.path.dirname(__file__), 'templates/eyefiserver2.conf.template')
    with open(template_filename, 'r') as t:
        template = t.read()

    # FIXME: sets permissions!
    config_contents = template % {
        'mac_0': mac_0,
        'upload_key_0': upload_key_0,
        'upload_dir': upload_dir,
        'upload_uid': upload_uid if upload_uid is not None else os.getuid(),
        'upload_gid': upload_gid if upload_gid is not None else os.getgid(),
    }

    with open(CONFIG_FILE, 'w') as config_file:
        config_file.write(config_contents)
    return CONFIG_FILE


def _generate_test_config():
    """Call `hostapd_gen_config()` with some valid values to generate a config file for testing"""
    return eyefiserver2_gen_config('12:12:12:12:12:12', '00000000000000000000000000000000', '/tmp')


# FIXME: lock
def start_eyefiserver2(config_filename):
    process = Process(target=runEyeFi, args=[CONFIG_FILE])
    logging.info("Starting process EyeFiServer2")
    process.start()
    STATE['process'] = process
    STATE['running'] = True


# FIXME: lock
def stop_eyefiserver2():
    logging.info("Stopping process EyeFiServer2")
    STATE['process'].terminate()
    STATE['running'] = False
