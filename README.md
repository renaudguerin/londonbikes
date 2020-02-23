Purpose
=======

This script was written for an interview coding exercise.
It allows searching for docking points in the London public bike scheme, either by name or coordinates.
Details of a specific bike point can also be retrieved.

Installing dependencies
=======================

pip install pipenv
pipenv install

Required environment variables
==============================

Please set TFL_APP_ID and TFL_APP_KEY to an app ID and key obtained from https://api.tfl.gov.uk 

Usage
=====
londonbikes search <search_string>
londonbikes search <latitude> <longitude> <radius_in_metres>
londonbikes id <bike_point_id>
