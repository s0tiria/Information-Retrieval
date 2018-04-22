
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################
###########SYNOPSIS############
###############################
#
# Auteurs : Sotiria BAMPATZANI
#           Morgane DEHARENG
#
# Date : 18/04/18
#
# But : réalisation d'un petit moteur de recherche pour effectuer des requêtes booléennes sur un corpus donné
#
# Usage : python3 moteurRI.py
#
# Documentation : générée à l'aide de la commande 'pydoc -w .\moteurRI.py'
###############################

import os
import re
import sys
import glob
import spacy
import fr_core_news_sm
import nltk

def openFile(f):
    '''
    Lecture d'un fichier
    :param f: Le nom du fichier
    :return: Un identifiant vers le fichier ouvert, que l'on peut ensuite utiliser pour lire et écrire dans le fichier
    :rtype: TextIOWrapper
    '''
    fi = open(f, encoding='utf8')
    return fi

def extractTitle(f):
    '''
    Lecture de la première ligne d'un fichier
    :param f: Le nom d'un fichier déjà ouvert avec la fonction openFile
    :return: Le titre du document se trouvant dans la première ligne
    :rtype: String
    '''
    firstLine = f.readline().replace('\n', '').rstrip()
    title = firstLine.split(None, 1)[1]
    return title

def normalizeFile(f):
    '''
    Normalisation de base d'un fichier
    :param f: Le nom du fichier
    :return: Une variable conteant le contenu du fichier en une string
    :rtype: String
    '''
    fnorm = f.read().replace('\n', ' ')
    fnorm = fnorm.rstrip()
    return fnorm

def tokenizeText(text, encoding='utf8'):
    '''
    Normalisation et tokenisation du texte
    :param text: Le contenu du fichier en une variable String
    :return: Une liste des tokens du fichier
    :rtype: List
    '''
    text = text.replace("’", "'")
    text = text.replace('«', '"')
    text = text.replace('»', '"')
    tokens = nltk.word_tokenize(text)
    return tokens

def normalizeFile73(f):
    '''
    Normalisation d'un fichier illisible
    :param f: Le chemin du fichier à traiter
    :return: Le contenu normalisé du fichier en une variable String
    :rtype: String
    '''
    file = openFile(f)
    title = extractTitle(file)
    text = normalizeFile(file)
    listTokens = tokenizeText(text)

    newTokens = list()
    for token in listTokens:
        if len(token) > 1:
            newToken = token[:-1]
            if len(newToken) == 1:
                newToken = newToken.replace('i', 'il')
            newToken = newToken.replace('queu', 'que')
            newToken = newToken.replace('celuio-ci', 'celui-ci')
            newToken = newToken.replace('quh', 'qu')
            newToken = newToken.replace('Sainteu-Lazare', 'Saint-Lazare')
            newToken = newToken.replace('pardessusssssssssssssssssssss', 'pardessus')
            newTokens.append(newToken)
        else:
            newTokens.append(token)
    return '73. ' + title + '\n' + ' '.join(newTokens)

def removeStopwords(text, encoding='utf8'):
    '''
    Suppression des mots vides (stopwords)
    :param text: Le contenu du fichier en une variable String
    :return: Une liste des tokens du fichier sans les mots vides
    :rtype: List
    '''
    stopWords = set(nltk.corpus.stopwords.words('french'))
    tokens = tokenizeText(text)
    tokens = [w.lower() for w in tokens if w.isalpha()]
    filteredTokens = [word for word in tokens if not word in stopWords]
    filteredTokens = []
    for word in tokens:
        if word not in stopWords:
            filteredTokens.append(word)
    return filteredTokens

def LemmatizeWords(listWords):
    '''Lemmatisation
    :param listWords: Une liste des tokens
    :return: Une liste des tokens lemmatisés
    :rtype: List
    '''
    listLemmas = list()
    strWords = " ".join(str(word) for word in listWords)
    nlp = fr_core_news_sm.load()
    strLemmas = nlp(strWords)
    for frLemma in strLemmas:
        listLemmas.append(frLemma.lemma_)
    return listLemmas

def freqInDoc(term, listWords):
    '''
    Calcul de la fréquence locale dans le texte tokenisé et lemmatisé
    :param term: Le terme, une string
    :param listWords: Une liste de termes
    :return: La fréquence d'un terme dans une liste
    :rtype: int
    '''
    return listWords.count(term)

def word2index():
    '''
    Récupération de la requête entrée par l'utilisateur sur la ligne de commande
    :return: Une liste contenant les mots de la requête à traiter
    :rtype: list
    '''
    query = str(input())
    words = list()

    # s'il y a des espaces
    if ' ' in query:
        # création d'une liste contenant les mots recherchés
        words = query.split(" ")

        # pour chaque mot de la liste
        for i, word in enumerate(words):
            # si le mot commence avec '-' on le supprime de la liste finale
            if word.startswith('-'):
                words.remove(word)
            # si le mot commence avec '+' on supprime le caractère '+' du début et on garde le mot
            elif word.startswith('+'):
                words[i] = word[1:]

    # sinon, il n'y a qu'un seul mot dans la requête
    else:
        words.append(query)
    
    return words

