import os
import json
import math
import pandas as pd

def calculer_idf(index, nb_total_documents):
    idf_dict = {}
    for token, docs in index.items():
        idf_dict[token] = math.log(nb_total_documents / float(len(docs)))
    return idf_dict


def calculer_tf_par_document(index):
    tf_par_document = {}
    for token, docs in index.items():
        for docId, info in docs.items():
            if docId not in tf_par_document:
                tf_par_document[docId] = {}
            tf_par_document[docId][token] = info["count"]
    
    for docId in tf_par_document.keys():
        tf_par_document[docId]["| |"] = sum([tf_par_document[docId][token] for token in tf_par_document[docId].keys() if token != "| |"])

    return tf_par_document

def calculer_proximite(tokens_requete, positions_tokens):
    """
    Calcule la proximité moyenne entre les tokens de la requête dans un document.

    :param tokens_requete: Liste des tokens de la requête.
    :param positions_tokens: Dictionnaire où la clé est le token et la valeur est la liste des positions de ce token dans le document.
    :return: La distance moyenne entre les tokens consécutifs de la requête dans le document.
    """
    distances = []
    for i in range(len(tokens_requete) - 1):
        token_actuel = tokens_requete[i]
        token_suivant = tokens_requete[i + 1]
        
        # Vérifie si les deux tokens consécutifs sont dans le document
        if token_actuel in positions_tokens and token_suivant in positions_tokens:
            positions_actuelles = positions_tokens[token_actuel]
            positions_suivantes = positions_tokens[token_suivant]
            
            # Calculer toutes les distances possibles entre les positions des deux tokens et prendre la plus petite
            distance_min = min([abs(int(pos2) - int(pos1)) for pos1 in positions_actuelles for pos2 in positions_suivantes])
            distances.append(distance_min)
    
    # Calculer la distance moyenne si des distances ont été trouvées
    if distances:
        return sum(distances) / len(distances)
    else:
        return 1000000  # Retourner 1 000 000 000 si aucun couple de tokens n'est trouvé consécutifs 



