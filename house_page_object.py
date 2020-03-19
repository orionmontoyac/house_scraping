import yaml
import requests
import bs4
import re
import logging
import csv
import datetime
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

is_well_formed_url= re.compile(r'^https?://.+/.+$') # i.e. https://www.somesite.com/something
is_root_path = re.compile(r'^/.+$') # i.e. /some-text
logging.basicConfig(level=logging.INFO)


def config():
    __config = None
    if not __config:
        with open('config.yaml',mode = 'r') as f:
            __config = yaml.load(f)
    
    return __config

class HousePage:

    def __init__(self, news_site_uid, url):
        
        self._queries = config()[news_site_uid]['queries']
        self._regex = config()[news_site_uid]['regex']
        self._html = None
        self._link = url

        self._visit(url)

    def _select(self, query_string):
        return self._html.select(query_string)
    
    def _select_from_house(self, query_string):
        return self._html.select(query_string) 
       
    def _visit(self, url):
        response = requests.get(url)
        response.raise_for_status()

        self._html = bs4.BeautifulSoup(response.text, 'html.parser')

class HomePage:

    def __init__(self, news_site_uid, url):
        self._queries = config()[news_site_uid]['queries']
        self._regex = config()[news_site_uid]['regex']
        self._html = None
        self._visit(url)
        
    def _select(self, query_string):
        nodes = []
        for page in self._html:
            nodes = nodes + page.select(query_string)
        
        return nodes
    
    def _visit(self, url):
        self._html = []
        page = 1
        while(page <= 44):
            new_url = url + str(page)
            response = requests.get(new_url)
            if response.status_code != 404:
                logging.info('Getting response from: {}'.format(new_url))
                response.raise_for_status()
                self._html.append(bs4.BeautifulSoup(response.text, 'html.parser'))
                page += 1
            else:
                break

    @property
    def house_links(self):
        link_list = []
        for link in self._select(self._queries['homepage_house_links']):
            if link and link.has_attr('href'):
                link_list.append(link)

        return set(link['href'] for link in link_list)


class housePage(HousePage):

    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)

    def _valid_house(self):
        return len(self._select(self._queries['valid_house'])) < 1
    
    @property
    def zone(self):
        result = self._select(self._queries['house_zone'])
        zone = result[0].text#re.search(self._regex['rooms_regex'],result[0].text)
        zone = zone.replace('\n','')
        return zone if len(result) else ''
    
    @property
    def prize(self):
        result = self._select(self._queries['house_prize'])
        prize = re.search(self._regex['prize_regex'],result[0].text)[0]
        return prize if len(result) else ''

    @property
    def area(self):
        result = self._select(self._queries['house_area'])
        area = re.search(self._regex['area_regex'],result[0].text)[0]
        return area if len(result) else ''

    @property
    def rooms(self):
        result = self._select(self._queries['house_bath_rooms'])
        rooms = re.search(self._regex['rooms_regex'],result[0].text)[0]
        return rooms if len(result) else ''
    
    @property
    def bath_rooms(self):
        result = self._select(self._queries['house_bath_rooms'])
        baths = re.search(self._regex['rooms_regex'],result[0].text)[0]
        return baths if len(result) else ''
    
    @property
    def link(self):
        return self._link 
