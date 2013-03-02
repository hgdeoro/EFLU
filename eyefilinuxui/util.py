'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''
import uuid

MSG_START = 'start'
MSG_GET_PID = 'get_pid'
MSG_QUIT = 'quit'


def _send_msg(state, msg):
    """Sends a message to the child process"""
    # FIXME: shouldn't poll() to check if there are old messages awaiting to be read?
    msg_uuid = str(uuid.uuid4())
    assert state['running']
    assert state['parent_conn']
    assert state['process']
    msg = dict(msg)
    msg.update({'_uuid': msg_uuid})
    state['parent_conn'].send(msg)
    return msg_uuid


def _recv_msg(state, msg_uuid=None):
    """Receive a message"""
    assert state['running']
    assert state['parent_conn']
    assert state['process']

    msg = state['parent_conn'].recv()
    if msg_uuid is not None and '_uuid' in msg:
        assert msg_uuid == msg['_uuid']

    return msg
