'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

MSG_START = 'start'
MSG_QUIT = 'quit'


def _send_msg(state, msg):
    """Sends a message to the child process"""
    assert state['running']
    assert state['parent_conn']
    assert state['process']
    state['parent_conn'].send(msg)
