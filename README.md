## Post-mortem Timeline Generator

Mark messages in a public slack channel with a reaction emoji such as
`:small_blue_diamond:` and export them to a file sent via DM.

Trigger with: `/timeline :small_blue_diamond:`

Here's what it looks like when used:

![ux](/images/timeline-ux.jpg)

and here's the backend:

![architecture](/images/architecture.jpg)
## To deploy:
### Set up pre-requisites
* Python3
* `pip install --user awscli aws-sam-cli pipenv`
* Valid AWS credentials
* Slack permission to create a Slack application.

### Create a Slack App
* Start here: https://api.slack.com/apps and create an App.

* add a Bot user, and hit Install App. Customise the name and preference :)

* Note down the App and Bot OAuth tokens, and the Signing Secret to set
as variables later.

* In OAuth and Permissions, add these:
    - channels:history (to parse the channel’s messages for reactions)
    - chat:write:bot (to message the user as the bot)
    - chat:write:user (to write ephemeral user-only messages to the user)
    - im:read (to handle the slash command and fail gracefully in dm’s)
    - files:write:user (to send the file)
    - users:read (to read the user directory and work out username to user id
     to make the output legible).

* You'll need your API Gateway URL to enable the slash command: we'll come back
to this.

### Set AWS parameters
Create S3 bucket if required:
```
aws s3 mb s3://deploy-timeline-<uniquename>
```

Set:
```
BUCKET='deploy-timeline' # Bucket to hold .yml in AWS for SAM
STACK_NAME='timeline-tool' # CF stack name
BOT_TOKEN=<slack bot token> # From slack app
SLACK_TOKEN=<slack app token> # From slack app
SIGNING_SECRET=<slack signing secret> # From slack app
LOGGING_DESTINATION=<arn of logging resource>
LOGGING_FORMAT=<desired logging format>
```

## Deploy

From this repo's directory, deploy `deploy.yml` using SAM CLI (a Cloudformation
transform) to create the AWS resources required. The below will upload 
requirements to S3, create a new .yml, push to AWS then clean up after itself.

Run:
```
./package.sh
sam package --template-file deploy.yml \
 --s3-bucket $BUCKET --output-template-file packaged.yml --region eu-west-1
sam deploy --template-file packaged.yml \
 --stack-name $STACK_NAME --capabilities CAPABILITY_NAMED_IAM \
 --region eu-west-1 --parameter-overrides SigningSecret=$SIGNING_SECRET \
 SlackBotToken=$BOT_TOKEN SlackAppToken=$SLACK_TOKEN \
 LoggingDestinationArn=$LOGGING_DESTINATION LoggingFormat=$LOGGING_FORMAT \
 --confirm-changeset
./package_cleanup.sh

```

You can now create your Slack App's slash command (I went with `/timeline`) 
and add the created API Gateway's URL to it! 🎉
