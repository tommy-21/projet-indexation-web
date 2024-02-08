import re
import sys
import json

def processing(text, stemming=False):
    text = text.lower() #.split()
    processed = re.findall(r'\b\w+\b', text)

    if stemming:
        stemmer = SnowballStemmer("french")
        processed = [stemmer.stem(tok) for tok in processed]

    return processed

def find_positions(input_list, value):
    return [index for index, elem in enumerate(input_list) if elem == value]


def create_index(prepared_data, positional=False):
    # Liste exaustive des tokens
    tokens_list = prepared_data[0]["data"]
    for doc in prepared_data:
        tokens_list.extend(doc["data"])
    tokens_list = set(tokens_list)
    tokens_list = list(tokens_list)

    # Calcul de l'index non positionnel pour les titres
    index_data = {}
    nb_docs = len(prepared_data)
    for token in tokens_list:
        if positional == False:
            index_data[token] = [id for id in range(nb_docs) if (token in prepared_data[id]["data"])]
        else:    
            index_data[token] = [str(id)+":"+str(find_positions(prepared_data[id]["data"], token)) for id in range(nb_docs) if (token in prepared_data[id]["data"])]
            
    return index_data


def main(stemming=False, positional=False):

    # Chargement du fichier json
    file_path = 'crawled_urls.json'
    with open(file_path, 'r') as file:
        crawled_urls = json.load(file)

    print(crawled_urls[1].keys())

    # Prétraitement des documents
    titles = [url["title"] for url in crawled_urls]
    h1s = [url["h1"] for url in crawled_urls]
    contents = [url["content"] for url in crawled_urls]

    processed_titles = [{"id":titles.index(title)+1, "data":processing(title)} for title in titles]
    if stemming:
        stemmed_titles = [{"id":titles.index(title)+1, "data":processing(title, stemming=stemming)} for title in titles]
    processed_h1s = [{"id":h1s.index(h1)+1, "data":processing(h1)} for h1 in h1s]
    processed_contents = [{"id":contents.index(content)+1, "data":processing(content)} for content in contents]


    # Statistiques sur les documents
    nb_docs = len(crawled_urls)
    nb_tok_titles = sum([len(doc["data"]) for doc in processed_titles])
    nb_tok_h1s = sum([len(doc["data"]) for doc in processed_h1s])
    nb_tok_contents = sum([len(doc["data"]) for doc in processed_contents])
    nb_tokens = nb_tok_titles+nb_tok_h1s+nb_tok_contents

    statistiques = {
        "Nombre de documents" : nb_docs, 
        "Nombre total de tokens" : nb_tokens,
        "Moyenne de tokens par documents" : nb_tokens/nb_docs,
        "Titre" : {
            "Nombre de tokens" : nb_tok_titles,
            "Nombres moyen de tokens par documents" : nb_tok_titles/nb_docs
        },
        "h1" : {
            "Nombre de tokens" : nb_tok_h1s,
            "Nombres moyen de tokens par documents" : nb_tok_h1s/nb_docs,
        },
        "content" : {
            "Nombre de tokens" : nb_tok_contents,
            "Nombres moyen de tokens par documents" : nb_tok_contents/nb_docs,
        }
    }
    # Sauvegarde des métadonnées dans un fichier json
    with open("metadata.json", 'w') as file:
        json.dump(statistiques, file, indent=4)
        print("Metadata saved!")
    

    non_pos_index = create_index(prepared_data=processed_titles)
    # Sauvegarde de l'index dans un fichier json
    file_name = 'title.non_pos_index.json'
    with open(file_name, 'w') as file:
        json.dump(non_pos_index, file, indent=4)
        print("Non positional index saved!")

    if stemming:
        stemmed_non_pos_index = create_index(prepared_data=stemmed_titles)
        # Sauvegarde de l'index dans un fichier json
        file_name = 'mon_stemmer.title.non_pos_index.json'
        with open(file_name, 'w') as file:
            json.dump(stemmed_non_pos_index, file, indent=4)
            print("Stemmed non positional index saved!")

    if positional:
        pos_index = create_index(prepared_data=processed_titles, positional=True)
        # Sauvegarde de l'index dans un fichier json
        file_name = 'title.pos_index.json'
        with open(file_name, 'w') as file:
            json.dump(pos_index, file, indent=4)
            print("Positional index saved!")

    if stemming and positional:
        stemmed_pos_index = create_index(prepared_data=processed_titles, positional=True)
        # Sauvegarde de l'index dans un fichier json
        file_name = 'mon_stemmer.title.pos_index.json'
        with open(file_name, 'w') as file:
            json.dump(stemmed_pos_index, file, indent=4)
            print("Stemmed positional index saved!")

    


if __name__ == '__main__':
    stemming = False
    positional = False

    if 'stemming' in sys.argv:
        stemming = True
        import nltk
        from nltk.stem.snowball import SnowballStemmer
    
    if 'positional' in sys.argv:
        positional = True

    main(stemming=stemming, positional=positional)