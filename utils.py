import json
import os
import requests
from functools import reduce
from bs4 import BeautifulSoup
import uuid
import base64


def make_soup(text):
    return BeautifulSoup(text, 'html.parser')


def save_json(json_data, file_name):
    with open(file_name, 'w') as f:
        json.dump(json_data, f)
        f.close()


def load_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)

def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def download_image(meta):
    """
    :param image_meta: { 'url': '', 'path': '', 'file_name': 'full file path w/0 extension' }
    """
    url = meta['url']
    file_path = meta['path']
    file_name = meta['file_name']
    if os.path.exists(file_path + file_name + '.jpg'):
        return

    with open(file_path + file_name + '.jpg', 'wb') as handle:
        response = requests.get(url, stream=True)
        if not response.ok:
            print(response)
        for block in response.iter_content(1024):
            if not block:
                break
            handle.write(block)

    print("Image Saved:", file_name)


def download_pdf(meta):
    """
    :param image_meta: { 'url': '', 'path': '', 'file_name': 'full file path w/0 extension' }
    """
    url = meta['url']
    file_path = meta['path']
    file_name = meta['file_name']
    if os.path.exists(file_path + file_name + '.pdf'):
        return
    try:
        with open(file_path + file_name + '.pdf', 'wb') as handle:
            response = requests.get(url, stream=True)
            if not response.ok:
                print(response)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

        print("\r\rPDF Saved:", file_name)
    except Exception:
        print('Error', url)


def safe_list_index(l, index):
    if index > len(l)-1:
        return ''
    else:
        return l[index]

def safe_list_obj_index(l, index):
    if index > len(l)-1:
        return {}
    else:
        return l[index]


def flatten_list(l):
    if len(l) == 0:
        return ''
    return reduce(lambda x, y: x + '^' + y, l)

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)

    # Print New Line on Complete
    if iteration == total:
        print()


def file_counter(path):
    path, dirs, files = next(os.walk(path))
    return len(files)


def mock_response(path):
    with open(path, 'r') as f:
        return f.read()


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]



def shorten_url(url):
    uuidstring = str(uuid.uuid5(uuid.NAMESPACE_DNS, url))
    return base64.encodebytes(uuid.UUID(uuidstring).bytes).decode("ascii").rstrip('=\n').replace('/', '_')



