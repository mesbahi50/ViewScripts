"""

Rahul Vishnoi
Period 5
Version 2.0
Connect.py

This program is able to automatically connect to the view edge server thing
and it starts running the most recent log in the server. The program asks for
the date to make the searching process faster. If there is no log file for the
date that is passed then the program breaks and tells the user that there is
no logs for that date.

"""
import os
import paramiko
import time
from paramiko_expect import SSHClientInteraction


# Takes care of the pinging
class PingIt():
    def __init__(self,name):
        self.hostname = name
    def runIt(self):
        response = os.system("ping -c 1 " + self.hostname)
        if response == 0:
            return True
        else:
            print("Can not connect to Server; check network")
            return False

# This class opens the ssh connection to the server
class BuildSsh():
    #Consturctor
    def __init__(self,host,user,pas,timeStop):
        self.host = host
        self.user = user
        self.password = pas
        self.ssh = paramiko.SSHClient()
        self.globalT = 0.0
        self.timeToStop = timeStop

    # Opens the Ssh and saves it to the self.ssh object
    def openIt(self):
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host,22,self.user,self.password)


    # gets everything in the directory
    def getComps(self, dir):
        cmd = "cd "+dir+";ls -la"
        stdin,stdout,stderr = self.ssh.exec_command(cmd)
        values = stdout.readlines()
        for val in values:
            print(val)
        return values

    def process_tail(self,line_prefix, current_line):
        file = "TestLog.txt"
        with open(file,"a") as file_object:
            file_object.write(current_line)
            file_object.close()
        return current_line

    def timer(self, something):
        time.sleep(float(1/100))
        if self.globalT > self.timeToStop:
            return True
        else:
            self.globalT = self.globalT+1
            return False

    # after a log is selected this method starts tailing it
    def stalkLog(self,log,dir,timeToStop):
        cmd = "cd "+dir+";tail -f "+log
        interact = SSHClientInteraction(self.ssh, timeout=10, display=False)
        interact.send(cmd)
        #def tail(self, line_prefix=None, callback=None,
        #         output_callback=None, stop_callback=lambda x: False,
        #         timeout=None):
        interact.tail(None,self.process_tail,None,self.timer)




#This class is in charge of finding out what log to open
class StringManip():
    def __init__(self):
        self.options = []
        self.numDate = []


    def findDates(self,logs,day):
        count = 0
        for log in logs:
            if day in log:
                lg = log[log.find("ve"):]
                self.options.append(lg)
                count += 1
            else:
                pass
        if count == 0:
            return False
        else:
            return True

    def pickOption(self):
        self.options = sorted(self.options, reverse = True)
        for date in self.options:
            print(date)
        return self.options[0]





date = input("what is the month and day(Example - Jun/24): ")
date = date[0:date.find("/"):] + " "+ date[date.find("/")+1:]
timeToTail = input("how long(in minutes) would you like to tail the log file? ")
timeToTail = float(timeToTail)
timeToTail = timeToTail * 7 * 60 + 2*timeToTail

# can be modified for the change of the directorys
direct = "go/src/github.com/viewsenseai/viewedge-services"
repeat = 0
while repeat < 5:
    pg = PingIt("10.50.80.104")# the host that the program will ssh to
    connected = pg.runIt()
    if connected is True:
        repeat = 200
        #BuildSsh(host,username,password)
        ssh_use = BuildSsh("10.50.80.104","msedge","msedge", timeToTail)
        ssh_use.openIt()
        value = ssh_use.getComps(direct)
        sm = StringManip()
        possiblity = sm.findDates(value,date)
        if possiblity is True:
            log_to_run = sm.pickOption()
            #stalkLog(the log file, directory)
            ssh_use.stalkLog(log_to_run, direct,timeToTail)
        else:
            print("There is no logs for that date")
    else:
        repeat += 1
