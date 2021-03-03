import re
import time
from datetime import datetime
from functools import lru_cache
import html
import os
import logging

from slack_sdk import WebClient


BOT_TOKEN = os.environ["BOT_TOKEN"]
SLACK_TOKEN = os.environ["SLACK_TOKEN"]


def get_channel_history(client, channel_id, latest=None):
    if latest is None:
        latest = str(time.mktime(datetime.now().timetuple()))
    resp = client.conversations_history(channel=channel_id, latest=latest)
    messages = resp.data["messages"]
    yield from messages
    if resp.data["has_more"]:
        yield from get_channel_history(client, channel_id, latest=messages[-1]["ts"])


def get_reacted_messages(client, channel_id, reaction):
    logging.info(f"Getting all messages with {reaction}")
    reaction = reaction[1:-1]
    for message in get_channel_history(client, channel_id):
        if "reactions" in message:
            for r in message["reactions"]:
                if r["name"] == reaction:
                    yield message


@lru_cache(maxsize=128)
def lookup_user(client, user_id):
    return client.users_info(user=user_id).data["user"]


def who_posted_message(client, message):
    if "user" in message:
        user = lookup_user(client, message["user"])
        return user["profile"]["real_name"]
    else:
        return message["username"]


def format_slack_msg(client, text):
    users = {
        user_id: lookup_user(client, user_id)["profile"]["real_name"]
        for user_id in set(re.findall(r"<@([^>]+)>", text))
    }
    for user_id, name in users.items():
        text = text.replace(f"<@{user_id}>", "@" + name)

    text = html.unescape(text)
    return text.replace("\n\n", "\n")


def collate_timestamped_messages(client, messages):
    logging.info("Collating all messages into human readable output string")
    output = str()
    for message in messages:
        user_name = who_posted_message(client, message)
        timestamp = int(message["ts"].split(".")[0])
        text = message["text"]

        if "attachments" in message:
            other_text = "\n".join(
                attachment["text"].strip()
                for attachment in message["attachments"]
                if attachment.get("text")
            )
            if other_text:
                text = text + "\n" + other_text

        text = format_slack_msg(client, text)
        output += f"{datetime.fromtimestamp(timestamp)} " f"{user_name} : {text}\n\n"

    return output


def send_timeline_as_file(client, chan, output):
    logging.info("Sending multiline string as file content to Slack user")
    return client.files_upload(channels=chan, content=output, title="Timeline")


def lambda_handler(event, context):
    logging.info(f"Event trigger recieved: {event}")
    main(event)
    return None


def main(command_data):
    reaction = command_data.get("text", None)
    channel_id = command_data["channel_id"][0]
    channel_name = command_data["channel_name"][0]
    user_id = command_data["user_id"][0]

    logging.info("Getting Slack clients")
    client = WebClient(token=SLACK_TOKEN)
    bot_client = WebClient(token=BOT_TOKEN)

    reacted = list(get_reacted_messages(client, channel_id, reaction[0]))[::-1]

    file_output = collate_timestamped_messages(client, reacted)

    export_msg = (
        f"Here's your export of *#{channel_name}*'s"
        f" messages marked with {reaction[0]}:"
    )
    bot_client.chat_postMessage(channel=user_id, text=export_msg, as_user=True)
    if file_output:
        send_timeline_as_file(bot_client, user_id, file_output)
    else:
        logging.info("No messages had requested reaction")
        bot_client.chat_postMessage(
            channel=user_id,
            text=":sadparrot: No messages have the" f"{reaction[0]} reaction!",
            as_user=True,
        )
