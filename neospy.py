import sys
import os
import time
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
sys.path.append('./')
from config import config
from config import config_mainnet
from config import config_testnet
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
SEEDS = config['seeds']
NEOCLI_PATH = config['neoclipath']

type = ""
if len(sys.argv) > 1:
	type = sys.argv[1]
if type == "mainnet":
	RESTART_THRESHOLD = config_mainnet['restartthreshold']
	START_SILENT = config_mainnet['startsilent']
	INTERVAL = config_mainnet['interval']
	LOCAL_SRV = config_mainnet['localsrv']
	SEEDS = config_mainnet['seeds']
if type == "testnet":
	RESTART_THRESHOLD = config_testnet['restartthreshold']
	START_SILENT = config_testnet['startsilent']
	INTERVAL = config_testnet['interval']
	LOCAL_SRV = config_testnet['localsrv']
	SEEDS = config_testnet['seeds']
if type == "":
	type = "default_mainnet"
lastRestartTimestamp = datetime.fromtimestamp(0)
lastRecordLocalIndex = 0
lastRecordLocalTime = datetime.fromtimestamp(0)
restart_cnt = 0

def getBestBlockCount():
    maxHeight = -1
    for seed in SEEDS:
        height = neoapi.getCurrentHeight('http://' + seed)
        if maxHeight < height:
            maxHeight = height
    logging.info('[{0}] getBestBlockCount maxheight: {1}'.format(type, maxHeight))
    return maxHeight

def getLocalBlockCount():
    height = neoapi.getCurrentHeight(LOCAL_SRV)
    logging.info('[{0}] getLocalBlockCount localheight: {1}'.format(type, height))
    return height

def isLocalRunning():
    #(state, output) = commands.getstatusoutput('ps -ef | grep "./neo-cli" | wc -l')#ps -ef -o pid -o comm | grep neo-cli
    p = Popen('ps -ef -o pid -o comm | grep neo-cli | wc -l', shell=True, stdout=PIPE)
    output = p.communicate()[0]
    output = output.decode('utf-8')
    state = p.returncode
    logging.info('[{0}] isLocalRunning shell command, state: {1}, output: {2}'.format(type, state, output))
    if state != 0:
        height = getLocalBlockCount()
        logging.info('[{0}] isLocalRunning command failed, use rpc getblockcount. height: {1}'.format(type, height))
        if height < 0:
            return False
        return True
    if int(output) < 1:
        return False
    return True

def startLocalNode():
    result = os.system('./shell/start.sh {0}'.format(NEOCLI_PATH))
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
    logging.warning('[{0}] shutdown.res:{1}'.format(type, result))
    if result == 0:
        return True
    return False
	
while True:
    if not isLocalRunning():
        if not shutdownScreen():
            continue;
        startLocalNode()

    time.sleep(INTERVAL)
    #get rss
    mem = state.getRss()
    if 0 < mem:
        logging.info('[{0}] getrss rss: {1}KiB'.format(type, mem))
    #check block count
    localBlockCount = getLocalBlockCount()
    bestBlockCount = getBestBlockCount()
    if localBlockCount < 0 or bestBlockCount < 0:
        logging.error('[{0}] wrong height, localheight: {1}, bestheight: {2}'.format(type, localBlockCount, bestBlockCount))
        continue
    if localBlockCount > lastRecordLocalIndex:
        lastRecordLocalIndex = localBlockCount
        lastRecordLocalTime = datetime.now()
    if localBlockCount == lastRecordLocalIndex and notChangeOverLimit():
        restart_cnt += 1
        logging.warning('[{0}] restarting, restart_cnt: {1}, localheight: {2}, bestheight: {3}'.format(type, restart_cnt, localBlockCount, bestBlockCount))
        stopLocalNode()
        continue
    if RESTART_THRESHOLD < bestBlockCount - localBlockCount and not restartRecently():
        restart_cnt += 1
        logging.warning('[{0}] restarting, restart_cnt: {1}, localheight: {2}, bestheight: {3}'.format(type, restart_cnt, localBlockCount, bestBlockCount))
        stopLocalNode()
	continue
    if localBlockCount > bestBlockCount and not restartRecently():
	restart_cnt += 1
	stopLocalNode();

