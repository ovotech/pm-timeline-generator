from datetime import datetime
from functools import lru_cache
import json
import os
import sys
import time

import slack


def list_channels(client, cursor=''):
    resp = client.channels_list(cursor=cursor)
    yield from resp.data['channels']
    next_cursor = resp.data['response_metadata']['next_cursor']
    if next_cursor:
        yield from list_channels(client, cursor=next_cursor)


def find_channel(client, channel_name):
    for channel in list_channels(client):
        if channel['name'].lower() == channel_name.lower():
            return channel


def get_channel_history(client, channel_id, latest=None):
    if latest is None:
        latest = str(time.mktime(datetime.now().timetuple()))
    resp = client.channels_history(channel=channel_id, latest=latest)
    messages = resp.data['messages']
    yield from messages
    if resp.data['has_more']:
        yield from get_channel_history(client,
                                       channel_id,
                                       latest=messages[-1]['ts'])


def get_reacted_messages(client, channel_id, reaction):
    for message in get_channel_history(client, channel_id):
        if "reactions" in message:
            for r in message['reactions']:
                if r['name'] == reaction:
                    yield message


@lru_cache(maxsize=128)
def lookup_user(client, user_id):
    return client.users_info(user=user_id).data


def print_timestamped_message(messages):
    for message in messages:
        user = lookup_user(client, message['user'])
        user_name = user['user']['profile']['real_name']
        # print(user_name)
        timestamp = int(message['ts'].split(".")[0])
        print(datetime.fromtimestamp(timestamp), user_name, message['text'])


if __name__ == '__main__':
    if len(sys.argv) == 3:
        reaction = sys.argv[2]
        if not (reaction[-1] == ":" and reaction[0] == ":"):
            raise Exception(
                "reaction should be wrapped in colons: `:small_blue_diamond:`")
        channel_name = sys.argv[1]
    else:
        raise Exception("Invalid number of args")

    client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
    # channels = list(list_channels(client))
    # print(len(channels))

    channel = find_channel(client, channel_name)

    # print(json.dumps(channel, indent=4))
    # history = list(get_channel_history(client, channel['id']))
    # print(json.dumps(history, indent=4))

    reacted = list(
        get_reacted_messages(client, channel['id'], "small_blue_diamond")
    )[::-1]

    json.dump(reacted, open('tmpdump.json', 'w'))
    # reacted = json.load(open('tmpdump.json'))
    # print(json.dumps(reacted, indent=4))
    print_timestamped_message(reacted)
