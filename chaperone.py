'''
The Chaperone watches out for given Process and quits it. Build for XDLSM errors.
CSchuermann 2017
'''

import subprocess
import os
from time import sleep
from datetime import datetime as dt

def chaperone(process_window_name_list):
    print 'Chaperone watches out for the bad Girl \"{}\"'.format(' and'.join(process_window_name_list))
    counter = 0
    while True:
            tkl = subprocess.check_output("tasklist /v")
            for process_window_name in process_window_name_list:
                if process_window_name in tkl:
                    sleep(0.5)
                    print 'encountered {} {}'.format(process_window_name, dt.now())
                    os.popen('taskkill /F /FI \"WINDOWTITLE eq {}\"'.format(process_window_name))
                    sleep(1)
                else:
                    print '\r Chaperone always sleeps with one eye open: {}{}'.format('z'*counter,' '*(5-counter)),
                    sleep(5)
                    if counter >= 5:
                        counter = 0
                    else:
                        counter +=1
                    pass
                
if __name__ == "__main__":
    chaperone(['Exception:C:\\XD2006_542\\BIN\\XDLSM.EXE','Exception:C:\\XD2006_542\\BIN\\XDFFT.EXE'])