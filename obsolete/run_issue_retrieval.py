from errata.utils.github_utils import *
import os

args = get_args()
cfg = config_parse(args.i)
gh_login, gh = github_connector(username=cfg.get('issues', 'gh_login'),
                                password=cfg.get('issues', 'gh_password'),
                                team=cfg.get('issues', 'gh_team'),
                                repo=cfg.get('issues', 'gh_repo'), cfg=cfg)

directory = args.issue
if not os.path.exists(directory):
    os.makedirs(directory)
# issues number returns the ordinal number for the next json & txt file.
issues_number = get_file_number(directory, extension='.json')
if args.id:
    for n in args.id:
        # Get issue number
        number = get_number(gh, n)
        # Get corresponding GitHub issue
        remote_issue = GitHubIssue(gh=gh,
                                   number=number)
        # Validate GitHub issue against JSON schema
        remote_issue.validate(action=args.command,
                              projects=get_projects(cfg))
        # Retrieve the corresponding GitHub issue
        remote_issue.retrieve(issue_f=open('{0}/issue{1}.json'.format(os.path.realpath(args.issue), issues_number)
                                           , 'w'),
                              dsets_f=open('{0}/datasets{1}.txt'.format(os.path.realpath(args.dsets), issues_number)
                                           , 'w'))
else:
    for issue in gh.iter_issues(state='all'):
        # Get corresponding GitHub issue
        remote_issue = GitHubIssue(gh=gh,
                                   number=get_number(gh, issue.number))
        # Validate GitHub issue against JSON schema
        remote_issue.validate(action=args.command,
                              projects=get_projects(cfg))
        dsets_number = get_file_number(directory, extension='.txt')

        # Retrieve the corresponding GitHub issue
        remote_issue.retrieve(issue_f=open('{0}/issue-{1}.json'.format(os.path.realpath(args.issue),
                                                                       issues_number), 'w'),
                              dsets_f=open('{0}/datasets-{1}.txt'.format(os.path.realpath(args.dsets),
                                                                      issues_number), 'w'))
