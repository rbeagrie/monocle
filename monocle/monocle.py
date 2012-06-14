#!/usr/bin/env python
import os
import sys
import copy
import webbrowser
import threading
from monocle.settings import MONOCLE_IP, MONOCLE_PORT

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monocle.settings")

    from django.core.management.commands.runserver import BaseRunserverCommand
    url = '%s:%s' %(MONOCLE_IP, MONOCLE_PORT) 
    print url
    args = copy.copy(sys.argv)
    args.extend(['runserver',url])
    print args
    rs = BaseRunserverCommand()
    t = threading.Thread(target=rs.run_from_argv,args=[args])
    t.start()
    #execute_from_command_line(args)
    wb = threading.Timer(3.0, webbrowser.open,args=['http://'+url+'/genes'])
    wb.start()
