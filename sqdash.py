#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import requests as req
import time
from configparser import ConfigParser
from flask_caching import Cache
from requests.auth import HTTPBasicAuth


app = dash.Dash(__name__)

cfg = ConfigParser()
cfg.read('./config.ini')
host = cfg['SQDash']['host']
auth=HTTPBasicAuth(cfg['SQDash']['username'], cfg['SQDash']['password'])
componentStatusUpdated = time.time()
componentStatusUpdateCycle = 300

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})


@cache.memoize(3600)
def get_components():
    timeStart = time.time()
    res = req.get("%s/api/components/search?qualifiers=TRK" % host, auth=auth)
    components={}
    for component in res.json()['components']:
        components[component['id']] = {
            'name': component['name'],
            'key': component['key']
        }
    print(f'get_components() duration: {time.time() - timeStart}s')
    return components

@cache.memoize(componentStatusUpdateCycle)
def get_component_status(components):
    timeStart = time.time()
    global componentStatusUpdated
    for key, component in components.items():
        #compRes = req.get((
        #    "%s/api/measures/component?component=%s&metricKeys="
        #    "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc") % (
        #    host, component['key']), auth=auth)
        #for metric in compRes.json()['component']['measures']:
        #    components[component['id']][metric['metric']] = metric['value']
        compStatus = req.get("%s/api/qualitygates/project_status?projectKey=%s" % (
            host, component['key']), auth=auth).json()['projectStatus']['status']
        components[key]['qualitygate'] = compStatus
    print(f'get_component_status() duration: {time.time() - timeStart}s')
    componentStatusUpdated = time.time()
    return components


def update_tiles():
    timeStart = time.time()
    tiles = []
    components = get_component_status(get_components())
    for key, component in components.items():
        tileStatus = ('success' if component['qualitygate'] == 'OK' else 'failed')
        tile = html.Div([
            html.Div([
                html.P("%s" % component['name'])
            ], className='card-body')
        ], className="mdc-card tile tile-%s" % tileStatus)
        tiles.append(tile)
    print(f'update_tiles() duration: {time.time() - timeStart}s')
    return html.Div([
        html.P((f'Updated {int(time.time() - componentStatusUpdated)}s ago, ',
                f'Update cycle: {componentStatusUpdateCycle}s'),
                className='last-updated'),
        html.Div(tiles, className='tile-container')
    ])


if __name__ == '__main__':
    app.layout = update_tiles
    app.run_server(debug=True)




# {
#  "_qHMDmzNtcYacbqv": {
#    "name": "Example Project",
#    "key": "org.example.project-name",
#    "code_smells": "0",
#    "bugs": "0",
#    "vulnerabilities": "0",
#    "ncloc": "0",
#    "duplicated_lines_density": "0.0",
#    "qualitygate": "OK"
#  }
#}

