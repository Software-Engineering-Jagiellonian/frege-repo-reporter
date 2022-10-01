from collections import defaultdict
from typing import Tuple

from database import db
from message_queue import messenger

ID_TO_LANGUAGE_NAME = {
    1: 'C',
    2: 'C++',
    3: 'C#',
    4: 'CSS',
    5: 'Java',
    6: 'JS',
    7: 'PHP',
    8: 'Python',
    9: 'Ruby',
}


def get_metrics(repo_id: str, commits: Tuple[str], languages: Tuple[int], get_currently_available: bool):
    if not db.check_repo_download_time(repo_id):
        analyzed_commits = db.get_analyzed_commits(repo_id, languages)
        commits_to_analyze = list(set(commits).difference(analyzed_commits))
        message_to_queue = {'repo_id': repo_id, 'languages': languages, 'commits': commits_to_analyze}

        messenger.send_message_to_downloader(message=message_to_queue)

    if not get_currently_available:
        all_metrics_analyzed, present_metrics, analyzed_metrics = db.get_metrics_analysis_info(repo_id, commits)
        if present_metrics == 0:
            return "Analysis just started. Try again in a few seconds. Note: If there will be no results after several" \
                   f" attempts, there is a chance that there are no files to analyze for provided commits", 404
        if not all_metrics_analyzed:
            return f"{present_metrics - analyzed_metrics} metrics not fully analyzed yet. Current progress: " \
                   f"{analyzed_metrics}/{present_metrics}. Try again in a few seconds.", 404

    return _map_metrics(db.get_metrics(repo_id, commits, languages))


def _map_metrics(raw_metrics: list) -> dict:
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(defaultdict)))

    for commit_hash, file_path, language_id, h1, h2, n1, n2, vocabulary, length, calculated_length, volume, \
        difficulty, effort, time, bugs, loc, lloc, sloc, comments, multi, blank, single_comments, score, rank, \
        *unrecognized \
            in raw_metrics:
        language_name = ID_TO_LANGUAGE_NAME[language_id]

        result[commit_hash][language_name][file_path]['h1'] = h1
        result[commit_hash][language_name][file_path]['h2'] = h2
        result[commit_hash][language_name][file_path]['n1'] = n1
        result[commit_hash][language_name][file_path]['n2'] = n2
        result[commit_hash][language_name][file_path]['vocabulary'] = vocabulary
        result[commit_hash][language_name][file_path]['length'] = length
        result[commit_hash][language_name][file_path]['calculated_length'] = calculated_length
        result[commit_hash][language_name][file_path]['volume'] = volume
        result[commit_hash][language_name][file_path]['difficulty'] = difficulty
        result[commit_hash][language_name][file_path]['effort'] = effort
        result[commit_hash][language_name][file_path]['time'] = time
        result[commit_hash][language_name][file_path]['bugs'] = bugs
        result[commit_hash][language_name][file_path]['loc'] = loc
        result[commit_hash][language_name][file_path]['lloc'] = lloc
        result[commit_hash][language_name][file_path]['sloc'] = sloc
        result[commit_hash][language_name][file_path]['comments'] = comments
        result[commit_hash][language_name][file_path]['multi'] = multi
        result[commit_hash][language_name][file_path]['blank'] = blank
        result[commit_hash][language_name][file_path]['single_comments'] = single_comments
        result[commit_hash][language_name][file_path]['score'] = score
        result[commit_hash][language_name][file_path]['rank'] = rank
        if unrecognized:
            result[commit_hash][language_name][file_path]['unrecognized_metrics'] = unrecognized

    return result
