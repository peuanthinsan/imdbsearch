import requests
import json
import logging
from urllib.parse import urlencode
from bs4 import BeautifulSoup as soup
from multiprocessing import Pool

import time

class PeopleAndMovies:

	BASE_URL = "http://www.imdb.com"

	def __init__(self, list_page_url_start="/search/title", pages=20, params={}):
		self.cache = {}

		imdb_params = params if params else {
			"groups": "top_1000",
			"sort": "user_rating",
			"view": "simple",
		}
		list_page_url = list_page_url_start + '?{}'.format(urlencode(imdb_params))

		"""BUILDING LIST OF MOVIE URLS TO CRAWL..."""
		# crawl list pages for list of movie_urls
		p = Pool(20)
		urls = p.map(self.parseUrls, [list_page_url + "&page=" + str(i) for i in range(1, pages + 1)])
		p.terminate()
		p.join()
		urls = [ url for chunk in urls for url in chunk ] if urls else []

		"""PARSING PEOPLE INFORMATION FROM MOVIE URLS..."""
		# extract people from urls as ({ movie: people })
		p = Pool(50)
		results = p.map(self.pageSummary, urls)
		p.terminate()
		p.join()

		"""INDEXING RESULTS..."""
		# index results by person_name as ({ person: movies })
		self.index(results)

	def pageSoup(self, page_url):
		r = requests.get(PeopleAndMovies.BASE_URL + page_url)
		if r.status_code == 200:
			page_soup = soup(r.text, 'html.parser')
			return page_soup

	def parseUrls(self, list_page_url):
		page_soup = self.pageSoup(list_page_url)
		if page_soup and "/search/title" in list_page_url:
			movie_titles = page_soup.select("#main .lister-item .lister-item-header a")
			return [title['href'] for title in movie_titles]

	def pageSummary(self, page_url):
		page_soup = self.pageSoup(page_url)
		overview = page_soup.find(id="title-overview-widget")
		if overview:
			title = overview.find("h1", attrs={"itemprop": "name"})
			year_node = title.find(id="titleYear")
			year_node.decompose() if year_node else None
			title = title.getText().strip()

			plot_summary = overview.find(class_="plot_summary")
			if plot_summary:
				directors = [item.find(attrs={"itemprop": "name"}).getText().strip() for item in plot_summary.findAll(attrs={"itemprop": "director"})]
				creators = [item.find(attrs={"itemprop": "name"}).getText().strip() for item in plot_summary.findAll(attrs={"itemprop": "creator"})]
				actors = [item.find(attrs={"itemprop": "name"}).getText().strip() for item in plot_summary.findAll(attrs={"itemprop": "actors"})]

				result = {}
				result[title] = { "directors": directors, "creators": creators, "actors": actors }
				return result

	def find(self, query):
		matches = []
		query_keywords = query.split(' ')
		for person_name in self.cache.keys():
			for name_token in person_name.split(' '):
				for keyword in query_keywords:
					if name_token.lower().strip().startswith(keyword.strip()):
						matches.append(json.dumps({
							person_name: self.cache[person_name]
						}))
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
							self.cache[person] = {}
							self.cache[person][role] = [title]

	def search(self, person_name):
		results = self.find(person_name)
		return '[{}]'.format(','.join(results))
