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

Le temps d'attentes entre deux téléchargements de pages est de 5s minimum (les requêtes aux robots.txt et au sitemaps.xml ne sont pas considérées)

### Arguments
Pour le lancement de l'exécution du ficher main.py, on peut ajouter les arguments suivants: 
- `sitemaps` : pour inclure la recherche les sitemaps et y récupérer des liens. Les limites de nombre maximum de document à récupérer passent à 100 pages au total et 20 liens par page. 