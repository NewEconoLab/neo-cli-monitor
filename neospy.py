import sys
import os
import time
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
sys.path.append('./')
from config import config
sys.path.append('./python/')
import neoapi
from log import logging
import state

#how mand blocks behind the best block count
RESTART_THRESHOLD = config['restartthreshold']
#avoid restarting within the time after start(minute)
START_SILENT = config['startsilent']
#check interval(second)
INTERVAL = config['interval']
LOCAL_SRV = config['localsrv']

lastRestartTimestamp = datetime.fromtimestamp(0)
lastRecordLocalIndex = 0
lastRecordLocalTime = datetime.fromtimestamp(0)
restart_cnt = 0

def getBestBlockCount():
    maxHeight = -1
    for seed in config['seeds']:
        height = neoapi.getCurrentHeight('http://' + seed)
        if maxHeight < height:
            maxHeight = height
    logging.info('[getBestBlockCount] maxheight: {0}'.format(maxHeight))
    return maxHeight

def getLocalBlockCount():
    height = neoapi.getCurrentHeight(LOCAL_SRV)
    logging.info('[getLocalBlockCount] localheight: {0}'.format(height))
    return height

def isLocalRunning():
    #(state, output) = commands.getstatusoutput('ps -ef | grep "./neo-cli" | wc -l')#ps -ef -o pid -o comm | grep neo-cli
    p = Popen('ps -ef -o pid -o comm | grep neo-cli | wc -l', shell=True, stdout=PIPE)
    output = p.communicate()[0]
    output = output.decode('utf-8')
    state = p.returncode
    logging.info('[isLocalRunning] shell command, state: {0}, output: {1}'.format(state, output))
    if state != 0:
        height = getLocalBlockCount()
        logging.info('[isLocalRunning] command failed, use rpc getblockcount. height: {0}'.format(height))
        if height < 0:
            return False
        return True
    if int(output) < 1:
        return False
    return True

def startLocalNode():
    result = os.system('./shell/start.sh {0}'.format(config['neoclipath']))
    if result == 0:
        global lastRestartTimestamp 
        lastRestartTimestamp = datetime.now()
        return True
    return False

def stopLocalNode():
    result = os.system('./shell/stop.sh')
    if result == 0:
        return True
    os.system('ps -ef -o pid -o comm | grep neo-cli | awk \'{print $1}\'| xargs kill')
    return True

def restartRecently():
    if timedelta(minutes=START_SILENT) > datetime.now() - lastRestartTimestamp:
        return True
    return False
	
def notChangeOverLimit():
    if timedelta(minutes=START_SILENT) < datetime.now() - lastRecordLocalTime:
        return True
    return False
	
def shutdownScreen():
    result = os.system('./shell/shutdownScreen.sh')
    logging.warning('shutdown.res:{0}'.format(result))
    if result == 0:
        return True
    return False
	
while True:
    if not isLocalRunning():
        if not shutdownScreen():
	    logging.info('[shutdownScreen] res: false')
            continue;
        startLocalNode()

    time.sleep(INTERVAL)
    #get rss
    mem = state.getRss()
    if 0 < mem:
        logging.info('[getrss] neo-cli rss: {0}KiB'.format(mem))
    #check block count
    localBlockCount = getLocalBlockCount()
    bestBlockCount = getBestBlockCount()
    if localBlockCount < 0 or bestBlockCount < 0:
        logging.error('[wrongheight] wrong height, localheight: {0}, bestheight: {1}'.format(localBlockCount, bestBlockCount))
        continue
    if localBlockCount > lastRecordLocalIndex:
	lastRecordLocalIndex = localBlockCount
	lastRecordLocalTime = datetime.now()
    if localBlockCount == lastRecordLocalIndex and notChangeOverLimit():
        restart_cnt += 1
        logging.warning('[restart] restarting, restart_cnt: {0}, localheight: {1}, bestheight: {2}'.format(restart_cnt, localBlockCount, bestBlockCount))
        stopLocalNode()
        continue
    if RESTART_THRESHOLD < bestBlockCount - localBlockCount and not restartRecently():
        restart_cnt += 1
        logging.warning('[restart] restarting, restart_cnt: {0}, localheight: {1}, bestheight: {2}'.format(restart_cnt, localBlockCount, bestBlockCount))
        stopLocalNode()
