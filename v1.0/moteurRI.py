
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################
###########SYNOPSIS############
###############################
#
# Auteurs : Sotiria BAMPATZANI
#           Morgane DEHARENG
#
# Date : 03/04/18
#
# But : réalisation d'un petit moteur de recherche pour effectuer des requêtes booléennes sur un corpus donné
#
# Usage : python3 moteurRI.py
###############################

import os
import re
import sys
import glob
import math
from collections import defaultdict
from collections import OrderedDict
import spacy
import fr_core_news_sm
import treetaggerwrapper
from FrenchLefffLemmatizer.FrenchLefffLemmatizer import FrenchLefffLemmatizer
import nltk
from nltk.tokenize import WhitespaceTokenizer
from nltk.corpus import stopwords
from nltk.stem.snowball import FrenchStemmer

def openFile(f):
    '''lecture d'un fichier'''
    fi = open(f, encoding='utf8')
    return fi

def extractTitle(f):
    '''lecture de la première ligne d'un fichier (ici contenant le titre)'''
    firstLine = f.readline().replace('\n', '').rstrip()
    title = firstLine.split(None, 1)[1]
    return title

def normalizeFile(f):
    '''normalisation de base d'un fichier et sauvegarde de ce dernier en une variable (string)'''
    fnorm = f.read().replace('\n', ' ')
    fnorm = fnorm.rstrip()
    return fnorm

def tokenizeText(text, encoding='utf8'):
    '''normalisation et tokenisation du texte'''
    text = text.replace("’", "'")
    text = text.replace('«', '"')
    text = text.replace('»', '"')
    tokens = nltk.word_tokenize(text)
    return tokens

def removeStopwords(text, encoding='utf8'):
    '''suppression des mots vides'''
    stopWords = set(nltk.corpus.stopwords.words('french'))
    tokens = tokenizeText(text)
    tokens = [w.lower() for w in tokens if w.isalpha()]
    filteredTokens = [word for word in tokens if not word in stopWords]
    filteredTokens = []
    for word in tokens:
        if word not in stopWords:
            filteredTokens.append(word)
    return filteredTokens

def stemWords(listWords):
    '''racinisation'''
    stemmedWords = list()
    stemmer = FrenchStemmer()
    for word in removeStopwords(listWords):
        stemmedWord=stemmer.stem(word)
        stemmedWords.append(stemmedWord)
    stemmedWords.sort()
    return stemmedWords

def LemmatizeWords(listWords):
    '''lemmatisation'''
    listLemmas = list()
    strWords = " ".join(str(word) for word in listWords)
    nlp = fr_core_news_sm.load()
    strLemmas = nlp(strWords)
    for frLemma in strLemmas:
        listLemmas.append(frLemma.lemma_)
    return listLemmas

def sortDict(dictionary, dictKey):
    '''tri d'un dictionnaire (s'il n'est pas vide)'''
    if not dictionary:
        return dictionary
    else:
        return OrderedDict(sorted(dictionary[dictKey].items(), key=lambda t: t[1], reverse=True))

def freqInDoc(term, lemmatizedText):
    '''fréquence locale dans le texte tokenisé et lemmatisé'''
    return lemmatizedText.count(term)

def word2index():
    '''mot cherché par l'utilisateur'''
    word = str(input())
    return word


if __name__ == "__main__":
    
    pathdir = "F:\M2 TAL\M2 S2\Recherche d'information\TPs\ExercicesDeStyle"

    try:
        os.path.exists(pathdir)
    except EnvironmentError:
        print("Problem with the path directory")
    else:
        docNo = 0
        freqGlobale = 0
        allFreqLoc = list()
        indexInverse = dict()
        print("Traitement du dossier:", pathdir)
        print("Veuillez taper un mot à indexer:")
        searchedWord = word2index()
        print(searchedWord)
        # pour chaque document
        # on ne prend en compte que les documents à indexer, autrement dit, ceux qui n'ont pas un '!' avant l'extension
        for filename in glob.glob(os.path.join(pathdir, '_txt\*[0-9].txt')):
            docNo += 1
            f = openFile(filename)
            # association d'un identifiant avec le nom du doc
            idDoc = dict()
            dictname = os.path.basename(filename)
            idDoc[dictname] = docNo
            print("Traitement du fichier :", dictname)
            # extraction du titre
            docTitle = extractTitle(f)
            # prétraitement du texte extrait
            content = normalizeFile(f)
            contentTokenized = removeStopwords(content)
            contentLemmatized = LemmatizeWords(contentTokenized)
            print(searchedWord)
            print(contentLemmatized)
            if searchedWord in contentLemmatized:
                # # calcul de la fréquence locale
                freqLocale = freqInDoc(searchedWord, contentLemmatized)
                # association de cette fréquence avec l'id du doc
                wordFreqLoc = dict()
                wordFreqLoc[docNo] = freqLocale
                # création d'une liste contenant tous les docs ayant le mot recherché avec sa fréquence
                if (wordFreqLoc[docNo] > 0): 
                    #print("fréq locale", wordFreqLoc)
                    #print("all fréq locale", allFreqLoc)
                    allFreqLoc.append(wordFreqLoc)
                    #print("all fréq locale", allFreqLoc)
                    # calcul de la fréquence globale
                    freqGlobale = freqGlobale + freqLocale
                    #print("fréq globale", freqGlobale)
                    indexInverse[searchedWord] = {freqGlobale : allFreqLoc}
                else:
                    continue
            break
        if len(indexInverse) > 0:
            print(indexInverse)
        print("Nombre total de fichiers traités:", docNo)
    print("Done")