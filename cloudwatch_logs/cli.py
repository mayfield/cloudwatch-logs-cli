#!/usr/bin/env python

import boto3
import datetime
import shellish
import time

awslogs = boto3.client('logs')


def _main(log_group, hours:float=None, follow=False, poll_freq_limit=5):
    """ Get latest logs from CloudWatch for a given log group. """
    last_ingest = 0
    now = datetime.datetime.now()
    next_token = None
    done = False
    max_age = hours * 3600
    seed = []
    while not done:
        kwargs = {"nextToken": next_token} if next_token else {}
        streams = awslogs.describe_log_streams(logGroupName=log_group,
                                               orderBy='LastEventTime',
                                               descending=True,
                                               **kwargs)
        if streams['logStreams']:
            s = streams['logStreams'][0]
            last_ingest = s['lastIngestionTime']
        for x in streams['logStreams']:
            age = now - datetime.datetime.fromtimestamp(x['creationTime'] / 1000)
            if age.total_seconds() >= max_age:
                done = True
                break
            seed.append(x)
        if 'nextToken' not in streams:
            break
        next_token = streams['nextToken']
    print_events(reversed(seed), log_group)
    if follow:
        limit = 50
        delay = 0.200
        while True:
            resp = awslogs.describe_log_streams(logGroupName=log_group,
                                                orderBy='LastEventTime',
                                                descending=True,
                                                limit=limit)
            limit = max(3, limit - 10)
            streams = [x for x in resp['logStreams'] if x['lastIngestionTime'] > last_ingest]
            if streams:
                last_ingest = streams[0]['lastIngestionTime']
                print_events(reversed(streams), log_group)
                delay = 0.200
            time.sleep(delay)
            delay = min(poll_freq_limit, delay * 1.5)
_main.__name__ = 'cloudwatch-logs'
main = shellish.autocommand(_main)


def fmt_event(x):
    msg = x['message']
    [maybe_type, *_] = msg.split(' ', 1)
    if maybe_type in ('START', 'END', 'REPORT'):
        return
    dt = datetime.datetime.fromtimestamp(x['timestamp'] / 1000)
    pretty_date = dt.strftime(f'%Y-%m-%d %I:%M:%S.{round(dt.microsecond / 1000):03} %p')
    msg_parts = msg.split('\t', 3)
    if len(msg_parts) == 4:
        [_, _, level, message] = msg_parts
        return f'{pretty_date} [{level}] {message.rstrip()}'
    else:
        # continuation line
        return msg.rstrip()


def print_events(streams, log_group, _last_event=[0]):
    for x in streams:
        resp = awslogs.get_log_events(logGroupName=log_group,
                                      logStreamName=x['logStreamName'],
                                      startFromHead=True)
        for ev in resp['events']:
            ts = ev['timestamp']
            if ts < _last_event[0]:
                continue
            _last_event[0] = ev['timestamp']
            line = fmt_event(ev)
            if line:
                print(line)
