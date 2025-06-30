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
        """Return list of people whose name tokens start with the query."""
        query_tokens = [q.lower() for q in query.split() if q]
        results = []
        for person, roles in self.cache.items():
            name_tokens = [t.lower() for t in person.split()]
            if any(nt.startswith(q) for q in query_tokens for nt in name_tokens):
                clean_roles = {
                    role: sorted(list(titles))
                    for role, titles in roles.items()
                    if titles
                }
                results.append({person: clean_roles})
        return results

    def index(self, results):
        """Build a cache mapping people to movies by role."""
        for page_summary in results:
            for title, people in page_summary.items():
                for role, persons in people.items():
                    for person in persons:
                        entry = self.cache.setdefault(
                            person,
                            {
                                "directors": set(),
                                "creators": set(),
                                "actors": set(),
                            },
                        )
                        entry[role].add(title)

    def search(self, person_name):
        """Return a JSON string for people whose name matches the query."""
        results = self.find(person_name)
        return json.dumps(results)
