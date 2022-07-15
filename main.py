import os
import requests
import argparse
import time
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def download_txt(url, params, filename, folder='books'):
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, f'{filename}.txt')
    with open(filepath, 'w') as file:
        file.write(response.text)


def download_image(url, filename, folder='covers'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, f'{filename}')
    with open(filepath, 'wb') as file:
        file.write(response.content)


def save_comments(comments, filename, folder='comments'):
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, f'{filename}.txt')
    if comments:
        with open(filepath, 'w') as file:
            file.write('\n'.join(comments))


def print_info(header, genres):
    print('Заголовок:', header)
    print('Жанры:', genres)
    print()


def parse_book_page(soup, book_url):
    all_genres = soup.find('span', class_='d_book').find_all('a')
    genres_only_text = [genre.text for genre in all_genres]
    book = {'genres': ', '.join(genres_only_text)}

    all_comments = soup.find_all('div', class_='texts')
    comments_only_text = [comment.text.split(')')[-1] for comment in all_comments]
    book['comments'] = comments_only_text

    img_url = soup.find('div', class_='bookimage').find('img')['src']
    img_name = urlparse(img_url).path
    img_name = os.path.basename(img_name)
    img_name = unquote(img_name)
    img_url = urljoin(book_url, img_url)
    book['img name'] = img_name
    book['img url'] = img_url

    header = soup.find('td', class_='ow_px_td').find('h1').text
    title, author = header.split('::')
    title = title.replace('/xa0', '').strip()
    author = author.replace('/xa0', '').strip()
    book['title'] = title
    book['author'] = author
    return book


def main():
    parser = argparse.ArgumentParser(description='Download books from tululu.org')
    parser.add_argument('-s', '--start_id', help='id of the first book you want to download', type=int, default=1)
    parser.add_argument('-e', '--end_id', help='id of the last book you want to download', type=int, default=11)
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        book_url = f'https://tululu.org/b{book_id}/'
        while True:
            try:
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(soup, book_url)
                filename = f'{book["title"]} - {book["author"]}'
                params = {'id': book_id}
                download_txt(f'https://tululu.org/txt.php', params, f'{book_id}. {filename}')
                download_image(book['img url'], book['img name'])
                save_comments(book['comments'], f'{book_id}. {filename}')
                print_info(filename, book['genres'])
                break
            except requests.HTTPError:
                print(f'Invalid URL for book {book_id}\n')
                break
            except requests.exceptions.ConnectionError:
                print('No internet connection', book_id)
                time.sleep(5)
                continue


if __name__ == '__main__':
    main()

