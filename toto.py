#!/usr/bin/env python3
# toto.py
# Adds the ID line to directory files using git metadata.
#
# Author:   Rebecca Bilbro
# Created:  Sun Aug 11 11:27:57 EDT 2019
#

"""
Scans local directory for git repository metadata and adds ID line to file headers.
"""

##########################################################################
## Imports
##########################################################################

import re
import os
import sys
import git
import argparse
import fileinput

##########################################################################
## Command Line Interface
##########################################################################

DESCRIPTION = "Writes commit ID to headers of files in local git repository."

ARGUMENTS = {
    ("-o", "--output"): {
        "metavar": "PATH",
        "default": sys.stdout,
        "type": argparse.FileType("w"),
        "help": "path to write out data to (stdout by default)",
    },
    ("-b", "--branch"): {
        "default": "master",
        "help": "the branch to list commits from",
    },
    ("-m", "--modify"): {
        "action": "store_true",
        "default": True,
        "help": "modify files in place to reset their versions",
    },
    "-n": {
        "metavar": "NUM",
        "dest": "num_lines",
        "type": int,
        "default": 10,
        "help": "maximum number of header lines to search through.",
    },
    "repo": {
        "nargs": "?",
        "default": os.getcwd(),
        "help": "path to repository to add copyright information",
    },
}

##########################################################################
## ID Extraction and File Modification
##########################################################################

IDRE = re.compile(
    r"^#\s*ID:\s+([\w\.\-]+)\s+\[([\s\S])*\]\s+([\w\@\.\+\-]*)\s+\$\s*$", re.I
)


def versionize(args):
    """
    Primary utility for performing the versionization.
    """
    try:
        path = os.path.abspath(args.repo)

        if not os.path.isdir(path):
            raise Exception("'{}' is not a directory!".format(args.repo))

        repo = git.Repo(path)
    except git.InvalidGitRepositoryError:
        raise Exception("'{}' is not a Git repository!".format(args.repo))

    # Construct the path version tree.
    versions = {}
    for commit in repo.iter_commits(args.branch):
        for blob in commit.tree.traverse():
            versions[blob.abspath] = commit

    # Track required modifications
    output = []

    # Walk the directory path
    for root, dirs, files in os.walk(path):

        # Ignore hidden directories (.git)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for name in files:
            name = os.path.join(root, name)
            if name not in versions:
                continue

            # Ignore non-python files
            if not name.endswith(".py"):
                continue

            try:
                output.append(read_head(name, versions[name], maxlines=args.num_lines))
            except Exception as e:
                raise Exception("could not read head of {}: {}".format(name, e))

    # Remove any matched files.
    output = filter(None, output)

    # Make the modifications if the args specifies to
    if args.modify:
        for path in output:
            modify_inplace(path)

    # Return the output
    return (
        ["{}".format(path) for path in output]
        if output
        else ["No files require ID header."]
    )


def read_head(path, commit, maxlines=None):
    """
    Reads the first maxlines of the file (or all lines if None) and looks
    for the copyright string. If it does not exist, return the path for
    that file.
    """

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f.readlines()):
            if maxlines and idx >= maxlines:
                break
            match = IDRE.match(line)
            if match:
                vers = "# ID: {} [{}] {} $".format(
                    os.path.basename(path), commit.hexsha[:7], commit.author.email
                )
                return path, vers


def modify_inplace(path):
    """
    Modifies the copyright line by writing all lines except the match line.
    """
    end = False
    for line in fileinput.input(path[0], inplace=1):
        match = IDRE.match(line)
        if not end and match:
            end = True
            sys.stdout.write(path[1] + "\n")
        else:
            sys.stdout.write(line)


if __name__ == "__main__":

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    # Add the arguments from the definition above
    for keys, kwargs in ARGUMENTS.items():
        if not isinstance(keys, tuple):
            keys = (keys,)
        parser.add_argument(*keys, **kwargs)

    # Handle the input from the command line
    args = parser.parse_args()
    output = list(versionize(args))
    args.output.write("\n".join(output) + "\n")

    # Exit successfully
    parser.exit(0)
