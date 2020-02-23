#!/usr/bin/env python3

import os
import sys

import requests
from geopy.distance import distance
from tabulate import tabulate

api_url_base = "https://api.tfl.gov.uk/BikePoint/"
timeout = 30


def search_by_coords(coords, radius):
    r = requests.get(api_url_base, params=credentials, timeout=timeout)
    r.raise_for_status()
    bikepoints = r.json()
    # In Python 3.8 one can do an assignment within the loop comprehension condition:
    # nearby_bikepoints = [ dict({'distance':dist},**b) for b in bikepoints
    #                       if dist := distance(coords,(b['lat'],b['lon'])).m <= radius ]
    # Until then, use a regular for loop to avoid evaluating distance twice :
    results = []
    for b in bikepoints:
        dist = distance(coords, (b['lat'], b['lon'])).m
        if (dist <= radius):
            match = {key: b[key] for key in ('id', 'commonName', 'lat', 'lon')}
            match["distance"] = dist
            results.append(match)
            # or just : results.append(dict({'distance':dist},**match))
    return results


def search_by_name(name):
    r = requests.get(api_url_base + "Search",
                     params={'query': name, **credentials}, timeout=timeout)
    r.raise_for_status()
    bikepoints = r.json()
    return [{k: b[k] for k in ('id', 'commonName', 'lat', 'lon')} for b in bikepoints]


def show_id(id):
    r = requests.get(api_url_base + id, params=credentials, timeout=timeout)
    if r.status_code == requests.codes.ok:
        bikepoint = r.json()
        result = {k: bikepoint[k] for k in ('commonName', 'lat', 'lon')}
        neededproperties = [p for p in bikepoint['additionalProperties']
                            if p["key"] in ('NbBikes', 'NbEmptyDocks')]
        extra_fields = {p['key']: int(p['value']) for p in neededproperties}
        result.update(extra_fields)
        return [result]
    elif r.status_code == 404:
        print(f"Bike point id {id} not recognised")
        sys.exit(13)
    else:
        r.raise_for_status()


def usage():
    name=sys.argv[0]
    print("Usage:\n"
          f"{name} search <search_string>\n"
          f"{name} search <latitude> <longitude> <radius_in_metres>\n"
          f"{name} id <bike_point_id>"
          )
    sys.exit(1)


def pretty_print(data):
    headers = {'id': 'Id', 'commonName': 'Name', 'lat': 'Latitude', 'lon': 'Longitude',
               'NbBikes': 'Num Bikes', 'NbEmptyDocks': 'Empty Docks'}
    print(tabulate(data, headers=headers, tablefmt="plain"))


def init_credentials():
    global credentials
    try:
        credentials = {'app_id': os.environ["TFL_APP_ID"],
                       'app_key': os.environ["TFL_APP_KEY"]}
    except KeyError:
        print("Please set the environment variables TFL_APP_ID and TFL_APP_KEY")
        sys.exit(99)


def main(argv):
    def get_arg(index):
        try:
            return argv[index]
        except IndexError:
            return None

    init_credentials()

    if get_arg(1) == "search":
        if len(argv) == 5:
            try:
                pretty_print(
                    search_by_coords((float(argv[2]), float(argv[3])), float(argv[4])))
            except:
                print("The search request is invalid")
                sys.exit(11)
        elif len(argv) == 3:
            pretty_print(search_by_name(argv[2]))
        elif len(argv) == 2:
            print("Please specify a search term")
            sys.exit(10)
        else:
            usage()
    elif get_arg(1) == "id":
        if len(argv) == 3:
            pretty_print(show_id(argv[2]))
        elif len(argv) == 2:
            print("Please specify a bike point id")
            sys.exit(12)
        else:
            usage()
    else:
        usage()


if __name__ == "__main__":
    main(sys.argv)
