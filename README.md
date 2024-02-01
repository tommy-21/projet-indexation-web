# projet-indexation-web
TPs du Cours d'indexation Web
Par l'étudiant AGONNOUDE Tom

## Crawler 

### Exécution simple
Pour exécuter le crawler:
- Cloner le repo et se mettre dans le dossier `crawler/`
- S'assurer que toutes les dépendances sont installés
- Lancer l'exécution du fichier main.py

```
git clone https://github.com/tommy-21/projet-indexation-web.git && cd projet-indexation-web/crawler/
pip install -r requirements.txt
python main.py
```
Pour cette version la plus simple du crawler, les limites de nombres de documents à récupérer sont de 5 liens par pages et 50 pages au total. 

Le programme retourne le fichier `crawled_webpages.txt` contenant les urls dont les pages ont été téléchargées.

Le temps d'attente entre deux téléchargements de pages est de 5s entre chaque appel (les requêtes aux robots.txt ne sont pas considérées). Ce temps de 5s prend en compte la durée de téléchargement de la page précédente.

### Arguments
Pour le lancement de l'exécution du ficher main.py, on peut ajouter les arguments suivants: 
- `sitemaps` : pour inclure la recherche les sitemaps et y récupérer des liens. La limite de nombre maximum de document à récupérer au total passe à 100 pages. On se limitera aussi à 15 liens par sitemap visitées.
- `database` : pour créer une base de données relationnelle pour stocker les pages web trouvées ainsi que leur dates et heures de parsing respectifs. Les liens retournés dans le fichier final `crawled_webpages.txt` sont ceux enrégistrés dans la base de données avec leur âge.