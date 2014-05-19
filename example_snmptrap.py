# Example using the AFCollectorAPI for generating AppFirst Incident Reports from SNMP Traps.
# In your snmptrapd.conf file, map traps to execute the script in this file.  For example, to 
# route all traps here: 
# 
# traphandle default python /etc/snmp/snmptrap.py (correct the path, of course).  
#
# Make sure AFCollectorAPI.py is available.  You can get it from github:
#   https://github.com/appfirst/Incident-Reporting
#
# Incident reports can be viewed with the "browse" feature at appfirst.com.  Locate the server running the 
# collector, and choose the process 'snmptrapd'.  Then pull down 'select resources' and check 'Critical Incident
# Reports'.  Click on a point on the graph that shows an incident, and the text of the incident will appear in 
# the table below.
#
# You can also configure an alert on incident reports, either by count, or by keyword (such as 'CRITICAL').

import sys
import os
import time
import logging
from AFCollectorAPI import CollectorAPIHandler

def pid_from_name(name):
  n = name.replace(name[0], "[%s]" % name[0])  # the square brackets keep grep from finding itself
  cmd = "ps xa | grep %s" % n
  for line in os.popen(cmd):
    fields = line.split()
    pid = fields[0]
    return pid

lines = []
for line in sys.stdin:
    lines.append(line)
capi =  CollectorAPIHandler()
capi.verbosity = False
capi.pid_override = pid_from_name("snmptrapd") 
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
capi.setFormatter(formatter)
logger = logging.getLogger("SNMP-TRAP")
logger.setLevel(logging.DEBUG)
logger.addHandler(capi)
msg = lines[0]+lines[3]  # in this example, we use the first and third lines.  
logger.critical(msg)
