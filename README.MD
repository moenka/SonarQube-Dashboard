SonarQube Dashboard
===================

Simple dashboard to show all SonarQube projects on one screen with the feedback of which project has a failed quality gate.

## Quickstart Guide

1. Copy `example.ini` to `config.ini` and fill out the configuration file.
2. Run `sqdash.py`.
3. In your browser go to `http://127.0.0.1:8050/` to see the dashboard.

## Dashboard Size

The dashboard is hardcoded to support a 12x10 tiles dashboard so currently it can show a maximum of 120 projects at the same time. If you want to show more projects, redefine the width and height of the tiles in the `assets/style.css`. Note that you need to use global padding and grid-gap into account when doing you calculations.

