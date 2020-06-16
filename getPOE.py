'''
This script gives a quick way to see the POE situation on a Cisco switch

Espescially helpful for figuring out what model is needed for 
an add or replace i.e. a PoE capable switch or not

run it like the following.  It takes the IP (or hostname if switch is in DNS) of the switch as a command line argument:

python getPOE.py 10.21.1.151

It will print a summary of the ports using POE and a count of how many ports are using POE
'''

import pprint
import sys
import paramiko
import getpass
import time

def runCommand(ip, user, pword):

    #set up the SSH connection using Paramiko
    sshTarget = paramiko.SSHClient()
    sshTarget.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshTarget.connect(ip, username=user, password=pword)
    shell = sshTarget.invoke_shell()
    
    #disables more prompt to get all results at once and eats all shell output before what we want
    shell.send('terminal length 0\n') 
    time.sleep(.5)
    shell.recv(65535)
    
    #this command produces output list and description of all ports that are currently using PoE
    shell.send('show power inline | include on\n')
    time.sleep(.5)
    output = shell.recv(65535)
    
    #we are done with this switch now, so terminate connection
    sshTarget.close()
    
    return output

def printResults(output):

    #get output as list of lines
    output = output.decode("utf-8")
    output = output.split('\n')
    
    #last line will be the prompt, whcih contains the hostname and a #, which we will remove
    hostname = output[len(output) - 1].strip('#')
    
    #we do not want to count the first and last lines in the list, they are the entered command and the prompt
    del output[len(output) -1]
    del output[0]
    
    #now the only lines in output are the lines describing a port using PoE, print for info
    pprint.pprint(output)
    
    #print number of ports using POE and the hostname for clarity
    print('\nThere are ' + str(len(output)) + ' active ports currently using PoE on ' + hostname)

def main():
    
    if len(sys.argv) != 2:  # check number of command line args
        print('usage: python getPOE.py [IP address of switch]')
        sys.exit(1)
  
    ip = sys.argv[1]
    
    print('Enter your SSH username:')
    username = input()
    
    password = getpass.getpass('Enter your SSH password:\n')
    
    printResults(runCommand(ip, username, password))
    
main()