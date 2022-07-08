import os
import requests
import argparse
from pathlib import Path
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
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


def download_image(url, filename, folder='covers/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = f'{folder}{filename}'
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_comments(comments, filename, folder='comments/'):
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = f'{folder}{filename}.txt'
    if comments:
        with open(filepath, 'w') as file:
            file.write('\n'.join(comments))


def print_info(header, genres):
    print('Заголовок:', header)
    print('Жанры:', genres)
    print()


def parse_book_page(soup):
    book_info = {}
    all_genres = soup.find('span', class_='d_book').find_all('a')
    only_text_genres = []
    for genre in all_genres:
        only_text_genres.append(genre.text)
    book_info['genres'] = ', '.join(only_text_genres)

    all_comments = soup.find_all('div', class_='texts')
    only_text_comments = []
    for comment in all_comments:
        only_text_comments.append(comment.text.split(')')[-1])
    book_info['comments'] = only_text_comments

    img_url = soup.find('div', class_='bookimage').find('img')['src']
    img_name = urlparse(img_url).path
    img_name = os.path.basename(img_name)
    img_name = unquote(img_name)
    img_url = urljoin('https://tululu.org/', img_url)
    book_info['img name'] = img_name
    book_info['img url'] = img_url

    header = soup.find('td', class_='ow_px_td').find('h1').text
    title, author = header.split('::')
    while not title[-1].isalnum():
        title = title[:-1]
    while not author[0].isalnum():
        author = author[1:]
    book_info['title'] = title
    book_info['author'] = author
    return book_info


path = Path.cwd() / 'books'
parser = argparse.ArgumentParser(description='Download books from tululu.org')
parser.add_argument('-s', '--start_id', help='id of the first book you want to download', type=int, default=1)
parser.add_argument('-e', '--end_id', help='id of the first book you want to download', type=int, default=11)
args = parser.parse_args()
for i in range(args.start_id, args.end_id):
    name_url = f'https://tululu.org/b{i}/'
    response = requests.get(name_url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        book_info = parse_book_page(soup)
        title, author, img_url, img_name, genres, comments = book_info['title'], book_info['author'], book_info['img url'], book_info['img name'], book_info['genres'], book_info['comments']
        filename = f'{title} - {author}'
        download_txt(f'https://tululu.org/txt.php?id={i}', f'{i}. {filename}')
        download_image(img_url, img_name)
        download_comments(comments, f'{i}. {filename}')
        print_info(filename, genres)
    except requests.HTTPError:
        pass


