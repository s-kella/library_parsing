import requests
from pathlib import Path


path = Path.cwd()/'books'

for i in range(1, 11):
    filename = f'{path}\id{i}.txt'
    url = f'https://tululu.org/txt.php?id={i}'
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'w') as file:
        file.write(response.text)
