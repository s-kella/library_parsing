import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def on_reload():
    rendered_page = template.render(
        books=books_for_rendering)
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('template.html')

with open("books.json", "r", encoding="utf8") as books_file:
    books = books_file.read()
books = json.loads(books)
books_for_rendering = []
for book in books:
    books_for_rendering.append({'author': book['author'],
                                'title': book['title'],
                                'pic': os.path.join('covers', book['img name'])})
on_reload()

server = Server()
server.watch('template.html', on_reload)
server.serve(root='.')

