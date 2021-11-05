import urllib.request
from bs4 import BeautifulSoup
from tika import parser
import re

class Prisme():
    
    def __init__(self, traitement):
        if not isinstance(traitement, Traitement):
            raise TypeError("Un prisme prend un traitement en argument")
        self.t = traitement
        
    def run(self, fichier):
        lecture = open(fichier, 'r')
        liste = []
        for ligne in lecture:                                  #On nettoie les urls et on les ajoutes à la liste d'urls collectées
            url = re.sub(r'\n', '', ligne)
            liste.append(url)
        collecte = Collecte(liste)
        if self.t.donnee == "texte":                           #on vérifie si le traitement porte sur du texte
            collecte.run()                                     #on collecte le texte des urls
            self.t.load(collecte.content())                    #on charge les textes dans le traitement
            self.t.run()                                       #on lance le traitement
    
    def show(self):
        self.t.show()
        
    
class Collecte():
    
    def __init__(self, liste):
        if type(liste) is not list:
            raise TypeError("Une collecte prend une liste en argument")
        self.l = liste
        self.result = []
        
    def run(self, donnee="texte"):
        if donnee != "texte" and donnee != "image":
            raise ValueError("Indiquez \"texte\" ou \"image\"")
        self.result = []
        for url in self.l:                                         #pour chaque url de la liste
            ressource = Ressource(url)                             #on crée la ressource correspondante
            if donnee == "texte":
                self.result.append(ressource.text())
    
    def content(self):
        return self.result

    
class Ressource():
    
    def __init__(self, url):
        if type(url) is not str:
            raise TypeError("L'url doit être donnée comme une chaine de charactères")
        self.url = url
        if url[-5:] == ".html":
            self.donnee = "HTML"
        if url[-4:] == ".pdf":
            self.donnee = "PDF"
    
    def type(self):
        return self.donnee
    
    def text(self):
        if self.donnee == "PDF":                                                                  #si l'url envoie vers un pdf
            texte = parser.from_file(self.url)['content']                                         #on en extrait le texte à l'aide d'un parser pdf
        if self.donnee == "HTML":                                                                 #si l'url envoie vers une page html
            soup = BeautifulSoup(urllib.request.urlopen(self.url).read(), features="html.parser") #on en extrait le texte à l'aide d'un parser html
            for nontexte in soup(["script", "style"]):                                            #on supprime ce qui ne nous intéresse pas
                nontexte.extract()
            texte = soup.get_text()
                                                                                                  #on "nettoie" le texte
        lignes = (ligne.strip() for ligne in texte.splitlines())
        chunks = (phrase.strip() for ligne in lignes for phrase in ligne.split("  "))
        texte = ' '.join(chunk for chunk in chunks if chunk)
        return(texte)
    
class Traitement():
    
    def __init__(self):
        self.données = []
    
    def load(self, liste):
        self.données = liste


class Traitementtrivial(Traitement):
    
    def __init__(self):
        self.données = []
        self.donnee = "texte"
        self.result = None
    
    def run(self):
        non_mot = [' ', ',', '.', ';', ':', '!', '\'', '(', ')', '[', ']', '/', '-', '*', '\'', '\"', '#', '…', '’']
        comptage = {}
        m = 1
        mot = ''
        for texte in self.données:
            for char in range(len(texte)):
                if m == 0 and texte[char] in non_mot:
                    m = 1
                    if mot in comptage:
                        comptage[mot]+=1
                    else:
                        comptage[mot]=1
                    mot = ''
                if m == 0 and texte[char] not in non_mot:
                    mot+=texte[char]
                if m == 1 and texte[char] not in non_mot:
                    m = 0
                    mot+=texte[char]
        self.result = comptage


class Traitementtrivialalpha(Traitementtrivial):
    
    def show(self):
        c = 0
        for mot in self.result:
            c+=self.result[mot]
        print(sorted(self.result.items(), key=lambda t: t[0]))
        print(f'Le nombre de mots total est {c}')

class Traitementtrivialnum(Traitementtrivial):
    
    def show(self):
        c = 0
        for mot in self.result:
            c+=self.result[mot]
        print(sorted(self.result.items(), key=lambda t: t[1]))
        print(f'Le nombre de mots total est {c}')
