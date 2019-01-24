from subprocess import Popen, PIPE 

def getRss():
    p = Popen("ps -ef -o pid -o rss -o size -o vsize -o sz -o comm | grep neo-cli | awk \'{print $2}\'", shell=True, stdout=PIPE)
    state = p.returncode
    output = p.communicate()[0]
    output = output.decode('utf-8')
    if state != 0:
        return -1
    if output == '':
        return -1
    return int(output)
