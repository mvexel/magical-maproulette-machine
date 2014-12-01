#!/usr/bin/env python

from urlparse import urljoin
import json
import requests
import sys
import yaml
import argparse
import os
from voluptuous import Schema, Required

# the schema for the config file
config_schema = Schema({
    'challenge': {
        Required('slug'): str,
        Required('title'): str,
        'blurb': str,
        'description': str,
        'help': str,
        Required('instruction'): str,
        'difficulty': int},
    Required('overpass_query'): str,
    Required('maproulette_server'): str
})


# this holds the challenge data
challenge = {}

# this holds the tasks geojson to post
tasks_geojson = ""

# are we creating or updating?
update = True

# should we be verbose?
verbose = False

# are we in interactive mode?
interactive = False

# are we dry-runnning?
dryrun = False

config = {
    'challenge': {
        'difficulty': 2,
        'description': "Lots of businesses are in OSM but don't have opening hours.",
        'title': 'Businesses without Opening Hours',
        'instruction': 'Look up the opening hours on the business web site and add an `opening_hours` tag to the node',
        'slug': 'business-no-hours',
        'blurb': 'Add opening hours to shops and restaurants',
        'help': 'Look up the opening hours on the business web site and add an `opening_hours` tag to the node'},
    'maproulette_server': 'http://dev.maproulette.org/',
    'overpass_query': 'node(40.5,-112.2,40.8,-111.7)[amenity~"shop|restaurant"][opening_hours!~"."]'}

# endpoints
server = ""
challenge_endpoint = ""
tasks_endpoint = ""

# add'l headers for request
headers = {'content-type': 'application/json'}  # json header


def process_config_file(path):
    global config
    try:
        with open(path, 'rb') as stream:
            config = yaml.load(stream)
            try:
                config_schema(config)
            except Exception, e:
                raise e
            if verbose:
                print("configuration read in: \n {}".format(config))
        print("Config file read successfully, continuing to post challenge and tasks...\n")
    except Exception:
        raise
    choose_server()


def display_help_text():
    print("""Your query needs to be formulated in Overpass QL.
If you are not familiar with this language, head over to the
Language Guide at http://bit.ly/overpass-ql-guide or the
Language Reference at http://bit.ly/overpass-ql-ref. To test
your queries, use Overpass Turbo at http://overpass-turbo.eu/

This is the interactive mode. It will guide you through the
entire process step by step. There is also a 'headless' mode
that requires no user intervention, and uses a config file
instead. Invoke the Machine with the --h switch to learn more.
""")
    prompt()


def prompt(prompt="Press enter to continue", default=None):
    return raw_input("{} {} --> ".format(
        prompt,
        "(Enter for {default})".format(
            default=default) if default else "")) or default


def get_challenge_meta():
    challenge_defaults = config['challenge']

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
        default=challenge_defaults['slug'])
    #title,
    challenge["title"] = prompt(
        "Challenge title",
        default=challenge_defaults['title'])
    #blurb,
    challenge["blurb"] = prompt(
        "Challenge blurb (optional)",
        default=challenge_defaults['blurb'])
    #description,
    challenge["description"] = prompt(
        "Challenge description (optional)",
        default=challenge_defaults['description'])
    #help,
    challenge["help"] = prompt(
        "Challenge help (optional)",
        default=challenge_defaults['help'])
    #instruction,
    challenge["instruction"] = prompt(
        "Challenge instruction",
        default=challenge_defaults['instruction'])
    #difficulty
    challenge["difficulty"] = prompt(
        "Challenge difficulty (1=easy, 2=medium, 3=hard)",
        default=challenge_defaults['difficulty'])


def choose_server():
    global challenge_endpoint
    global tasks_endpoint
    global server

    if interactive:
        server = prompt("Which MapRoulette server shall we use?", default=config.get('maproulette_server'))
    else:
        server = config.get('maproulette_server')
    challenge_endpoint = urljoin(server, "/api/admin/challenge/{slug}".format(slug=config['challenge']['slug']))
    tasks_endpoint = urljoin(server, "/api/admin/challenge/{slug}/tasks?geojson".format(slug=config['challenge']['slug']))


def create_or_update_challenge():
    print("We will {createorupdate} your challenge {slug}".format(
        createorupdate="update" if update else "create",
        slug=config['challenge']['slug']))
    if verbose:
        print("going to {} at {}".format(("update" if update else "create"), challenge_endpoint))
    if update:
        response = requests.put(challenge_endpoint, data=json.dumps(config['challenge']), headers=headers)
    else:
        response = requests.post(challenge_endpoint, data=json.dumps(config['challenge']), headers=headers)
    eval_response(response)
    return


