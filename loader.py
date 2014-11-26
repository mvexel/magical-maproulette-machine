#!/usr/bin/env python


def display_help_text():
    print("""Hey. This is the magic MapRoulette Machine.
It lets you magically create a real MapRoulette challenge
from an Overpass QL query. Pretty neat.

This is the interactive mode. That's all we have for now,
so just follow along.
""")


def prompt(prompt="Press enter to continue"):
    return raw_input("{} --> ".format(prompt))


def get_challenge_meta():
    # ask for slug,
    slug = prompt("Challenge slug")
    #title,
    title = prompt("Challenge title")
    #blurb,
    blurb = prompt("Challenge blurb")
    #description,
    description = prompt("Challenge description")
    #help,
    help = prompt("Challenge help")
    #instruction,
    instruction = prompt("Challenge instruction")
    #difficulty
    difficulty = prompt("Challenge difficulty (1,2,3)")


def create_challenge():
    pass


def main():
    interactive = True
    servers = {
        "local": "http://localhost:5000/",
        "dev": "http://dev.maproulette.org/",
        "prod": "http://maproulette.org/"
    }

    if interactive:
        # display help text
        display_help_text()
        prompt()
        is_new = prompt("Will this be a new (n) or an existing (e) challenge?")

        if is_new == "n":
            # if new ask for slug, title, blurb, description, help, instruction, difficulty
            get_challenge_meta()
            # then create challenge
            create_challenge()


if __name__ == '__main__':
    main()

# overpass query
# summary results
# post
# result + link to challenge
