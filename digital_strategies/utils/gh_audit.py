#!/usr/bin/env python3

# Reports active GitHub repositories with open issues.
# Requires PyGithub

import argparse

from github import Auth, Github

def main(pat):
    auth = Auth.Token(pat)
    g = Github(auth=auth)
    for repo in g.get_organization('RockefellerArchiveCenter').get_repos():
        if (not repo.archived) and (repo.open_issues_count):
            print(repo.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reports active GitHub repositories with open issues.')
    parser.add_argument('pat')

    args = parser.parse_args()
    main(args.pat)