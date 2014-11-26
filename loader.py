#!/usr/bin/env python

from urlparse import urljoin
import json
import requests
import sys

# this holds the challenge data
challenge = {}

# this holds the tasks geojson to post
tasks_geojson = ""

# are we creating or updating?
update = False

# are we testing?
testing = False

# server to talk to
server = "http://localhost:5000/" if testing else "http://dev.maproulette.org/"
challenge_endpoint = ""
tasks_endpoint = ""

# add'l headers for request
headers = {'content-type': 'application/json'}  # json header


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
    print("""
OK, first we will need to collect some challenge metadata.
You can find out more about the meaning of these various bits in the MapRoulette
Challenge tutorial --> https://gist.github.com/mvexel/b5ad1cb0c91ac245ea3f

The default values are for an example challenge that deals with
businesses without opening hours around Salt Lake City, Utah, USA.
""")
    # ask for slug,
    challenge["slug"] = prompt(
        "Challenge slug",
        default="business-no-hours")
    #title,
    challenge["title"] = prompt(
        "Challenge title",
        default="Businesses without Opening Hours")
    #blurb,
    challenge["blurb"] = prompt(
        "Challenge blurb (optional)",
        default="Add opening hours to shops and restaurants")
    #description,
    challenge["description"] = prompt(
        "Challenge description (optional)",
        default="Lots of businesses are in OSM but don't have opening hours.")
    #help,
    challenge["help"] = prompt(
        "Challenge help (optional)",
        default="Look up the opening hours on the business web site and add an `opening_hours` tag to the node")
    #instruction,
    challenge["instruction"] = prompt(
        "Challenge instruction",
        default="Look up the opening hours on the business web site and add an `opening_hours` tag to the node")
    #difficulty
    challenge["difficulty"] = prompt(
        "Challenge difficulty (1=easy, 2=medium, 3=hard)",
        default=2)


def choose_server():
    global server
    global challenge_endpoint
    global tasks_endpoint

    server = prompt("Which MapRoulette server shall we use?", default=server)
    challenge_endpoint = urljoin(server, "/api/admin/challenge/{slug}".format(slug=challenge["slug"]))
    tasks_endpoint = urljoin(server, "/api/admin/challenge/{slug}/tasks?geojson".format(slug=challenge["slug"]))


def create_or_update_challenge():
    print("We will {createorupdate} your challenge {slug}".format(
        createorupdate="update" if update else "create",
        slug=challenge["slug"]))
    if update:
        response = requests.put(challenge_endpoint, data=json.dumps(challenge), headers=headers)
    else:
        response = requests.post(challenge_endpoint, data=json.dumps(challenge), headers=headers)
    eval_response(response)
    return


def get_tasks_from_overpass():
    global tasks_geojson
    import overpass
    print("Now let's collect your tasks.")
    overpass_query = prompt(
        "Input the overpass query stub that returns the OSM objects you want fixed",
        default="""node(40.5,-112.2,40.8,-111.7)[amenity~"shop|restaurant"][opening_hours!~"."]""")
    api = overpass.API()
    tasks_geojson = api.get(overpass_query, asGeoJSON=True)
    if testing:
        print(tasks_geojson)
    prompt("Your query returned {num} tasks. Press Enter to continue and post these tasks.".format(
        num=len(tasks_geojson['features'])))


def post_tasks():
    if update:
        print("Updating tasks...")
        response = requests.put(tasks_endpoint, data=json.dumps(tasks_geojson), headers=headers)
    else:
        print("Creating tasks...")
        response = requests.post(tasks_endpoint, data=json.dumps(tasks_geojson), headers=headers)
    eval_response(response)
    return


def activate_challenge():
    print("Activating your challenge now...")
    challenge["active"] = True
    response = requests.put(challenge_endpoint, data=json.dumps(challenge), headers=headers)
    eval_response(response)


def eval_response(response):
    if not str(response.status_code).startswith("2"):
        print("something went wrong with this request and we got an HTTP status code {status_code} back".format(
            status_code=response.status_code))
        sys.exit(1)
    else:
        print("That went A-OK")


def main():
    interactive = True  # interactive is all we have for now.
    global update

    if testing:
        print("Testing...")

    if interactive:
        # display help text
        display_help_text()

        # prompt to continue
        prompt()

        # get challenge metadata
        get_challenge_meta()

        # which server will we be using?
        choose_server()

        # is this going to be a new or existing challenge?
        update = prompt("Will this be a new challenge? (y/n)", default="n") != "y"

        # create or update the challenge
        create_or_update_challenge()

        # now collect the tasks
        get_tasks_from_overpass()

        # post!
        post_tasks()

        # activate the challenge
        activate_challenge()

        print("\nHey that went well. You should now be able to check out your challenge at {url}".format(
            url=urljoin(server, "#t={slug}".format(slug=challenge["slug"]))))

if __name__ == '__main__':
    main()
