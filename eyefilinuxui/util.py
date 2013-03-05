'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import json
import logging
import pika
import pprint
import subprocess
import uuid

from multiprocessing import Process, Pipe
from collections import OrderedDict
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)


EVENT_QUEUE_NAME = 'eflu.events'

MSG_START = 'start'
MSG_GET_PID = 'get_pid'
MSG_QUIT = 'quit'


#===============================================================================
# IPC messages
#===============================================================================

# FIXME: rename '_send_msg()' to '_send_ipc_msg()'
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


# FIXME: rename '_recv_msg()' to '_recv_ipc_msg()'
def _recv_msg(state, msg_uuid=None):
    """Receive a message"""
    assert state['running']
    assert state['parent_conn']
    assert state['process']

    msg = state['parent_conn'].recv()
    if msg_uuid is not None and '_uuid' in msg:
        assert msg_uuid == msg['_uuid']

    return msg


#===============================================================================
# RabbitMQ messages
#===============================================================================

def _send_amqp_msg(msg, queue_name):
    assert isinstance(msg, dict)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=queue_name, type='fanout')
    channel.basic_publish(exchange=queue_name, routing_key='', body=json.dumps(msg))
    connection.close()


def create_event(origin, event_type, extra={}):
    """Creates a low-level event"""
    assert isinstance(extra, dict)
    return {
        'origin': origin, # ORIGIN of the event
        'type': event_type, # TYPE of event
        'extra': extra.copy(), # dict with EXTRA information
    }


def send_event(origin, event_type, extra={}):
    """Low-level method to create and send an event"""
    return _send_amqp_msg(create_event(origin, event_type, extra), EVENT_QUEUE_NAME)


SERVICE_STATUS_UP = 'UP'
SERVICE_STATUS_DOWN = 'DOWN'

SERVICE_NAME_RABBITMQ = 'service_rabbitmq'
SERVICE_NAME_EYEFISERVER2 = 'service_eyefiserver2'


def event_is_service_status(msg):
    """Returns True if 'msg' is about the status of a service"""
    assert isinstance(msg, dict)
    return msg['type'] == 'service_status'


def create_service_status_event(service_name, new_status):
    """
    Creates a 'service status' event, to signal a change in the status
    of the service.
    """
    return create_event(service_name, 'service_status', {'new_status': new_status})


#===============================================================================
# MultiProcessing targets
#===============================================================================

def generic_target(conn, _logger, amqp_queue_name, start_args, action_map):
    _logger.info("Waiting for message...")

    process = []
    closing_connection = [False]

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=amqp_queue_name, type='fanout')
    result = channel.queue_declare(exclusive=True)
    _queue_name = result.method.queue
    channel.queue_bind(exchange=amqp_queue_name, queue=_queue_name)

    def callback(ch, method, properties, msg):
        msg = json.loads(msg)
        _logger.info("Message received: %s", pprint.pformat(msg))

        if msg['action'] in action_map:
            func = action_map[msg['action']]
            assert callable(func)
            func()
            return

        if msg['action'] == MSG_QUIT:
            closing_connection[0] = True
            if process:
                _logger.warn("A process exists: %s", process[0])
            # FIXME: stop process if exists?
            while process:
                process.pop()
            connection.close()
            return

        if msg['action'] == MSG_GET_PID:
            response = {}
            if '_uuid' in msg:
                response['_uuid'] = msg['_uuid']
            response['pid'] = None
            if process[0]:
                response['pid'] = process[0].pid

            # data es sent over 'connection' (Pipe)
            conn.send(response)
            return

        if msg['action'] == MSG_START:
            if process:
                # FIXME: raise error? stop old process? warn and continue?
                _logger.warn("A process exists: %s. It will be overriden", process[0])
                while process:
                    process.pop()
            _logger.info("Will Popen with args: %s", pprint.pformat(start_args))
            process.append(subprocess.Popen(start_args, close_fds=True, cwd='/'))
            _logger.info("Popen returded process %s", process[0])
            return

        # FIXME: remove this, implement or comment this
        if msg['action'] == "CHECK_CHILD":
            if process:
                # ret_code = process.wait()
                process[0].poll()
                if process[0].returncode is not None:
                    _logger.info("Cleaning up finished Popen process. Exit status: %s", process[0].returncode)
                    if process[0].returncode != 0:
                        _logger.warn("Exit status != 0")
                    process[0].wait()
                    while process:
                        process.pop()
                else:
                    _logger.debug("Popen process %s is running", process[0])
            return

        if msg['action'] in action_map:
            func = action_map[msg['action']]
            func(msg, process)
            return

        _logger.error("UNKNOWN MESSAGE: %s", pprint.pformat(msg))

    channel.basic_consume(callback, queue=_queue_name, no_ack=True)
    conn.send("ACK")
    try:
        logging.info("Starting channel.start_consuming()...")
        channel.start_consuming()
        logging.info("channel.start_consuming() finished...")
    except AMQPConnectionError:
        if closing_connection[0]:
            _logger.info("Ignoring AMQPConnectionError")
        else:
            raise


