from typing import Tuple

import psycopg2

from config import DB_HOST, DB_NAME, DB_PORT, DB_PASS, DB_USER

query_metrics = """SELECT commit_hash, file_path, language_id, h1, h2, n1, 
            n2, vocabulary, length, calculated_length, volume, difficulty, effort, time, bugs, loc, lloc, sloc, 
            comments, multi, blank, single_comments, score, rank
                    FROM python_file_halstead_metrics hm
                        JOIN python_file_loc_metrics lm ON hm.python_file_id=lm.python_file_id
                        JOIN python_file_mi_metrics mm ON hm.python_file_id=mm.python_file_id
                        JOIN python_file pf ON hm.python_file_id = pf.id
                        JOIN repository_language_file rlf on pf.file_id = rlf.id
                        JOIN repository_language rl on rlf.repository_language_id = rl.id
                        WHERE repository_id=%s AND commit_hash IN %s AND language_id IN %s"""

query_metrics_analyzed = """SELECT COUNT(*) FROM repository_language
                        WHERE repository_id=%s AND commit_hash IN %s AND present=true AND analyzed=true"""

query_metrics_present = """SELECT COUNT(*) FROM repository_language
                        WHERE repository_id=%s AND commit_hash IN %s AND present=true"""

query_get_repo_download_time = """SELECT download_time FROM repositories WHERE repo_id=%s"""

query_insert_repo = """INSERT INTO repositories VALUES (%s, %s, %s, null) ON CONFLICT DO NOTHING"""

query_get_analyzed_commits = """SELECT DISTINCT commit_hash FROM repository_language WHERE repository_id=%s AND 
                        language_id IN %s AND analyzed=true"""


def _connect():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)


def get_metrics(repo_id: str, commits: Tuple[str], languages: Tuple[int]):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_metrics, [repo_id, commits, languages])
            return cur.fetchall()


def get_metrics_analysis_info(repo_id: str, commits: Tuple[str]) -> Tuple[bool, int, int]:
    """
    :return: Tuple of (bool, int, int) which corresponds to (if all metrics analyzed, present_metrics, analyzed_metrics)
    """
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_metrics_analyzed, [repo_id, commits])
            analyzed = cur.fetchone()[0]

            cur.execute(query_metrics_present, [repo_id, commits])
            present = cur.fetchone()[0]
            return present == 0 or present - analyzed == 0, present, analyzed


def check_repo_download_time(repo_id: str) -> bool:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_get_repo_download_time, [repo_id])
            return cur.fetchone()[0]


def insert_repo_to_repositories_if_not_exists(repo_id: str, git_url: str, repo_url: str):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_insert_repo, [repo_id, git_url, repo_url])


def get_analyzed_commits(repo_id, languages):
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query_get_analyzed_commits, [repo_id, languages])
            return {row[0] for row in cur.fetchall()}
