import json
import logging
from urllib.parse import urlencode
from multiprocessing import Pool

import requests
from bs4 import BeautifulSoup as soup


class PeopleAndMovies:
    BASE_URL = "http://www.imdb.com"
    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.5",
    }

    def __init__(self, list_page_url_start="/search/title", pages=20, params=None):
        self.cache = {}

        imdb_params = params if params else {
            "groups": "top_1000",
            "sort": "user_rating",
            "view": "simple",
        }
        list_page_url = f"{list_page_url_start}?{urlencode(imdb_params)}"

        # BUILDING LIST OF MOVIE URLS TO CRAWL...
        p = Pool(20)
        urls = p.map(self.parseUrls, [list_page_url + "&page=" + str(i) for i in range(1, pages + 1)])
        p.terminate()
        p.join()
        urls = [url for chunk in urls if chunk for url in chunk]

        # PARSING PEOPLE INFORMATION FROM MOVIE URLS...
        p = Pool(50)
        results = p.map(self.pageSummary, urls)
        p.terminate()
        p.join()
        results = [r for r in results if r]

        # INDEXING RESULTS...
        self.index(results)

    def pageSoup(self, page_url):
        try:
            r = requests.get(
                self.BASE_URL + page_url,
                headers=self.DEFAULT_HEADERS,
                timeout=10,
            )
            if r.status_code == 200:
                return soup(r.text, "html.parser")
        except requests.RequestException as e:
            logging.error("Failed to fetch %s: %s", page_url, e)
        return None

    def parseUrls(self, list_page_url):
        page_soup = self.pageSoup(list_page_url)
        if page_soup and "/search/title" in list_page_url:
            script = page_soup.find('script', id='__NEXT_DATA__')
            if script:
                try:
                    data = json.loads(script.string)
                    items = (
                        data["props"]["pageProps"]["searchResults"]["titleResults"]["titleListItems"]
                    )
                    return [f"/title/{item['titleId']}/" for item in items]
                except Exception as e:
                    logging.error("Failed to parse list page %s: %s", list_page_url, e)
        return []

    def pageSummary(self, page_url):
        page_soup = self.pageSoup(page_url)
        if not page_soup:
            return None
        script = page_soup.find('script', id='__NEXT_DATA__')
        if not script:
            return None
        try:
            data = json.loads(script.string)
            main = data['props']['pageProps']['mainColumnData']
            title = main['titleText']['text']

            def extract_people(section):
                if not section:
                    return []
                if isinstance(section, list):
                    people = []
                    for entry in section:
                        for cred in entry.get('credits', []):
                            name = cred.get('name', {}).get('nameText', {}).get('text')
                            if name:
                                people.append(name)
                    return people
                if isinstance(section, dict):
                    return [edge['node']['name']['nameText']['text'] for edge in section.get('edges', [])]
                return []

            directors = extract_people(main.get('directors'))
            creators = extract_people(main.get('creators'))
            actors = extract_people(main.get('cast'))

            return {title: {"directors": directors, "creators": creators, "actors": actors}}
        except Exception as e:
            logging.error("Failed to parse page %s: %s", page_url, e)
        return None

    def find(self, query):
        matches = []
        query_keywords = query.split(' ')
        for person_name in self.cache.keys():
            for name_token in person_name.split(' '):
                for keyword in query_keywords:
                    if name_token.lower().strip().startswith(keyword.strip()):
                        matches.append(json.dumps({person_name: self.cache[person_name]}))
                        break
        return matches

    def index(self, results):
        for page_summary in results:
            for title, people in page_summary.items():
                for role in people.keys():
                    for person in people[role]:
                        if person in self.cache:
                            if role in self.cache[person]:
                                self.cache[person][role].append(title)
                            else:
                                self.cache[person][role] = [title]
                        else:
                            self.cache[person] = {role: [title]}

    def search(self, person_name):
        results = self.find(person_name)
        return '[{}]'.format(','.join(results))
