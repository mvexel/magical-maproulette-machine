#!/usr/bin/env python

from urlparse import urljoin
import json
import requests

challenge = {}

_servers = {
    "local": "http://localhost:5000/",
    "dev": "http://dev.maproulette.org/",
    "prod": "http://maproulette.org/"
}

_server = _servers["dev"]  # default to dev for now.


def display_help_text():
    print("""Hey. This is the magic MapRoulette Machine.
It lets you magically create a real MapRoulette challenge
from an Overpass QL query. Pretty neat.

This is the interactive mode. That's all we have for now,
so just follow along.
""")


def prompt(prompt="Press enter to continue", default=None):
    return raw_input("{} {} --> ".format(
        prompt,
        "(Enter for {default})".format(
            default=default) if default else "")) or default


def get_challenge_meta():
    # ask for slug,
    challenge["slug"] = prompt(
        "Challenge slug",
        default="test-challenge")
    #title,
    challenge["title"] = prompt(
        "Challenge title",
        default="Test Challenge")
    #blurb,
    challenge["blurb"] = prompt(
        "Challenge blurb (optional)",
        default="Blurb for Test Challenge")
    #description,
    challenge["description"] = prompt(
        "Challenge description (optional)",
        default="This describes Test Challenge")
    #help,
    challenge["help"] = prompt(
        "Challenge help (optional)",
        default="Help for the Test Challenge")
    #instruction,
    challenge["instruction"] = prompt(
        "Challenge instruction",
        default="This tells the user what to do for each task")
    #difficulty
    challenge["difficulty"] = prompt(
        "Challenge difficulty (1=easy, 2=medium, 3=hard)",
        default=1)


def create_challenge():
    print("We will create your challenge {slug}".format(slug=challenge["slug"]))
    print(json.dumps(challenge))
    challenge_endpoint = urljoin(_server, "/api/admin/challenge/{slug}".format(slug=challenge["slug"]))
    print(challenge_endpoint)
    pass


def post_tasks():
    tasks_endpoint = urljoin(_server, "/api/admin/challenge/{slug}/tasks".format(slug=challenge["slug"]))
    print(tasks_endpoint)
    pass


def main():
    interactive = True  # interactive is all we have for now.

    if interactive:
        # display help text
        display_help_text()

        # prompt to continue
        prompt()

        # get challenge metadata
        get_challenge_meta()

        # is this going to be a new or existing challenge?
        is_new = prompt("Will this be a new challenge? (y/n)")

        # if new, create
        if is_new == "y":
            create_challenge()


if __name__ == '__main__':
    main()

# overpass query
# summary results
# post
# result + link to challenge
