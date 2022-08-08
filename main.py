import os
import json
import requests
import argparse
import time
import parse_tululu_category
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def download_txt(url, params, filename, path):
    filename = sanitize_filename(filename)
    response = requests.get(url, params=params)
    response.raise_for_status()

    folder = 'books'
    full_path = os.path.join(path, folder)
    os.makedirs(full_path, exist_ok=True)
    check_for_redirect(response)
    filepath = os.path.join(full_path, f'{filename}.txt')
    with open(filepath, 'w') as file:
        file.write(response.text)


def download_image(url, filename, path):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    folder = 'covers'
    full_path = os.path.join(path, folder)
    os.makedirs(full_path, exist_ok=True)
    filepath = os.path.join(full_path, filename)
    print(filepath)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def print_info(header, genres):
    print('Заголовок:', header)
    print('Жанры:', genres)
    print()


def parse_book_page(soup, book_url):
    genres_selector = 'span.d_book a'
    all_genres = soup.select(genres_selector)
    genres_only_text = [genre.text for genre in all_genres]

    comments_selector = 'div.texts'
    all_comments = soup.select(comments_selector)
    comments_only_text = [comment.text.split(')')[-1] for comment in all_comments]

    img_selector = 'div.bookimage img'
    img_url = soup.select_one(img_selector)['src']
    img_name = urlparse(img_url).path
    img_name = os.path.basename(img_name)
    img_name = unquote(img_name)
    img_url = urljoin(book_url, img_url)

    header_selector = 'td.ow_px_td h1'
    header = soup.select_one(header_selector).text
    title, author = header.split('::')
    title = title.replace('/xa0', '').strip()
    author = author.replace('/xa0', '').strip()

    book = {'title': title,
            'author': author,
            'img url': img_url,
            'genres': ', '.join(genres_only_text),
            'comments': comments_only_text,
            'img name': img_name
            }
    return book


def add_info_to_json(books, path):
    filepath = os.path.join(path, 'books.json')
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(books, file, sort_keys=True, indent=4, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Download books from tululu.org')
    parser.add_argument('-s', '--start_page', help='id of the first book you want to download.', type=int, default=1)
    parser.add_argument('-e', '--end_page', help='id of the last book you want to download.', type=int, default=1)
    parser.add_argument('-d', '--dest_folder', help='the path to the directory with the parsing results: pictures, books, JSON.')
    args = parser.parse_args()
    book_links = parse_tululu_category.parse_pages(start_page=args.start_page, end_page=args.end_page)
    books = []
    for link in book_links:
        book_id = link.split('/b')[-1].strip('/')
        while True:
            try:
                response = requests.get(link)
                response.raise_for_status()
                check_for_redirect(response)
                soup = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(soup, link)
                filename = f'{book["title"]} - {book["author"]}'
                params = {'id': book_id}
                download_txt(f'https://tululu.org/txt.php', params, f'{book_id}. {filename}', args.dest_folder if args.dest_folder else os.getcwd())
                download_image(book['img url'], book['img name'], args.dest_folder if args.dest_folder else os.getcwd())
                books.append(book)
                print_info(filename, book['genres'])
                break
            except requests.HTTPError:
                print(f'Invalid URL for book {book_id}\n')
                break
            except requests.exceptions.ConnectionError:
                print('No internet connection', link)
                time.sleep(5)
                continue
    add_info_to_json(books, args.dest_folder if args.dest_folder else os.getcwd())


if __name__ == '__main__':
    main()
