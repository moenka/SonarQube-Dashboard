#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import requests as req
from requests.auth import HTTPBasicAuth
from configparser import ConfigParser


def parse_config():
    cfg = ConfigParser()
    cfg.read('./config.ini')
    host = cfg['SQDash']['host']
    auth=HTTPBasicAuth(cfg['SQDash']['username'], cfg['SQDash']['password'])
    return host, auth

def get_componentList(host, auth):
    res = req.get("%s/api/components/search?qualifiers=TRK" % host, auth=auth)
    return res.json()['components']

def get_component_details(host, auth, components_list):
    components={}
    for component in components_list:
        components[component['id']] = {
            'name': component['name'],
            'key': component['key']
        }
        compRes = req.get((
            "%s/api/measures/component?component=%s&metricKeys="
            "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc") % (
            host, component['key']), auth=auth)
        for metric in compRes.json()['component']['measures']:
            components[component['id']][metric['metric']] = metric['value']
        compStatus = req.get("%s/api/qualitygates/project_status?projectKey=%s" % (
            host, component['key']), auth=auth).json()['projectStatus']['status']
        components[component['id']]['qualitygate'] = compStatus
    return components

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

def create_tiles(components):
    tiles = []
    for key, component in components.items():
        tileStatus = ('success' if component['qualitygate'] == 'OK' else 'failed')
        tile = html.Div([
            html.Div([
                html.P("%s" % component['name'], className='mdc-typography mdc-typography--body1')
            ], className='card-body')
        ], className="mdc-card tile tile-%s" % tileStatus)
        tiles.append(tile)
    return tiles


def main():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    host, auth = parse_config()
    componentList = get_componentList(host, auth)
    components = get_component_details(host, auth, componentList)
    #print(components)
    tiles = create_tiles(components)
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(tiles, className='tile-container')
    app.run_server()


if __name__ == '__main__':
    main()