def generic_start_multiprocess(start_args, action_map, _logger, queue_name, state):
    parent_conn, child_conn = Pipe()
    process = Process(target=generic_target, args=(
        child_conn,
        _logger,
        queue_name,
        start_args,
        action_map
    ))
    _logger.info("Launching child...")
    process.start()

    _logger.info("Waiting for ACK")
    parent_conn.recv()
    _logger.info("ACK received...")

    state['running'] = True
    state['parent_conn'] = parent_conn
    state['process'] = process

    _send_amqp_msg({'action': MSG_START}, queue_name)


def generic_mp_stop(_logger, queue_name, state):
    _logger.info("Stopping...")
    _send_amqp_msg({'action': MSG_QUIT}, queue_name)
    state['running'] = False
    _logger.info("Waiting for process.join() on pid %s...", state['process'].pid)
    state['process'].terminate()
    state['process'].join()
    _logger.info("Process exit status: %s", state['process'].exitcode)


def generic_mp_get_pid(_logger, queue_name, state):
    """Returns the PID, or None if not running"""
    msg_uuid = str(uuid.uuid4())
    _send_amqp_msg({'_uuid': msg_uuid, 'action': MSG_GET_PID}, queue_name)

    msg = _recv_msg(state, msg_uuid=msg_uuid)
    return msg['pid']


#===============================================================================
# Exif
#===============================================================================

# get_tags_to_show() returns the tags in the order defined here
EXIF_TAGS = OrderedDict((
    ('EXIF ISOSpeedRatings', 'ISO'),
    ('EXIF FNumber', 'Aperture'),
    ('EXIF ExposureTime', 'Exposure'),
    ('EXIF Flash', 'Flash'),
    ('EXIF DateTimeDigitized', 'Date'),
))


def get_tags_to_show(tags):
    """Returns a dict with exif information to show"""
    to_show = OrderedDict()
    for tag_name in EXIF_TAGS.keys():
        to_show[EXIF_TAGS[tag_name]] = tags.get(tag_name, '-')
    return to_show


def get_exif_tags(image_filename):
    """Returns a dict with exif information"""
    try:
        import EXIF
        with open(image_filename, 'rb') as image_file:
            return dict(EXIF.process_file(image_file))
    except:
        logger.exception("Couldn't load exif tags... will return empty dict")
        return {}


def how_much_rotate(tags):
    """
    Returns how many degrees the image should be rotated.
    Returns `None` if no information is in `tags` or an error ocurs.
    """
    #    In [21]: y = x['Image Orientation']
    #    In [22]: EXIF.EXIF_TAGS[y.tag]
    #    Out[22]:
    #    ('Orientation',
    #     {1: 'Horizontal (normal)',
    #      2: 'Mirrored horizontal',
    #      3: 'Rotated 180',
    #      4: 'Mirrored vertical',
    #      5: 'Mirrored horizontal then rotated 90 CCW',
    #      6: 'Rotated 90 CW',
    #      7: 'Mirrored horizontal then rotated 90 CW',
    #      8: 'Rotated 90 CCW'})

    if not 'Image Orientation' in tags:
        return None

    image_orientation = tags['Image Orientation'].values[0]
    if image_orientation == 1:
        return 0
    elif image_orientation == 3:
        return 180
    elif image_orientation == 6:
        return 90
    elif image_orientation == 8:
        return -90
    else:
        logger.warn("Unknown 'Image Orientation' value: %s", image_orientation)
        return None
