import time
from protego import Protego
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote



def get_robotstxt(url):
    base_url = url.split('/')[0] + '//' + url.split('/')[2]
    robots_url = base_url + '/robots.txt'
    response = requests.get(robots_url)

    if response.status_code == 200:
        return response.text
    else:
        return None


def fetch_and_parse(url):
    encoded_url = quote(url, safe='/:?=&')

    links = []
    response = requests.get(encoded_url)

    if response.status_code == 200:
        page = response.text
        soup = BeautifulSoup(page, 'html.parser')
        a_tags = soup.find_all('a')

        # Extration des liens
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href:
                links.append(href)
    else:
        print("Failed to retrieve the webpage from url", url)
        page = None


    # Filtrage des liens autorisés par le robots.txt
    robotstxt = get_robotstxt(url)
    if robotstxt:
        rp = Protego.parse(robotstxt)
        allowed_links = [link for link in links if rp.can_fetch(link, "*")]
    else:
        allowed_links = links

    return (page, allowed_links)



if __name__ == '__main__':
    seed = ["https://ensai.fr/"]    # ensemble d’urls de départ
    termination = 50                # nombre max de pages à crawler

    frontier = seed     # file d'attente des requêtes initialisé par le seed
    discovered = []     # liste des liens déjà téléchargés 
    
    
    for url in frontier:
        # récupération de la page et des liens présents sur la page analysée
        page, urls_found = fetch_and_parse(url)
        time.sleep(3)

        if page:
            # ajout des nouveaux liens à la liste d'attente
            new_urls_found = []
            new_urls_found = [link for link in urls_found if (link not in frontier and len(new_urls_found)<5)]
            frontier.extend(new_urls_found)

            # mise à jour de la frontier et du discovered
            print("Done for", url)
            discovered.append(url)
            frontier.remove(url)

        # arret si nombre max de page atteint
        if len(discovered) >= termination :
            break


    # ecriture dans un fichier txt de toutes les urls trouvées
    with open('crawled_webpages.txt', 'w') as file:
        for item in discovered:
            file.write(str(item) + '\n')
