#!/usr/bin/env python3
#
# General Purpose Imports
import getopt
import sys
import time
import datetime
import re
import threading
import time
import os

# Paramiko for SSHClient()
import paramiko

# Debug purpose
import pprint

# Import for colored debug text
from termcolor import colored

version=1.3

# Defining the exception that will let us exit the thread
# when test only the connection.
# TODO: Maybe there's a better way.
class OnlyConnection(Exception):
    def __init__(self):
        super().__init__()

# 
def ssh_conn(ip, cmd, threads):
    try:
        # Instanciate the client.
        ssh = paramiko.SSHClient()
        
        # Sets SSH Client timeout and Key Policy.
        ssh.auth_timeout = ssh_timeout
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        debug( "* {}: Connecting...".format(ip ) )
        # Connecting to given ip  for this thread.
        ssh.connect(ip, port=22, username=ssh_user, password=ssh_password, look_for_keys=False, timeout=ssh_timeout)

        # If the script is launched with --connect-only here the code will raise
        # a custom exception to skip to the report creation in the 'finally' block.
        if connect_only:
            print("* {}: Testing only connection".format(ip) )
            raise OnlyConnection()

        debug("* {}: Sending command.".format(ip ) )
        # Sending command to the remote ssh server.
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()

        # Reading output in ascii for the remote host
        output = stdout.read().decode('utf-8')
        error  = stderr.read().decode('utf-8')
        
        # If the --verbose ( -v ) option is specified then print
        # out to the terminal the remote output of the command.
        if verbose:
            print ( "\n* {}: Verbose output start".format(ip) )
            # Format the output and prints it line by line.
            for line in output.split("\n"):
                if line != "":
                    print ( "STDOUT: " + line  )
            for line in error.split("\n"):
                if line != "":
                    print ( "STDERR: " + line  )
            print ( "* {}: Verbose output end.\n".format(ip) )

        debug("* {}: Closing connection".format( ip ) )
        ssh.close()

        # If the script reaches this point, the status is OK.
        status = "OK"

    except paramiko.AuthenticationException:
        print("* {}: User or password incorrect, Please try again!!!".format(ip))
        status = "ERROR"
        output = "ERROR: Authentication error."
        error = True
    except OnlyConnection as e:
        status = "OK"
        output = "Connected"
        error = False
    except Exception as e:
        print ( "* {}: {}".format(ip, str(e)) )
        status = "ERROR"
        output = "ERROR: {}".format(str(e))        
        error = True
    finally:
        # If a command is not set just set the cmd variable
        # to a string just for report purpose.
        if not cmd:
            cmd = "Connect Only"
        
        # If an output file is specified with option -o --output writes
        # the result of the thread on the report file.
        # TODO: Check for race-conditions in high-thread exections
        if o_file != False:
            outFile = open( str(o_file) + ".swarm.csv", "a")
            outFile.writelines( "{},\"{}\",\"{}\",{},{}\n".format(ip, status, cmd.strip("\n"), output.strip("\n"), datetime.datetime.today()) )
            outFile.close()
        
        debug("* Thread end {}".format(ip))
    
    return output, error

def SSH_Thread(hosts, cmd, threads):

    thread_pool_count   = 0
    thread_limit        = threads
    thread_slots        = []
    
    # While there are hosts left
    while len(hosts) > 0:

        print("* Host mancanti {}".format(len(hosts)))

        while len(thread_slots) < thread_limit:
            
            try:
                # Recupera un ip dall'array.
                ip = hosts.pop()
                
                # Avvia il thread
                trd = threading.Thread(target=ssh_conn, args=( ip.strip("\n"), cmd, thread_pool_count ))
                debug("* Appending the thread")
                
                thread_slots.append( trd )
                
                debug("* Slot used: {}".format(len(thread_slots)))
                debug("* Thread: {}".format( pprint.pformat(trd) ))
                
                trd.daemon = False
                trd.start()
                
            except Exception as e:
                debug("* EXCEPT: {}".format(str(e)))
                #debug(str(e))
                break
        
        # Una volta uscito dal while ( significa che i thread slot sono occupati )
        # allora per ognuno di essi aspetta il termine.
        debug("* Waiting threads to complete...")
        
        for thread in thread_slots:
            thread.join()
        
        debug("* Emptying thead slots...")
        
        thread_slots = []

# Legge il file specificato e ritornare un array dove ogni cella
# corrisponde ad una riga del file.
def get_ip_from_file( file ):
    temp_ip = []
    debug("*** Getting IPs form file.")
    count = 0
    line_count = 1
    with open(file, 'r') as fh:
        for line in fh.readlines():
            line = line.strip("\n")
            if not line:
                if verbose:
                    debug ("* Invalid ip at line {}".format(line_count) )
                pass
            else:
                temp_ip.append(line)
                count = count + 1 
                
            line_count = line_count + 1
                
            
        print("*** IPs extracted : {}".format(count))
        print("*** Total lines   : {}".format(line_count))

    return temp_ip

