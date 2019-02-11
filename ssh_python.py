# -*- coding: utf-8 -*-
import paramiko
import time
import sys, os
from multiprocessing import Pool, cpu_count

# character match
PW_MAP = { '1':'a', '2':'b', '3':'c', '4':'d', '5':'e', '6':'f', '7':'g', '8':'h', '9':'i', '0':'j' }
# list of information for ssh connection
SSH_INFO = []

def main():
    # code for remote HOST information
    host_ip = ''
    PW = ''
    # password for su
    RPW = ''
    SSH_INFO.append([host_ip, PW, RPW])

    cnt = len(SSH_INFO)
    if cnt:
        # get in to ssh with multiprocessing
        pool = Pool(cpu_count()-1)
        pool.starmap(sshConnect, SSH_INFO)
        pool.close()
        pool.join()
    else:
        print ('There is no host to connect !')
    
# dictionary method for additional system argument
def getPrefixedcmd(arg):
    return {
        "argument_1": "something\n",
        "argument_0": "greate\n"
    }.get(arg, "DEFAULT value is here if there is no matched in dictionary")

# Get data for print output to console
def waitStreams(chan):
    time.sleep(1)
    outdata=errdata = ""

    while chan.recv_ready():
        outdata += chan.recv(1000).decode()
    while chan.recv_stderr_ready():
        errdata += chan.recv_stderr(1000).decode()

    return outdata, errdata

# actual ssh connection
def sshConnect(host, pw, rpw):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username='cobellus', password=pw)
        time.sleep(3)
        # paramiko.SSHClient.invoke_shell for successive session
        channel = ssh.invoke_shell()
        channel.send('su -\n')
        outdata, errdata = waitStreams(channel)
        # you can check the output like putty console using "print (outdata)"
        channel.send(rpw + '\n')
        outdata, errdata = waitStreams(channel)
        print ('Login Successful: ' + host)

        # for prefixed command
        if len(sys.argv) > 1:
            precmd = getPrefixedcmd(sys.argv[1])
            execCommand(precmd, channel)
        else:
            # check script.txt file
            if os.path.getsize('script.txt') > 0:
                with open('script.txt') as cmds:
                    for cmd in cmds:
                        cmd = cmd.rstrip('\n')
                        execCommand(cmd, channel)
            else:
                print ("script.txt file is empty !")
        
    except Exception as e:
        print ('Somethings gone wrong !', e)
        # Failed IP list written here
        f = open("failed_IPs.txt", 'w')
        f.write(host+"\n")
        f.close()
        
    finally:
        if ssh is not None:
            print (host+': Job done')
            ssh.close()

# send command and loop Stream outdata is end
def execCommand(command, chn):
    chn.send(command + "\n")
    while True:
        outdata, errdata = waitStreams(chn)
        '''if outdata:
            print (outdata)'''
        if outdata.endswith("]# '"):
            break
    
if __name__ == "__main__":
    main()
