'''
Created on Mar 2, 2013

@author: Horacio G. de Oro
'''

import sys

from eyefilinuxui.util import send_event
import os


def main():
    print "Sending event for file {0}".format(sys.argv[1])
    assert os.path.exists(sys.argv[1])
    assert os.path.isfile(sys.argv[1])
    send_event('eyefiserver', 'upload', {
        'filename': sys.argv[1],
    })


if __name__ == '__main__':
    main()
