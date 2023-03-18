# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 17:10:05 2023

@author: juanh
"""

import requests
import os
import time

# MAIN_DOMAINs
MAIN_DOMAIN = "https://a.4cdn.org"
ATTACHMENTE_DOMAIN = "https://i.4cdn.org"

# End points
BOARDS = f"{MAIN_DOMAIN}/boards.json"
THREADS_LIST = f"{MAIN_DOMAIN}/board/threads.json"
CATALOG = f"{MAIN_DOMAIN}/board/catalog.json"
ARCHIVE = f"{MAIN_DOMAIN}/board/archive.json"
INDEXES = f"{MAIN_DOMAIN}/board/page.json"
THREAD = f"{MAIN_DOMAIN}/board/thread/no.json"
IMAGE = f"{ATTACHMENTE_DOMAIN}/board/tim.extension"


def make_request(url, **kwargs):
    first_time = True
    while True:
        try:
            if not first_time:
                print(f"Reintentando conexión con {url}")

            r = requests.get(url, **kwargs)

            if not first_time:
                print(f"Conexión exitosa a {url}")
            return r

        except requests.ConnectionError:
            print(f"Error al conectar con {url}. Renintentando en 5 segundos")
            time.sleep(5)
            first_time = False


def exists_thread_by_id(board, thread_id):
    """
    Parameters
    ----------
    board : TYPE
        DESCRIPTION.
    thread_id : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        Test is a thread with id thread_id is reachale.

    """
    r = make_request(THREAD.replace("board", board).replace("no", thread_id))
    if r.status_code == requests.codes.ok:
        return r

    return None


def exists_board_by_id(board):
    r = make_request(CATALOG.replace("board", board))
    return True if r.status_code == requests.codes.ok else False


def has_attachment(post):
    """
    Test if a json post contains an attachment.

    Parameters
    ----------
    post : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return True if "tim" in post else False


def download_attachment(board, post, path='.'):
    """
    Download attachment from a post.

    Parameters
    ----------
    board : TYPE
        DESCRIPTION.
    post : TYPE
        DESCRIPTION.
    path : TYPE, optional
        DESCRIPTION. The default is '.'.

    Returns
    -------
    None.

    """
    tim = post['tim']
    ext = post['ext']
    no = post['no']
    filename = post['filename']
    r = make_request(f"{ATTACHMENTE_DOMAIN}/{board}/{tim}{ext}", stream=True)
    if r.status_code == requests.codes.ok:
        with open(os.path.join(path, f"{no} - {filename}{ext}"),
                  'wb') as attachment:
            for chunk in r.iter_content(chunk_size=1024):
                attachment.write(chunk)

    else:
        print(f"Error al descargar {tim} en post {post}")


def get_thread_by_id(board, thread_id):
    """
    Returns json representation of a thread in board

    Parameters
    ----------
    board : TYPE
        DESCRIPTION.
    thread_id : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return make_request(
        THREAD.replace("board", board).replace("no", thread_id)
        ).json()


def get_catalog_by_broad(broad):
    return make_request(CATALOG.replace("broad", broad)).json()


def get_threads_by_keywords(board, keyboards=()):
    """
    Returns a set of threads that contains keywords in subject or comment.

    Parameters
    ----------
    board : TYPE
        DESCRIPTION.
    keyboards : TYPE, optional
        DESCRIPTION. The default is ().

    Returns
    -------
    TYPE
        DESCRIPTION

    """

    threads = set()

    catalog = make_request(CATALOG.replace("board", board))
    if catalog.status_code == requests.codes.ok:
        # List of threads
        catalog_json = catalog.json()

        for page in catalog_json:
            for thread in page['threads']:
                s = thread['sub'].lower() if 'sub' in thread else ''
                c = thread['com'].lower() if 'com' in thread else ''
                for keyword in keyboards:
                    k = keyword.lower()
                    if k in s or k in c:
                        threads.add(str(thread['no']))
                        break

    else:
        print(f"Something went wrong trying to get catalog from board {board}")

    return threads


def download_thread(board, thread_id, path='.', start_from=0, wait=2):
    thread = make_request(
        THREAD.replace("board", board).replace("no", thread_id)
        )
    if thread.status_code == requests.codes.ok:
        final_path = os.path.join(path, '.'+thread_id)
        wait = wait if wait < 2 else 2
        if not os.path.exists(final_path):
            os.mkdir(final_path)

        posts = thread.json()['posts']
        for i in range(start_from, len(posts)):
            if has_attachment(posts[i]):
                download_attachment(board, posts[i], final_path)
                time.sleep(wait)

    else:
        raise Exception("""Al descargar el hilo con id {thread_id} se obtuvo el codigo \
                        {thread.status_code}""")

    return thread_id


def track_thread(board, thread_id, path='.', update_time=15):
    print(f"Tracking thread {thread_id}")
    last_post_index = 0
    # stupid off by one bug. Fix by setting last_time to epoch
    # Thursday, 1 January 1970 0:00:00
    # Thu, 01 Jan 1970 00:00:00 GMT
    thread = make_request(
        THREAD.replace("board", board).replace("no", thread_id)
        )
    while True:
        if thread.status_code == requests.codes.not_found:
            raise Exception(f"""Thread {thread_id} does not \
                ¸exist or has been deleted""")

        posts_nuevos = len(thread.json()['posts']) - last_post_index
        print(f""""Hilo {thread_id}: Hay \
            {posts_nuevos} posts nuevos""")
        download_thread(
            board, thread_id,
            path=path,
            start_from=last_post_index
            )
        last_time = {'If-Modified-Since': thread.headers['Last-Modified']}
        last_post_index = len(thread.json()['posts'])
        if posts_nuevos < 1:
            # Se intenta corregir en caso de que se hayan borrado posts
            last_post_index = last_post_index - posts_nuevos
        while True:
            thread = make_request(
                THREAD.replace("board", board).replace("no", thread_id),
                headers=last_time
                )
            if thread.status_code == requests.codes.not_modified:
                time.sleep(update_time)
                continue

            break
