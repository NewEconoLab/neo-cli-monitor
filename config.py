import json

config = {}
with open('config.json', 'r') as configfile:
    res = json.load(configfile)
    config['neoclipath'] = res['neoclipath']
    config['seeds'] = res['seeds']
    config['interval'] = res['interval']
    config['restartthreshold'] = res['restartthreshold']
    config['startsilent'] = res['startsilent']
    config['localsrv'] = res['localsrv']
	
config_mainnet = {}
with open('config.mainnet.json', 'r') as configfile:
    res = json.load(configfile)
    config_mainnet['neoclipath'] = res['neoclipath']
    config_mainnet['seeds'] = res['seeds']
    config_mainnet['interval'] = res['interval']
    config_mainnet['restartthreshold'] = res['restartthreshold']
    config_mainnet['startsilent'] = res['startsilent']
    config_mainnet['localsrv'] = res['localsrv']

config_testnet = {}
with open('config.testnet.json', 'r') as configfile:
    res = json.load(configfile)
    config_testnet['neoclipath'] = res['neoclipath']
    config_testnet['seeds'] = res['seeds']
    config_testnet['interval'] = res['interval']
    config_testnet['restartthreshold'] = res['restartthreshold']
    config_testnet['startsilent'] = res['startsilent']
    config_testnet['localsrv'] = res['localsrv']