def get_tasks_from_overpass():
    """Get the geoJSON with the OSM features that should
    become tasks from the Overpass API.

    Uses the provided `overpass_query` from the config file
    if provided, or asks for query input in interactive mode"""

    import overpass

    global tasks_geojson

    print("Now let's collect your tasks.")

    if interactive:
        overpass_query = prompt(
            "Input the overpass query stub that returns the OSM objects you want fixed",
            default=config['overpass_query'])
    else:
        overpass_query = config['overpass_query']

    api = overpass.API()
    tasks_geojson = api.get(overpass_query, asGeoJSON=True)

    if verbose:
        print("GeoJSON returned:\n{}".format(tasks_geojson))

    # if the geojson has no features, give the opportunity to retry.
    if not "features" in tasks_geojson:
        if prompt("The Overpass query did not return any features. Would you like to try again?") == "y":
            get_tasks_from_overpass()
        exit(1)

    num_tasks = len(tasks_geojson['features'])

    print("Your query returned {num} tasks.".format(
        num=num_tasks))
    if interactive:
        prompt('Press Enter to continue and post these tasks.')


def post_tasks():
    """Posts the tasks to the MapRoulette server"""

    if update:
        print("Updating tasks...")
        response = requests.put(tasks_endpoint, data=json.dumps(tasks_geojson), headers=headers)
    else:
        print("Creating tasks...")
        response = requests.post(tasks_endpoint, data=json.dumps(tasks_geojson), headers=headers)
    eval_response(response)
    return


def activate_challenge():
    """Activates the challenge in the MapRoulette server"""

    print("Activating your challenge now...")
    challenge["active"] = True
    response = requests.put(challenge_endpoint, data=json.dumps(challenge), headers=headers)
    eval_response(response)


def eval_response(response):
    """Evaluates the HTTP response from the server.
    Anything that is not a 2XX response code is considered
    an error and will cause an exception to be raised."""

    if not str(response.status_code).startswith("2"):
        print("something went wrong with this request and we got an HTTP status code {status_code} back".format(
            status_code=response.status_code))
        sys.exit(1)
    else:
        print("That went A-OK")


def send_to_server():
    """Convenience function to create or update the challenge,
    collect GeoJSON from Overpass, post tasks and activate the
    challenge."""

    if not dryrun:
        # create or update the challenge
        create_or_update_challenge()

        # now collect the tasks
        get_tasks_from_overpass()

        # post!
        post_tasks()

        # activate the challenge
        activate_challenge()
    else:
        print("\nThis is where we would post your challenge to MapRoulette, but this is a dry run so we won't.")


def finalize():
    """Outputs a confirmation and goodbye message"""

    if not dryrun:
        print("\nHey that went well!\nYou should now be able to check out your challenge at:\n{url}".format(
            url=urljoin(server, "#t={slug}".format(slug=config['challenge']['slug']))))
    print("\nAll done!")
    sys.exit(0)


def main():
    """Main loop"""

    global update
    global dryrun
    global verbose
    global interactive

    # welcome!
    print("""
Hey! This is the Magic MapRoulette Machine.

It lets you magically create a real MapRoulette challenge
from an Overpass query. Pretty neat.
""")

    # parse the arguments on the left hand side
    parser = argparse.ArgumentParser(
        description="The Magic MapRoulette Machine")
    parser.add_argument(
        "--new",
        help="Create a new challenge? If omitted we will try to update an existing challenge.",
        action="store_false")
    parser.add_argument(
        "--v", "--verbose",
        dest="verbose",
        help="Verbose output",
        action="store_true")
    parser.add_argument(
        "--dry-run",
        dest="dryrun",
        help="Do not actually post anything",
        action="store_true")
    parser.add_argument(
        "config_file",
        help="YAML config file. If omitted, we will use interactive mode.",
        metavar="CONFIG_FILE",
        type=str,
        nargs="?")
    parser.set_defaults(new=False, dryrun=False, verbose=False)

    args = parser.parse_args()

    # store new / update
    if args.new:
        update = False

    # store dry run
    if args.dryrun:
        dryrun = True

    # store verbose
    if args.verbose:
        verbose = True
        print("Arguments passed:\n{}".format(args))

    if args.config_file and os.path.isfile(args.config_file):
        # process the config file
        process_config_file(args.config_file)

        # then update challenge
        send_to_server()

        # finalize
        finalize()
    else:
        interactive = True

    if interactive:
        # display help text
        display_help_text()

        # get challenge metadata
        get_challenge_meta()

        # which server will we be using?
        choose_server()

        # is this going to be a new or existing challenge?
        update = prompt("Will this be a new challenge? (y/n)", default="n") != "y"

        # send everything to the server
        send_to_server()

        # finalize
        finalize()

if __name__ == '__main__':
    main()
