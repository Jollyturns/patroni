from datetime import datetime, timedelta
from lettuce import world, steps
import time
import pytz
import requests


@steps
class PatroniAPISteps(object):

    def __init__(self, environ):
        self.env = environ
        self.response = None
        self.status_code = None

    # there is no way we can find out if the node has already
    # started as a leader without checking the DCS. We cannot
    # just rely on the database availability, since there is
    # a short gap between the time PostgreSQL becomes available
    # and Patroni assuming the leader role.
    @staticmethod
    def is_a_leader(step, name, time_limit):
        '''(\w+) is a leader after (\d+) seconds'''
        max_time = time.time() + int(time_limit)
        while (world.etcd_ctl.query("leader") != name):
            time.sleep(1)
            if time.time() > max_time:
                assert False, "{0} is not a leader in etcd after {1} seconds".format(name, time_limit)

    @staticmethod
    def sleep_for_n_seconds(step, value):
        '''I sleep for (\d+) seconds'''
        time.sleep(int(value))

    def do_get(self, step, url):
        '''I issue a GET request to (https?://(?:\w|\.|:|/)+)'''
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            self.code = None
            self.response = None
        else:
            self.status_code = r.status_code
            try:
                self.response = r.json()
            except ValueError:
                self.response = r.content

    def do_post_empty(self, step, url):
        '''I issue an empty POST request to (https?://(?:\w|\.|:|/)+)'''
        self.do_post(step, url, None)

    def do_post(self, step, url, data):
        '''I issue a POST request to (https?://(?:\w|\.|:|/)+) with ((?:\w+=(?:\w|\.|:|-|\+|\s)+,?)+)'''
        post_data = {}
        if data:
            post_components = data.split(',')
            for pc in post_components:
                if '=' in pc:
                    k, v = pc.split('=', 2)
                    post_data[k.strip()] = v.strip()
        try:
            r = requests.post(url, json=post_data)
        except requests.exceptions.RequestException:
            self.code = None
            self.response = None
        else:
            self.status_code = r.status_code
            try:
                self.response = r.json()
            except ValueError:
                self.response = r.content

    def check_response(self, step, component, data):
        '''I receive a response (\w+) (.*)'''
        if component == 'code':
            assert self.status_code == int(data),\
                    "status code {0} != {1}, response: {2}".format(self.status_code, int(data), self.response)
        elif component == 'text':
            assert self.response == data.strip('"'), "response {0} does not contain {1}".format(self.response, data)
        else:
            assert component in self.response, "{0} is not part of the response".format(component)
            assert self.response[component] == data, "{0} does not contain {1}".format(component, data)

    def replication_works(self, step, master, replica, time_limit):
        '''replication works from (\w+) to (\w+) after (\d+) seconds'''
        step.behave_as("""
           When I add the table test_{0} to {1}
            Then table test_{0} is present on {2} after {3} seconds
            """.format(int(time.time()), master, replica, time_limit))

    def scheduld_failover(self, step, at_url, from_host, to_host, in_seconds):
        '''I issue a scheduled failover at (https?://(?:\w|\.|:|/)+) from (\w+) to (\w+) in (\d+) seconds'''
        step.behave_as("""
            Given I issue a POST request to {0}/failover with leader={1},candidate={2},scheduled_at={3}
            """.format(at_url, from_host, to_host, datetime.now(pytz.utc) + timedelta(seconds=int(in_seconds))))


PatroniAPISteps(world)