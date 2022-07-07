# -*- coding: cp1251 -*-
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import lxml
import os


def check_for_redirect(response):
    print(response.url)
    if response.url == 'https://tululu.org/':
        print(8)
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = f'{folder}{filename}.txt'
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


path = Path.cwd() / 'books'

for i in range(1, 11):
    name_url = f'https://tululu.org/b{i}/'
    response = requests.get(name_url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        header = soup.find('td', class_='ow_px_td').find('h1').text
        title, author = header.split('::')
        while not title[-1].isalnum():
            title = title[:-1]
        while not author[0].isalnum():
            author = author[1:]
        filename = f'{i}.{title} - {author}'
        download_txt(f'https://tululu.org/txt.php?id={i}', filename)
    except requests.HTTPError:
        pass