# main
if __name__ == "__main__":

    # traitement d'un fichier illisible
    file73 = normalizeFile73('.\ExercicesDeStyle\_txt\exercice73!.txt')
    with open('.\ExercicesDeStyle\_txt\exercice73.txt', 'w', encoding='utf-8') as file:
        file.write(file73)

    # chemin vers le dossier contenant les fichiers à indexer
    pathdir = ".\ExercicesDeStyle"

    try:
        os.path.exists(pathdir)
    except EnvironmentError:
        print("Problème avec le chemin vers le dossier contenant les fichiers")
    else:
        # déclaration et initialisation des variables
        docNo = 0
        freqGlobale = 0
        allFreqLoc = list()
        allTitleLoc = list()
        indexInverse = dict()
        indexTitle = dict()

        print("Traitement du dossier :", pathdir)
        print("Votre recherche :")

        # on sauvegarde la requête de l'utilisateur dans une liste search
        search = word2index()
        
        # pour chaque document
        # on ne prend en compte que les documents à indexer, autrement dit, ceux qui n'ont pas un '!' avant l'extension
        for filename in glob.glob(os.path.join(pathdir, '_txt\*[0-9].txt')):
            docNo += 1

            # ouverture du fichier
            f = openFile(filename)

            # association d'un identifiant avec le nom du doc
            idDoc = dict()
            dictname = os.path.basename(filename)
            idDoc[dictname] = docNo
            print("Traitement du fichier :", dictname)

            # extraction du titre
            docTitle = extractTitle(f)

            # création d'une table de correspondance entre le titre, l'url et l'identifiant
            allTitle = dict()
            if docNo not in allTitle.keys():
                allTitle.setdefault(docNo, (dictname, docTitle))

            # prétraitement du texte extrait à l'aide des fonctions normalizeFile, removeStopwords et LemmatizeWords
            content = normalizeFile(f)
            contentTokenized = removeStopwords(content)
            contentLemmatized = LemmatizeWords(contentTokenized)

            # pour chaque mot de la requête
            for word in search:

                # si le(s) mot(s) recherché(s) par l'utilisateur existe(nt) dans le fichier
                if word in contentLemmatized:

                    # calcul de la fréquence locale
                    freqLocale = freqInDoc(word, contentLemmatized)

                    # association de cette fréquence avec l'id du doc
                    wordFreqLoc = dict()
                    wordFreqTitle = dict()
                    # pour l'index inversé
                    wordFreqLoc[word] = {docNo: freqLocale}
                    # pour l'affichage des documents trouvés
                    wordFreqTitle[word] = {allTitle[docNo] : freqLocale}

                    # création d'une liste contenant tous les docs ayant le mot recherché avec sa fréquence
                    allFreqLoc.append(wordFreqLoc)
                    allTitleLoc.append(wordFreqTitle)

                    # calcul de la fréquence globale
                    freqGlobale = freqGlobale + freqLocale
                
                    # création de l'index inversé
                    indexInverse = {freqGlobale : allFreqLoc}
                    indexTitle = {freqGlobale : allTitleLoc}

        # si l'index inversé a été créé, autrement dit, si le(s) mot(s) recherché(s) existe(nt) dans le corpus
        if len(indexInverse) > 0:
            print("\nSauvegarde de l'index inversé")
            with open("indexInverse.txt", 'w') as index:
                index.write(str(indexInverse))
            # pour la requête "chapeau +pardessus -cou" :
            # {7: [{'chapeau': {1: 1}}, {'pardessus': {1: 1}}, {'chapeau': {2: 1}}, {'chapeau': {3: 1}}, {'pardessus': {3: 1}}, {'chapeau': {4: 1}}, {'pardessus': {4: 1}}]}
            # où :
            # {fréquence de tous les termes dans tous les documents : {mot: [{docNo: fréqLocale}}, {mot: [{docNo: fréqLocale}} ...]}

        # sinon
        else:
            print("Le mot(s) recherché(s) n'existe(nt) pas dans le corpus")
        print("\nNombre total de fichiers traités :", docNo)
        print("Nombre total d'occurrences trouvées :", freqGlobale)

        # affichage des documents trouvés
        print("\nDocuments trouvés : ")
        for items in allTitleLoc:
            for value in items:
                query = str(value)
                for val in items.values():
                    for doc in val.keys():
                        url = str(doc[0])
                        title = str(doc[1])
                    for freq in val.values():
                        frequency = str(freq)
            print(title + " - " + url + " : " + frequency + " occurrence(s) de " + query )

    print("\nDone")