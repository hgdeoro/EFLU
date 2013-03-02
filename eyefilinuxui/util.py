'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''
import uuid
import pika
import json
import pprint

from pika.exceptions import AMQPConnectionError


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


def _send_amqp_msg(msg, queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange=queue_name, type='fanout')
    channel.basic_publish(exchange=queue_name, routing_key='', body=json.dumps(msg))
    connection.close()


def generic_target(conn, _logger, amqp_queue_name, action_map):
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
        channel.start_consuming()
    except AMQPConnectionError:
        if closing_connection[0]:
            _logger.info("Ignoring AMQPConnectionError")
        else:
            raise