def usage():
    print ("Swarm v{}".format(version))
    print ("Usage: swarm --ips [IPS/IP_FILE] --cmd [BASH_CMD] --ssh-user [USER] --ssh-pass [PASSWORD]\n")
    print ("Required:")
    print (" -i IP\t\t--ips IP\t\tTarget IP Adresses ( Comma-separeted values or File with one ip per line).")
    print (" -c CMD\t\t--cmd CMD\t\tCommand to be executed ( Should be a valid Bash command )")
    print (" -u USER\t--ssh-user USER\t\tSSH username used for connection.")
    print (" -p PASS\t--ssh-password PASS\ttSSH password used for connection.")
    print ("\nOptional:")
    print (" -t NUM\t\t--threads NUM\tNumber of thread to run concurrently ( Default: 4 )")
    print (" -o FILE\t--output FILE\tFile where command output will be stored")
    print (" -T FILE\t--ssh-timeout NUM\tSSH Connection Timeout in seconds. ( Default: 8 )")
    print (" -x\t\t--connect-only\tOnly test the connection. ( Can perform report -o )")
    print (" -v\t\t--verbose\tShows the version of the script.")
    print (" -d\t\t--debug\t\tEnebles debug output.")
    print (" -h\t\t--help\t\tShows this help.")
    print ("\nAuthor: Luca 'misfotto' Tortora <misfotto@gmail.com>")
    print ("Github: github.com/misfotto")
    sys.exit(1)

def debug( data ):
    if is_debug:
        print (colored( data, "white", attrs=['dark'] ))

if __name__ == '__main__':
    
    # Default options
    cmd             = False
    verbose         = False
    o_file          = False
    i_file          = False
    is_debug        = False
    thread_slots    = []
    threads         = 4
    ssh_timeout     = 8
    ssh_user        = False
    ssh_password    = False
    connect_only    = False
    
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 
            "hc:i:t:o:T:u:p:xdv", 
            ["help", "cmd=", "ips=", "threads=", "output=","ssh-timeout=","ssh-user=","ssh-password=","connect-only","debug", "verbose"]
        )
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    
    
    for o, a in opts:
        if o in ("-c", "--cmd"):
            cmd = a
        elif o in ("-i", "--ips"):
            i_file = a
        elif o in ("-t", "--threads"):
            threads = int(a)
        elif o in ("-o", "--output"):
            o_file = a
        elif o in ("-T", "--ssh-timeout"):
            ssh_timeout = int(a)
        elif o in ("-u", "--ssh-user"):
            ssh_user = a
        elif o in ("-p", "--ssh-password"):
            ssh_password = a
        elif o in ("-x", "--connect-only"):
            connect_only = True
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-d", "--debug"):
            is_debug = True
        elif o in ("-h", "--help"):
            usage()
        else:
            print( "{}: unhandled option".format(o) )

    start = time.time()
    if verbose:
        print("* Time start: {}".format(print("* Time end: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))))))


    if o_file != False and not os.path.exists(str(o_file) + ".swarm.csv"):
        outFile = open( str(o_file) + ".swarm.csv", "a")
        outFile.writelines( "IP,STATUS,COMMAND,OUTPUT,DATE\n" ) 
        outFile.close()

    # Se il valore specificato per l'argomento --ips è un file allora utilizza
    # la funzione per leggere i valori riga per riga convertendoli in array.
    if i_file:
        if os.path.isfile(i_file):
            debug( "* Using {} as input file.".format(i_file) )
            ips = get_ip_from_file(i_file)
        else:
            debug( "* Using comma-separated values as input.".format(i_file) )
            ips = i_file.split(',')
    
    # Validates parameters combination.
    if ( ( not ips or not ssh_user or not ssh_password ) and ( not connect_only or not cmd) ):
        print ("* You should at least specify: --ips, --ssh-user and --ssh-password for the connection.")
        print ("* And also                   : --cmd or --connect-only for the action taken.")
        usage()
        exit( 1 )
    
    debug( "Starting SWARM {}\n".format(version) )
    debug ( "Command: '{}'".format(cmd) )
    debug ( "Threads: {}".format(threads) )
    debug ( "Verbose: {}\n".format(verbose) )
    
    SSH_Thread(hosts=ips, cmd=cmd, threads=threads)

    done = time.time()
    elapsed = done - start
    
    if verbose:
        print("* Time end: {}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(done))))
        print("* Completed in {}s".format(int(elapsed)) )

