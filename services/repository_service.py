from clients import github
from database import db

GITHUB_PREFIX = 'github.com/'


def get_repository(url: str):
    if 'github.com' in url:
        starting_index = url.index(GITHUB_PREFIX) + len(GITHUB_PREFIX)
        repo_id = url[starting_index:]
        git_url = url + ".git"
        db.insert_repo_to_repositories_if_not_exists(repo_id=repo_id, git_url=git_url, repo_url=url)
        return github.get_repository(repo_id)
    else:
        return 'Provided link is either incorrect or is not a GitHub repository link', 400
