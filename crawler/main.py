import sys
import time
import sqlite3
from protego import Protego
import requests
from bs4 import BeautifulSoup
from datetime import datetime



def get_robotstxt(url):
    '''
    Permet de d'obtenir le robots.txt pour une adresse url donnée

    Args:
        url (str): Le lien

    Returns:
        str or None: Le contenu brut (html) de la page
    '''
    base_url = url.split('/')[0] + '//' + url.split('/')[2]
    robots_url = base_url + '/robots.txt'
    timeout_duration = 10
    robots = None

    try:
        response = requests.get(robots_url, timeout=timeout_duration)
        if response.status_code == 200:
            robots = response.text
    except requests.Timeout:
        print(f"Request timed out after {timeout_duration} seconds for the robots.txt of {url}")
    except Exception as e:
        print(f'Exception {e} occured while trying to get the robots.txt of {url}')
    
    return robots


def robotstxt_authorization(url):
    '''
    Vérifie auprès du robots.txt si l'url peut être crawlé

    Args:
        url (str): Le lien

    Returns:
        bool: True si Oui, False si Non
    '''
    authorization = True
    robotstxt = get_robotstxt(url)
    if robotstxt:
        rp = Protego.parse(robotstxt)
        authorization = rp.can_fetch(url, "*")

    return authorization


def fetch(url):
    '''
    Recupère le contenu de la page web désignée par le lien.

    Args:
        url (str): Le lien

    Returns:
        str or None: Le contenu brut (html) de la page
    '''
    timeout_duration = 10
    page = None
    download_time = 0

    try:
        response = requests.get(url, timeout=timeout_duration)
        if response.status_code == 200:
            page = response.text
            download_time = float(response.elapsed.total_seconds())
    
    except requests.Timeout:
        print(f"Request timed out after {timeout_duration} seconds for {url}")
    except Exception as e:
        print(f'Exception {e} occured while trying to get {url}')

    time.sleep(max(0, 5-download_time))
    return page


def parse(page, frontier, limit=5):
    '''
    Récolte les liens contenus dans une page

    Args:
        page (str): La page à parcourir
        frontier (List[str]): Liste de liens déjà repertoriés
        limit (int): nombre maximum de liens à récupérer

    Returns:
        str or None: Le contenu brut (html) de la page
    '''
    links = []
    soup = BeautifulSoup(page, 'html.parser')
    a_tags = soup.find_all('a')

    # Extration des liens
    for a_tag in a_tags:
        link = a_tag.get('href')
        if link and link[:4]=='http' and (link not in links) and (link not in frontier):
            if robotstxt_authorization(link):
                links.append(link)
                if len(links)>=limit: 
                    break

    return links


def parse_sitemap(sitemap_content, limit=15):
    soup = BeautifulSoup(sitemap_content, 'xml')
    urls_info = []
    for url in soup.find_all('url'):
        loc = url.find('loc').text
        if loc and loc[:4]=='http' and (loc not in urls_info):
            urls_info.append(loc)
        if len(urls_info)>=limit:
            break
    return urls_info


def fetch_urls_from_sitemaps(url, limit = 30):
    robotstxt = get_robotstxt(url)
    links = []
    if robotstxt:
        rp = Protego.parse(robotstxt)
        sitemaps = list(rp.sitemaps)
        

        for sitemap in sitemaps:
            sitemap_content = fetch(sitemap)
            if sitemap_content:
                new_links = parse_sitemap(sitemap_content)
                links.extend([elmt for elmt in new_links if elmt not in links])
                if len(links)>= limit:
                    break

    return links


def save_to_database(url, page, conn):
    try:
        cursor = conn.cursor()
        current_time_seconds = time.time()
        readable_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time_seconds))
        sql = f"INSERT INTO crawled_pages (url, page_content, last_crawled) VALUES (?, ?, ?)"
        cursor.execute(sql, (url, page, readable_time,))
        conn.commit()
        print("Saved to database.")
    except Exception as e:
        print(f'Something went wrong with the saving of {url} to the database: {e}')


def compute_age(saving_time):
    time_format = "%Y-%m-%d %H:%M:%S"

    given_time = datetime.strptime(saving_time, time_format)
    current_time = datetime.now()

    age = current_time - given_time

    return str(age)


######################################## MAIN FUNCTION ################################################

def main(database, sitemaps):
    seed = ["https://ensai.fr/"]    # ensemble d’urls de départ
    termination = 50                # nombre max de pages à crawler
    frontier = seed     # file d'attente des requêtes initialisé par le seed
    discovered = []     # liste des liens déjà téléchargés 

    if database:
        conn = sqlite3.connect('crawler_database.db') # connection à la base de données
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS crawled_pages''')
        cursor.execute('''CREATE TABLE crawled_pages (url TEXT PRIMARY KEY, page_content TEXT, last_crawled TEXT);''')

    if sitemaps:
        retrieved_sitemaps_urls = []
        termination = 60
    
    # BOUCLE POUR CHAQUE LIEN DE LA FRONTIER
    for url in frontier:
        print("Start", url)
        # récupération de la page et des liens présents sur la page analysée
        page_content = fetch(url)

        # recherches et extraction de sitemaps
        if sitemaps: 
            base_url = url.split('/')[0] + '//' + url.split('/')[2]
            if base_url not in retrieved_sitemaps_urls:
                sitemaps_urls = fetch_urls_from_sitemaps(url)
                retrieved_sitemaps_urls.append(base_url)
                if sitemaps_urls:
                    frontier.extend([elmt for elmt in sitemaps_urls if elmt not in frontier])

        if page_content:
            # recherche de liens dans les documents téléchargés
            urls_found = parse(page_content, frontier=frontier)
            frontier.extend(urls_found),

            # mise à jour du discovered et sauvegarde dans la base de données
            discovered.append(url)
            if database:
                save_to_database(url, page=page_content, conn=conn)
            print("Done for", url, "\n")
            
            # arret si nombre max de page atteint
            if len(discovered) >= termination :
                break


    # ecriture dans un fichier txt de toutes les urls trouvées
    with open('crawled_webpages.txt', 'w') as file:
        if database:
            cursor.execute("SELECT * FROM crawled_pages")
            results = cursor.fetchall()
            for item in results:
                age = compute_age(item[2])
                file.write(str(item[0]) + '\t\t' + age + '\n')
        else:
            for item in discovered:
                file.write(str(item) + '\n')

    with open('to_be_crawled_webpages.txt', 'w') as file:
        for item in frontier:
            file.write(str(item) + '\n')




if __name__ == '__main__':
    database = False
    sitemaps = False

    if 'sitemaps' in sys.argv:
        sitemaps = True
    
    if 'database' in sys.argv:
        database = True

    main(database=database, sitemaps=sitemaps)