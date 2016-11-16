import re
import requests
import asyncio
import aiohttp
import json
import xml.etree.ElementTree as etree
from six.moves.urllib.parse import urlencode


__all__ = ['get_latest_movies']

SEARCH_BASE_URL = "http://www.imdb.com/xml/find?"
DETAIL_BASE_URL = "https://app.imdb.com/title/maindetails?"

class MovieInfoError(Exception):

    def __init__(self, message=None):
        self.message = message if message else 'Undefined error'

    def __str__(self):
        return self.message


def get_movies_from_rss(link):
    ''' Parse rss to get title proposals'''

    def get_title_proposals(raw_title):
        ''' Return list of movie title proposals'''
        proposals = list()
        tokens = re.findall(r"[\w']+", raw_title)
        for i, token in enumerate(tokens):
            if len(token) == 4 and token.isdigit():
                proposals.append(" ".join(tokens[:i+1]))
                return proposals
        for i in range(len(tokens), 0, -1):
            proposals.append(" ".join(tokens[:i+1]))
        return proposals

    response = requests.get(link)
    if response.status_code != 200:
        raise MovieInfoError('Download rss file failed')
    try:
        channel = etree.fromstring(response.text.encode('utf-8'))[0]
    except KeyError:
        raise MovieInfoError('Structure of rss file corrupted')
    try:
        raw_titles = [item.findall('title')[0].text for item in channel.findall('item')]
    except IndexError:
        raise MovieInfoError('Structure of rss file corrupted')
    if not raw_titles:
        raise MovieInfoError('No movies found in rss file')
    return map(get_title_proposals, raw_titles)


async def find_movie(proposals):

    async def movie_id_query(proposal):
        '''Return dict with movie data or None'''
        default_search_for_title_params = {
            'json': '1',
            'nr': 1,
            'tt': 'on',
            'q': proposal
        }
        query_params = urlencode(default_search_for_title_params)
        url = "{}{}".format(SEARCH_BASE_URL, query_params)
        movie_id = None
        async with aiohttp.get(url) as _resp:
            data = await _resp.read()
            try:
                data_json = json.loads(data.decode('utf-8'))
                if 'title_popular' in data_json and len(data_json['title_popular']):
                    movie_id = data_json['title_popular'][0]['id']
                elif 'title_approx' in data_json and len(data_json['title_approx']):
                    movie_id = data_json['title_approx'][0]['id']
            except (json.decoder.JSONDecodeError, IndexError):
                movie_id = None
        if movie_id:
            params = {'tconst': movie_id}
            url = "{}{}".format(DETAIL_BASE_URL, urlencode(params))
            async with aiohttp.get(url) as _resp:
                data = await _resp.read()
                try:
                    return json.loads(data.decode('utf-8'))['data']
                except (json.decoder.JSONDecodeError, IndexError):
                    return None
        return None

    results, _ = await asyncio.wait([movie_id_query(proposal) for proposal in proposals])
    for movie_proposal in results:
        movie_data = movie_proposal.result()
        if movie_data:
            return {movie_data['title']: movie_data}
    return {}


async def download_movie(proposals_list):
    movies, _ = await asyncio.wait([find_movie(proposals) for proposals in proposals_list])
    _return = {}
    for movie in movies:
        _return.update(movie.result())
    return _return



def get_latest_movies(link='https://yourbittorrent.com/movies/rss.xml'):
    titles_proposals = get_movies_from_rss(link)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(download_movie(titles_proposals))
    return result
