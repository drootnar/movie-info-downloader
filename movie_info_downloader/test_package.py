import pytest
import requests
import asyncio
from . import get_latest_movies, get_movies_from_rss, download_movie, MovieInfoError


class FakeResponse(object):
    def __init__(self, type_of_response):
        with open('movie_info_downloader/tests/{}.xml'.format(type_of_response), 'r') as xml_file:
                self.text = xml_file.read().replace('\n', '')
        self.status_code = 200

def fake_response(type_of_response):
        return FakeResponse(type_of_response)


def test_get_movies_from_rss(monkeypatch):
    monkeypatch.setattr(requests, 'get', fake_response)

    # file is corrupted so there is no movie proposals
    with pytest.raises(MovieInfoError) as excinfo:
        get_movies_from_rss('corrupted')

    # another version of corrupted file
    with pytest.raises(MovieInfoError) as excinfo:
        get_movies_from_rss('no_title_in_one_item')

    # file is correct now
    movies = list(get_movies_from_rss('correct'))
    assert len(movies) == 4
    assert movies[0][0] == 'Batman'
    assert movies[1][0] == "Hitman 2016"
    assert len(movies[2]) == 3  # can't recognize title so more proposals included
    assert movies[2][0] == "Hobbit mkv edited"
    assert len(movies[2][1].split()) > len(movies[2][2].split())
    assert movies[3][0] == "Hobbit2 2016"

def test_download_from_imdb(monkeypatch):
    monkeypatch.setattr(requests, 'get', fake_response)
    movies = get_movies_from_rss('correct')
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(download_movie(movies))
    assert len(result) == 4
    assert 'Batman' in result
    batman_movie = result['Batman']
    assert batman_movie['title'] == 'Batman'
    assert batman_movie['rating'] == 7.6
    assert 'genres' in batman_movie
    assert len(batman_movie['genres']) == 2