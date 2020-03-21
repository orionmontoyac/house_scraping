from house_page_object import *

def _save_houses(news_site_uid, houses):
    now = datetime.datetime.now()
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(houses[0])))
    out_file_name = '{news_site_uid}_{datetime}_houses.csv'.format(news_site_uid=news_site_uid, datetime=now.strftime('%Y_%m_%d'))

    with open(out_file_name, mode='w+') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)

        writer.writeheader()
        for house in houses:
            logging.info('Save house: {}'.format(house._link))
            row = {prop:str(getattr(house, prop)) for prop in csv_headers}#[str(getattr(house, prop)) for prop in csv_headers]
            writer.writerow(row)
            
def _build_link(host, link):
    if is_well_formed_url.match(link):
        return link
    elif is_root_path.match(link):
        return '{host}{uri}'.format(host=host, uri=link)
    else:
        return '{host}/{uri}'.format(host=host, uri=link)
    
def _fetch_house(news_site_uid, host, link):
    logging.info('Start fetching house at {}'.format(link))
    house = None
    try:
        house = housePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logging.warn('Error while fetching house!', exc_info=False)

    if house and not house._valid_house():
        logging.warn('Invalid house.')
        return None
    
    return house

def _houses_scraper(news_site_uid):
    host = config()[news_site_uid]['url']

    logging.info('Beginning scraper for {}'.format(host))
    logging.info('Finding links in homepage...')

    house_links = _find_house_links_in_homepage(news_site_uid)

    logging.info('{} house links found in homepage'.format(len(house_links)))
    
    houses = []
    for link in house_links:
        house = _fetch_house(news_site_uid, host, link)

        if house:
            logging.info('house fetched!')
            houses.append(house)
            #break
        
    _save_houses(news_site_uid, houses)


def _find_house_links_in_homepage(news_site_uid):
    homepage = HomePage(news_site_uid, config()[news_site_uid]['url_search'])

    return homepage.house_links

if __name__ == "__main__":
    _houses_scraper('finca_raiz')