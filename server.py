import os
from datetime import timedelta, datetime

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

temperature_service_url = os.environ.get('TEMPERATURE_SERVICE_URL', 'http://127.0.0.1:8000')
windspeed_service_url = os.environ.get('WINDSPEED_SERVICE_URL', 'http://127.0.0.1:8080')


def date_range(start, end):
    current_date = start

    while current_date <= end:
        yield current_date
        current_date += timedelta(days=1)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def get_date(param_name):
    try:
        date_param = request.args.get(param_name, '')
        date = datetime.strptime(date_param, '%Y-%m-%dT%H:%M:%SZ')
        return date
    except ValueError:
        raise InvalidUsage(f"Not valid datetime string for `{param_name}` query param")


def get_external_service(date, url):
    try:
        resp = requests.get(f'{url}/?at={date}')

        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            raise InvalidUsage(resp.json()['message'], status_code=404)

        raise InvalidUsage('Unexpected Error')
    except requests.exceptions.ConnectionError:
        raise InvalidUsage(f"External service {url} is unavailable or dont have data for `{date}` query param")


def get_weather_data(date):
    if request.path == '/temperatures':
        return get_external_service(date, temperature_service_url)

    elif request.path == '/speeds':
        return get_external_service(date, windspeed_service_url)

    elif request.path == '/weather':
        return {
            **get_external_service(date, temperature_service_url),
            **get_external_service(date, windspeed_service_url)
        }

    return {}


@app.route("/weather")
@app.route("/speeds")
@app.route("/temperatures")
def temperatures():
    start = get_date("start")
    end = get_date("end")
    result = []

    for date in date_range(start, end):
        strf_date = date.strftime(format='%Y-%m-%dT%H:%M:%SZ')
        result += [{
            'date': strf_date,
            **get_weather_data(strf_date)
        }]

    return jsonify(result)