def main():
    # Chargement des fichiers json
    # documents
    file_path = 'documents.json'
    with open(file_path, 'r') as file:
        documents = json.load(file)
    
    # index des titres
    file_path = 'title_pos_index.json'
    with open(file_path, 'r') as file:
        title_index = json.load(file)

    #index des contenus
    file_path = 'content_pos_index.json'
    with open(file_path, 'r') as file:
        content_index = json.load(file)
    

    # # Chargement des mesures TF et IDF
    # if os.path.exists("tf_title.json") and os.path.exists("tf_content.json") and os.path.exists("idf_title.json") and os.path.exists("idf_content.json"):
    #     with open("tf_title.json", 'r') as file:
    #         tf_title = json.load(file)
    #     with open("tf_content.json", 'r') as file:
    #         tf_content = json.load(file)
    #     with open("idf_title.json", 'r') as file:
    #         idf_title = json.load(file)
    #     with open("idf_content.json", 'r') as file:
    #         idf_content = json.load(file)

    # else:    
    #     nb_docs = len(documents)
    #     tf_title = calculer_tf_par_document(title_index)
    #     tf_content = calculer_tf_par_document(content_index)
    #     idf_title = calculer_idf(title_index, nb_docs)
    #     idf_content = calculer_idf(content_index, nb_docs)

    #     with open("tf_title.json", 'w') as file:
    #         json.dump(tf_title, file, indent=4)
    #         print("tf_title saved!")

    #     with open("tf_content.json", 'w') as file:
    #         json.dump(tf_content, file, indent=4)
    #         print("tf_content saved!")

    #     with open("idf_title.json", 'w') as file:
    #         json.dump(idf_title, file, indent=4)
    #         print("idf_title saved!")

    #     with open("idf_content.json", 'w') as file:
    #         json.dump(idf_content, file, indent=4)
    #         print("idf_content saved!")


    # Demander à l'utilisateur d'entrer une requête
    requete = input("Veuillez entrer votre requête : ")

    resultats = {}
    resultats["Requete"] = requete
    nom_fichier_resultat = f'resultats_{requete}'

    # traitement de la requête
    requete = requete.lower().split()



    tokens_contents = [set(content_index[tok].keys()) for tok in requete if tok in content_index.keys()]
    tokens_titles = [set(title_index[tok].keys()) for tok in requete if tok in title_index.keys()]

    if len(requete)!=len(tokens_contents) and len(requete)!=len(tokens_titles): 
        documents_restants = None
    else:
        if tokens_titles:
            title_has_all_tokens = tokens_titles[0]
            for tok_list in tokens_titles:
                title_has_all_tokens = title_has_all_tokens & tok_list

        if tokens_contents:
            content_has_all_tokens = tokens_contents[1]
            for tok_list in tokens_contents:
                content_has_all_tokens = content_has_all_tokens & tok_list

        documents_restants = [("both", docid) for docid in title_has_all_tokens & content_has_all_tokens]
        documents_restants += [("title", docid) for docid in title_has_all_tokens - content_has_all_tokens] 
        documents_restants += [("content", docid) for docid in content_has_all_tokens - title_has_all_tokens]


    # importance de la partie 
    features_documents = dict()
    if documents_restants:
        for docs in documents_restants:
            docID = docs[1]
            features_documents[docID] = {}

            features_documents[docID]["title"] = 0
            features_documents[docID]["content"] = 0
            features_documents[docID]["Occurrence_title"] = 0
            features_documents[docID]["Occurrence_content"] = 0
            features_documents[docID]["Proximite_title"] = 0
            features_documents[docID]["Proximite_content"] = 0

            # contenu ou titre
            if docs[0] == "title" or docs[0] == "both":
                features_documents[docID]["title"] = 1
            if docs[0] == "content" or docs[0] == "both":
                features_documents[docID]["content"] = 1

            # Nombres d'apparition
            features_documents[docID]["Occurrence_title"] = 0 
            features_documents[docID]["Occurrence_content"] = 0
            if docs[0] == "title" or docs[0] == "both":
                features_documents[docID]["Occurrence_title"] = sum([title_index[tok][docID]["count"] for tok in requete if tok in title_index.keys()])
            if docs[0] == "content" or docs[0] == "both":
                features_documents[docID]["Occurrence_content"] = sum([content_index[tok][docID]["count"] for tok in requete if tok in content_index.keys()])
            
            # Proximité
            positions_tokens_title = {}
            positions_tokens_content = {}

            if docs[0] == "title" or docs[0] == "both":
                for token in requete:
                    positions_tokens_title[token] = title_index[token][docID]["positions"] 
                features_documents[docID]["Proximite_title"] = calculer_proximite(requete, positions_tokens_title)
                
            if docs[0] == "content" or docs[0] == "both":
                for token in requete:
                    positions_tokens_content[token] = content_index[token][docID]["positions"]
                features_documents[docID]["Proximite_content"] = calculer_proximite(requete, positions_tokens_content)

            # # TF et IDF
            # features_documents[docID]["TF"] = sum([tf_title[docID][tok]/tf_title[docID]['| |'] for tok in requete]) \
            #                                     + sum([tf_content[docID][tok]/tf_content[docID]['| |'] for tok in requete])
            # features_documents[docID]["IDF"] = sum([idf_title[tok] for tok in requete]) \
            #                                      + sum([tf_content[tok] for tok in requete])

    # Calcul des scores
    scores = {}
    for docid in features_documents.keys():
        scores[docid] = 5*features_documents[docid]["Occurrence_title"] \
            + features_documents[docid]["Occurrence_content"] - 0.1*features_documents[docid]["Proximite_title"] - 0.5*features_documents[docid]["Proximite_content"]
        

    liste_id_docs_pertinents = sorted(scores, key=scores.get, reverse=True)
    documents_df = pd.DataFrame(documents, dtype=str)
    documents_df = documents_df.set_index("id")
    docs_pertinents = [{"Id":docid,
                        "Titre":documents_df.loc[docid, "title"], 
                        "Url":documents_df.loc[docid, "url"]} for docid in liste_id_docs_pertinents]
    
    resultats["Documents par ordre de pertinence"] = docs_pertinents
    resultats["Nombre total de documents"] = len(documents)
    resultats["Nombre de documents ayant survécu au filtre"] = len(liste_id_docs_pertinents)
    
    with open(nom_fichier_resultat, 'w') as file:
        json.dump(resultats, file, indent=4)
        print("Results saved!")
        
    print(resultats)

if __name__ == '__main__':
    main()
    
