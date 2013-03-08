# coding=utf-8

#----------------------------------------------------------------------
# Copyright (c) 2013 Horacio G. de Oro <hgdeoro@gmail.com>
#----------------------------------------------------------------------
#    This file is part of EFLU.
#
#    EFLU is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    EFLU is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with EFLU.  If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------

import os
import sys

from eyefilinuxui.util import send_event, create_upload_event


def main():
    print "Sending event for file {0}".format(sys.argv[1])
    assert os.path.exists(sys.argv[1])
    assert os.path.isfile(sys.argv[1])
    send_event(create_upload_event('cli', sys.argv[1]))


if __name__ == '__main__':
    main()
