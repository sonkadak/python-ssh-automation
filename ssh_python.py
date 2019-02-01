# -*- coding: utf-8 -*-
import paramiko
import time
import sys, os
from multiprocessing.dummy import Pool as ThreadPool

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
        # for prefixed command
        if len(sys.argv) > 1:
            precmd = getPrefixedcmd(sys.argv[1])
            for arg in SSH_INFO:
                sshParallel(arg[0], arg[1], arg[2], cnt, precmd)
        else:
            # just use commands in script.txt
            for arg in SSH_INFO:
                sshParallel(arg[0], arg[1], arg[2], cnt)
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
        outdata += str(chan.recv(1000))
    while chan.recv_stderr_ready():
        errdata += str(chan.recv_stderr(1000))

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

# multiprocessing
def sshParallel(host, pw, rpw, threads=1, pcmd=None):
    pool = ThreadPool(threads)
    results = pool.starmap(sshConnect, [(host, pw, rpw)])
    pool.close()
    pool.join()
    return results

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