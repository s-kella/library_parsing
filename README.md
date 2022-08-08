# library_parsing

Download books from the online-library [tululu.org](https://tululu.org/). Download the text of the book, and cover, and create a file with descriptions of the all downloaded books (title, author, genres, comments from tululu.org).

### How to install:

Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

### Options:

`-s` `--start_page` - first page you want to download. <br />
`-e` `--end_page` - last page you want to download. <br />
`-d` `--dest_folder` - the path to the directory with the parsing results: pictures, books, JSON. <br />
`-si` `--skip_imgs` - do not download images. <br />
`-st` `--skip_txt` - do not download books.

### Project Goals:

The code is written for educational purposes.
