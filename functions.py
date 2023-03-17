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
    r = requests.get(THREAD.replace("board", board).replace("no", thread_id))
    if r.status_code == requests.codes.ok:
        return r
    
    return None


def exists_board_by_id(board):
    r = requests.get(CATALOG.replace("board", board))
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
    r = requests.get(f"{ATTACHMENTE_DOMAIN}/{board}/{tim}{ext}", stream=True)
    if r.status_code == requests.codes.ok:
        print(f"\tPost {no}: Descargando {filename}{ext} - {tim}")
        with open(os.path.join(path, f"{no} - {filename}{ext}"), 'wb') as attachment:
            for chunk in r.iter_content(chunk_size=1024):
                attachment.write(chunk)

    else:
        print(f"Error al descargar {tim}")


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
    return requests.get(THREAD.replace("board", board).replace("no", thread_id)).json()


def get_catalog_by_broad(broad):
    return requests.get(CATALOG.replace("broad", broad)).json()


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
    
    catalog = requests.get(CATALOG.replace("board", board))
    if catalog.status_code == requests.codes.ok:
        # List of threads
        catalog_json = catalog.json()
        
        for page in catalog_json:
            for thread in page['threads']:
                s = thread['sub'].lower() if 'sub' in thread else ''
                c = thread['com'].lower() if 'com' in thread else ''
                for keyword in keyboards:
                    if keyword.lower() in s or keyword in c:
                        threads.add(str(thread['no']))
                        break
                    
    else:
        print(f"Something went wrong trying to get catalog from board {board}")
        
    return threads


def download_thread(board, thread_id, path='.', start_from=0, wait=2):
    final_path = os.path.join(path, '.'+thread_id)
    wait = wait if wait < 2 else 2
    if not os.path.exists(final_path):
        os.mkdir(final_path)
    
    primera_vez = True
    
    while True:
        try:
            if not primera_vez:
                print(f"Hilo {thread_id}: Reintentando conexion")
            thread = requests.get(THREAD.replace("board", board).replace("no", thread_id))
            if thread.status_code == requests.codes.ok:
                posts = thread.json()['posts']
                for i in range(start_from, len(posts)):
                    if has_attachment(posts[i]):
                        print(f"Hilo {thread_id}: posts {posts[i]['no']} tiene archivo adjunto")
                        download_attachment(board, posts[i], final_path)
                        time.sleep(wait)
        
            else:
                raise Exception("Al descargar el hilo con id {thread_id} se obtuvo el codigo {thread.status_code}")
            
            break
        
        except requests.ConnectionError as error:
            print(f"Hilo {thread_id}: Se llego al error: {error}")
            print("\tReintentando en 5 segundos")
            time.sleep(5)
            primera_vez = False
    return thread_id


def track_thread(board, thread_id, path='.', update_time=15):
    print(f"Tracking thread {thread_id}")
    last_post_index = 0
    update_time = update_time if update_time > 15 else 15
    # stupid off by one bug. Fix by setting last_time to epoch Thursday, 1 January 1970 0:00:00
    # Thu, 01 Jan 1970 00:00:00 GMT
    thread = requests.get(THREAD.replace("board", board).replace("no", thread_id))
    while True:
        if thread.status_code == requests.codes.not_found:
            raise Exception(f"Thread {thread_id} does not exist or has been deleted")
        
        print(f"Hilo {thread_id}: Hay {len(thread.json()['posts']) - last_post_index} posts nuevos")
        download_thread(board, thread_id, path=path, start_from=last_post_index)
        last_time = {'If-Modified-Since': thread.headers['Last-Modified']}
        last_post_index = len(thread.json()['posts'])
        while True:
            try:
                thread = requests.get(
                        THREAD.replace("board", board).replace("no", thread_id),
                        headers=last_time
                        )
                if thread.status_code == requests.codes.not_modified:
                    print(f"Hilo {thread_id}: No hay posts nuevos")
                    time.sleep(update_time)
                    continue
                
            except requests.ConnectionError as error:
                print(f"Ocurrio un error al monitorear hilo {thread_id}, retrying in 5 seconds")
                print(f"Error: {error}")
                time.sleep(5)
            
            break