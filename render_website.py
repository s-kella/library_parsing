import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from functools import partial


def on_reload(books_for_rendering):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']))
    template = env.get_template('template.html')
    for i, page in enumerate(books_for_rendering):
        columns = 2
        books = list(chunked(page, columns))
        rendered_page = template.render(books=books, cur_page=i, pages=len(books_for_rendering))
        page_path = os.path.join('pages', f'index{i}.html')
        with open(page_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    os.makedirs('pages', exist_ok=True)
    with open('books.json', 'r', encoding='utf8') as books_file:
        books = json.load(books_file)
    books_for_rendering = [{'author': book['author'],
                            'title': book['title'],
                            'pic': f'../covers/{book["img name"]}',
                            'genres': book['genres'].split(', '),
                            'path': f'../books/{book["filename"]}.txt'}
                           for book in books]
    book_on_one_page = 10
    books_for_rendering = list(chunked(books_for_rendering, book_on_one_page))
    partial_on_reload = partial(on_reload, books_for_rendering)
    partial_on_reload()
    return partial_on_reload


if __name__ == '__main__':
    partial_on_reload = main()
    server = Server()
    server.watch('template.html', partial_on_reload)
    server.serve(root='.')
