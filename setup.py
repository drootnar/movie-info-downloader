import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "movie_info_downloader",
    version = "0.0.4",
    author = "Kamil Rogalski",
    author_email = "drootnar@gmail.com",
    description = ("A simple package to get info from imdb about newest torrent movies using rss file"),
    license = "BSD",
    keywords = "torrent rss imdb",
    url = "http://packages.python.org/movie_info_downloader",
    packages=['movie_info_downloader'],
    long_description=read('README'),
    install_requires=[
        'requests',
        'asyncio',
        'aiohttp',
        'six'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)