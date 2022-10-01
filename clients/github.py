from collections import defaultdict

import requests

_GITHUB_HOST = "https://api.github.com"


def _get_repository_statistics(repository_name: str):
    return requests.get(f"{_GITHUB_HOST}/repos/{repository_name}").json()


def _get_repository_languages(repository_name: str):
    return requests.get(f"{_GITHUB_HOST}/repos/{repository_name}/languages").json()


def _get_repository_commits(repository_name: str):
    return requests.get(f"{_GITHUB_HOST}/repos/{repository_name}/commits").json()


def _get_repository_branches(repository_name: str):
    return requests.get(f"{_GITHUB_HOST}/repos/{repository_name}/branches").json()


def _compute_language_percentages(language_statistics: dict):
    values = language_statistics.values()
    values_sum = sum(values)

    return {language_name: round(value * 100 / values_sum, 2) for language_name, value in language_statistics.items()}


def get_repository(repo_id: str):
    branches_raw = _get_repository_branches(repo_id)
    commits_raw = _get_repository_commits(repo_id)
    repository_statistics = _get_repository_statistics(repo_id)
    languages = _compute_language_percentages(_get_repository_languages(repo_id))

    branch_to_commits = defaultdict(list)
    commit_sha_to_branch_names = {}

    for branch_raw in branches_raw:
        commit_sha_to_branch_names[branch_raw['commit']['sha']] = [branch_raw['name']]

    for commit_raw in commits_raw:
        current_commit_sha = commit_raw['sha']

        for branch_name in commit_sha_to_branch_names[current_commit_sha]:
            if branch_name not in branch_to_commits:
                branch_to_commits[branch_name] = [commit_raw]
            else:
                branch_to_commits[branch_name].append(commit_raw)

        parents_sha = commit_raw['parents']
        if parents_sha is None:
            continue

        for parent_sha in parents_sha:
            sha = parent_sha['sha']
            branch_names = commit_sha_to_branch_names[current_commit_sha]

            if sha not in commit_sha_to_branch_names:
                commit_sha_to_branch_names[sha] = list(branch_names)
            else:
                commit_sha_to_branch_names[sha].extend(branch_names)

    branches = []
    for (branch_name, commits_raw) in branch_to_commits.items():
        commits = []
        for c_raw in commits_raw:
            commit = c_raw['commit']
            commits.append({
                'author': commit['author'],
                'message': commit['message'],
                'date': commit['author']['date'],
                'sha': c_raw['sha'],
                'parents': c_raw['parents']
            }
            )
        branches.append({'name': branch_name, 'commits': commits})

    return {
        'repo_id': repo_id,
        'languages': languages,
        'branches': branches,
        'repositoryStatistics': repository_statistics
    }
