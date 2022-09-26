import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    for i, page in enumerate(books_for_rendering):
        books = list(chunked(page, 2))
        rendered_page = template.render(books=books)
        page_path = os.path.join('pages', f'index{i}.html')
        with open(page_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


os.makedirs('pages', exist_ok=True)
env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml']))
template = env.get_template('template.html')

with open("books.json", "r", encoding="utf8") as books_file:
    books = books_file.read()
books = json.loads(books)
books_for_rendering = []
for book in books:
    books_for_rendering.append({'author': book['author'],
                                'title': book['title'],
                                'pic': os.path.join('../covers', book['img name']),
                                'path': os.path.join('../books', f'{book["filename"]}.txt')})
books_for_rendering = list(chunked(books_for_rendering, 10))
on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')

