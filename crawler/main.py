import time
from protego import Protego
import requests
from bs4 import BeautifulSoup



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
    timeout_duration = 5
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
    response = requests.get(url)

    if response.status_code == 200:
        page = response.text
    else:
        print("Failed to retrieve the webpage from url", url)
        page = None

    return page



def parse(page, frontier, limit=5):
    '''
    Récolte les liens contenus dans une page

    Args:
        page (str): La page à parcourir
        frontier (List[str]): Liste de liens deja repertoriés
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



if __name__ == '__main__':
    seed = ["https://ensai.fr/"]    # ensemble d’urls de départ
    termination = 50                # nombre max de pages à crawler

    frontier = seed     # file d'attente des requêtes initialisé par le seed
    discovered = []     # liste des liens déjà téléchargés 
    
    for url in frontier:
        # récupération de la page et des liens présents sur la page analysée
        page_content = fetch(url)
        time.sleep(5)
        urls_found = parse(page_content, frontier=frontier)

        # mise à jour de la frontier et du discovered
        frontier.extend(urls_found)
        print("Done for", url)
        discovered.append(url)

        # arret si nombre max de page atteint
        if len(discovered) >= termination :
            break


    # ecriture dans un fichier txt de toutes les urls trouvées
    with open('crawled_webpages.txt', 'w') as file:
        for item in discovered:
            file.write(str(item) + '\n')

    with open('to_be_crawled_webpages.txt', 'w') as file:
        for item in frontier:
            file.write(str(item) + '\n')