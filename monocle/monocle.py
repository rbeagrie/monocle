#!/usr/bin/env python
import os
import sys
import copy
import webbrowser
import threading
from monocle.settings import MONOCLE_IP, MONOCLE_PORT

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monocle.settings")

    from django.core.management import ManagementUtility
    url = '%s:%s' %(MONOCLE_IP, MONOCLE_PORT) 
    print url
    args = copy.copy(sys.argv)
    args.extend(['runserver',url])
    print args
    utility = ManagementUtility(args)
    t = threading.Thread(target=utility.execute)
    t.start()
    #execute_from_command_line(args)
    webbrowser.open('http://'+url+'/genes')
