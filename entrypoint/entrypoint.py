import json
import os
from urllib.parse import parse_qs
import logging
import hashlib
import hmac

import boto3


"""Slackbot secrets"""
SIGNING_SECRET = os.environ["SIGNING_SECRET"]
MAIN_LAMBDA_ARN = os.environ["MAIN_LAMBDA_ARN"]


def verify_slack_request(slack_signature, slack_request_timestamp, request_body):
    """Confirms POST to API gateway has come from Slack: concatenates headers
    and body and encodes then compares to Slack's client secret in an env var
    """

    """ Form the bytestring as stated in the Slack API docs. """
    basestring = f"v0:{slack_request_timestamp}:{request_body}".encode("utf-8")

    """ Make the Signing Secret a bytestring too. """
    slack_signing_secret = bytes(SIGNING_SECRET, "utf-8")

    """ Create a new HMAC "signature", and return the string presentation. """
    my_signature = (
        "v0=" + hmac.new(slack_signing_secret, basestring, hashlib.sha256).hexdigest()
    )

    """ Compare the the Slack provided signature to ours.
    If they are equal, the request should be verified successfully.
    Log the unsuccessful requests for further analysis """
    if hmac.compare_digest(my_signature, slack_signature):
        return True
    else:
        logging.error(f"Verification failed. my_signature: {my_signature}")
        return False


def slashcommand_reponse(problem):

    error_handling = {
        "directmessage": ":rotating_light: Use this in a channel not DM!",
        "privategroup": ":sleuth_or_spy: I can only export public channels.",
        "noreaction": ":slackpolice: You must add a reaction!",
        "nocolons": ":wave: You must use a reaction not string!",
        "success": ":hourglass_flowing_sand: Exporting timeline! :hourglass:",
    }
    logging.info(f"returned {error_handling[problem]} to user")
    return {"statusCode": "200", "body": error_handling[problem]}


def process_command(command_data):

    reaction = command_data.get("text", [""])[0]
    channel_name = command_data["channel_name"][0]

    if channel_name == "directmessage":
        return slashcommand_reponse("directmessage")
    if channel_name == "privategroup":
        return slashcommand_reponse("privategroup")
    if reaction == "":
        return slashcommand_reponse("noreaction")
    if reaction[0] != ":" or reaction[-1] != ":":
        return slashcommand_reponse("nocolons")

    logging.info(f"Triggering main lambda with {command_data}")
    awslambda = boto3.client("lambda")
    awslambda.invoke(
        FunctionName=MAIN_LAMBDA_ARN,
        InvocationType="Event",
        Payload=json.dumps(command_data),
    )

    logging.info("finished triggering lambda: return OK to Slack and finish")
    return slashcommand_reponse("success")


def lambda_handler(event, context):
    """Check request came from Slack"""
    slack_signature = event["headers"]["X-Slack-Signature"]
    slack_request_timestamp = event["headers"]["X-Slack-Request-Timestamp"]

    if (
        verify_slack_request(slack_signature, slack_request_timestamp, event["body"])
        is True
    ):

        logging.info("Authenticated against client secret")
    else:
        logging.warning("Bad request: Failed comparison to signing secret.")
        response = {"statusCode": 400, "body": "Failed auth verification"}
        return response

    """Parse the Slack data."""
    command_data = parse_qs(event["body"])
    slash_returned_message = process_command(command_data)

    """
    Return 200 to let Slackbot know it's API call was handled and not to retry.
    """
    return slash_returned_message
