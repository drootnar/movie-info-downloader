Simple tool to download info about new movies on torrents (list taken from rss file).

Expose get_latest_movies() which parse rss file with newest torret movies and check the info in imdb service.
Return dict with titles as keys and dict with movie info as values.

Usage
-----
1. In your project install package: pip install movie_info_downloader
2. Usage:
```
from movie_info_downloader import get_latest_movies()

movies = get_lates_movies()
for movie in movies:
    print(movie)
    
>> ['Batman', 'Hobbit']
```

Installation for development
----------------------------
1. Clone repo
2. Create virtual environment via virtualenvironment: virtualenv -p <python3.5 path> env
3. Enable virtual environment: source env/bin/activate
3. Install packages: pip install -r requirements.txt
4
