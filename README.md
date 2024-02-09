# projet-indexation-web
TPs du Cours d'indexation Web

Par l'étudiant AGONNOUDE Tom

Ce repo regroupes les différents TP ci dessous :

1. [TP1 - Crawler](#tp1---crawler)
2. [TP2 - Création d'index](#tp2---index-creation)
2. [TP3 - Expansion de requête et ranking](#tp3---request-expansion-and-ranking)


## TP1 - Crawler 

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
- `sitemaps` : pour inclure la recherche les sitemaps et y récupérer des liens. La limite de nombre maximum de document à récupérer au total passe à 60 pages. On se limitera aussi à 15 liens par sitemap visitées.
- `database` : pour créer une base de données relationnelle pour stocker les pages web trouvées ainsi que leur dates et heures de parsing respectifs. Les liens retournés dans le fichier final `crawled_webpages.txt` sont ceux enrégistrés dans la base de données avec leur âge.



## TP2 - Index Creation  

### Exécution simple
Pour exécuter le code pour la création d'index :
- Cloner le repo et se mettre dans le dossier `index_tp2/`
- S'assurer que toutes les dépendances sont installés
- Lancer l'exécution du fichier main.py

```
git clone https://github.com/tommy-21/projet-indexation-web.git && cd projet-indexation-web/index_tp2/
pip install -r requirements.txt
python main.py
```
Cette dernière commande permet de créer l'index non positionnel du titre le plus simple (renvoyé dans un fichier `title.non_pos_index.json`) avec comme traitement un downcasing et une tokenisation simple. Elle permet aussi de générer un fichier `metadata.json` contenant des statistiques sur les documents traités. Les autres exécutions possibles (décrites ci-dessous) produisent à minima ces deux fichiers. 

### Arguments
Le lancement de l'exécution du ficher main.py peut se faire suivi des arguments suivants: 
- `stemming` : pour inclure du stemming dans le traitement des données. Renvoie le fichier `mon_stemmer.title.non_pos_index.json`.
- `positional` : pour créer un index positionnel. Renvoie le fichier `title.pos_index.json`. Mets un peu de temps (plus de 5 min)
- Mettre les deux arguments précédents à la fois renverra en plus un quatrième index, index positionnel obtenu à partir des données stemmé et renvoyé dans le fichier `mon_stemmer.title.pos_index.json` (tout ça est un peu chronophage par contre...)

Tout les index sont faits avec les titres.



## TP3 - Request Expansion and Ranking

### Exécution simple
Pour exécuter le code pour la création d'index :
- Cloner le repo et se mettre dans le dossier `index_tp3/`
- S'assurer que toutes les dépendances sont installés
- Lancer l'exécution du fichier main.py

```
git clone https://github.com/tommy-21/projet-indexation-web.git && cd projet-indexation-web/index_tp/
pip install -r requirements.txt
python main.py
```

Vous serez en suite invité (après quelques secondes...) à entrer votre requête. Ensuite appuyez sur "Entrée" et les résultats s'afichent.

Les résultats sont aussi stockés dans un fichier `results.json` avec d'autres informations pratiques.

### Détails techniques
Il n'y a pas ici d'arguments supplémentaires mais la fonction de ranking bm25 a été implémentée et est utilisée par défaut.

Uniquement l'option `ET` a été implémentée, c'est-à-dire, qu'on ne renvoie que des documents dans lesquels on retrouve tous les tokens contenus dans la requête utilisateur.

La première exécution du script peut prendre un peu de temps. Ceci est dû au calcul des valeurs TF et IDF de chaque token pour chaque document. Ces valeurs seront stockées dans des fichiers .json nommées respectivement `tf_title.json`, `idf_title.json`, `tf_content.json` et `idf_content.json` (TFs et IDFs pour chacun des index : titre et contenu). Ces fichiers vont justes être chargés puis réutilisés les prochaines fois pour éviter d'avoir la même latence à chaque exécution.  

Les features pour le ranking ont été calculées séparément pour les titres et pour les contenus des pages avec une très forte importance donnée au features concernant les titres dans la fonction de ranking. 
  