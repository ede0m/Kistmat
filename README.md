# Kismat 0.1

Kismat gives you that extra push you need on reddit.

Schedule bot sets to interact with target users.
Provide a `targets.json` file in the run directory:
```
{
    "reddit_username1" : {
        "vote_direction" : 1,
        "comments" : true,
        "submissions" : true
    },
    "reddit_username2" : {
        "vote_direction" : -1,
        "comments" : true,
        "submissions" : true
    }
}
```
Register targets to bots and register bots to schedules. 

Your bot-target, schedule-bot configurations and bot-post interactions are saved on program close. 
This session will load by default when restarting the app. You can also modify the session before running by modifying the `session.json` file in the run directory. 

You will need a reddit username to [register](https://redditclient.readthedocs.io/en/latest/oauth/) as a bot.

**please read [reddit's bottiquette wiki](https://www.reddit.com/wiki/bottiquette) before proceeding.**

----------------------------
### Installation

Kismat was developed with **Python 3.8.1.**

_Install the dependencies._

```sh
$ pip3 install -r requirements.txt
```

Then define your authentication for your username in a [`'praw.ini'`](https://praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html) file residing in the run directory. 

_Start the App._

```sh
$ python3 app.py
```
