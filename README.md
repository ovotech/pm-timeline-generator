## Post-mortem Timeline Generator

Mark a message in a slack channel with `:small_blue_diamond:` and point the
script at the channel to generate a timeline of events.

```
pip3 install slackclient

export SLACK_API_TOKEN=aaaa-111111111111111111111111111111111111111111111111111111111111111111111

python3 script.py inc-000 :small_blue_diamond:
```

```
2019-09-10 15:28:14 Jim <@U054TBYPJ> set the channel purpose: INC-000 - Bongo snails deletion from Spark AD sync - <https://ovotech.atlassian.net/browse/INC-192>
2019-09-10 15:33:21 Jim I have been told not to re-create any for now as Bongo may be able to reverse this :crossed_fingers::skin-tone-3:  - This was before I recreated the finance@ovo one
to get it sending all nachos back to Gombo. This one should be working as before, but there will be no historical nachoss which is fine as they are all in their Gombo Service Desk
2019-09-10 15:41:06 Jim nachoss that feed into Blimp will still have the log of nachoss in Blimp itsself. Any group that is used in snails itsself could potentially lose every in
teraction if Bongo are unable to fix this
2019-09-10 16:02:37 Jim Latest google reponse
2019-09-10 16:04:29 Jim 1) recreate any snails that went into Gombo and Salesfroce - Foxy on this now.
2019-09-10 16:05:00 Jim 2) Definitive answer from Bongo on whether snails can be recovered (ETA 1hr).
2019-09-10 16:05:23 Jim 3) Following that, consult teams for which data may be lost and make a call on whether to recreate.
2019-09-10 16:08:52 Jim Impact update: for the snails in question, some go into Blimp (or Gombo), and so their content will have been preserved. For other snails, any messages in them th
at were not worked may be lost. For all snails, any nachoss sent between them having been deleted and recreated will not have been delivered.
2019-09-10 16:17:59 Jim <@U047VTCSX> how long until next comms?
2019-09-10 16:18:12 Jim 39 mins on my timer
2019-09-10 16:40:01 Jim We were alerted at about 15:30, but the sync happened at 1:31 PM from looking at the logs
2019-09-10 17:13:31 Jim Comms have been sent and have updated those to say that the issue is resolved now (pending RCA)

Foxy is speaking with owners of Bongo snails to explain what has happened and why we are yet to recreate their group. When we have an update from Bongo can we post it in here?

We have a window of 13:31 Jim:21 for Customer facing nachoss which I have put in the comm. The time gets gradually later for SF and DL's leading up to 17:04. With Collab nachosboxes still bounci
ng for now.
2019-09-10 17:58:03 Jim So Based on this we should stand down for now. Both myself and <@U054TBYPJ> will be picking up the remaining snails offline. Thanks all!
```
