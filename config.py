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