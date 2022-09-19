import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open("books.json", "r", encoding="utf8") as books_file:
    books = books_file.read()
books = json.loads(books)

authors_n_names = []
for book in books:
    authors_n_names.append({'author': book['author'],
                            'title': book['title'],
                            'pic' : os.path.join('covers', book['img name'])})

rendered_page = template.render(
    authors_n_names=authors_n_names,
)

with open('index.html', 'w', encoding="utf8") as books_file:
    books_file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()