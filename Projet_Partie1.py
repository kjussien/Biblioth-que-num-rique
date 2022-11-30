#!/usr/bin/python3
import epub 
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfReader
from pdfminer.pdfparser import PDFParser 
from pdfminer.pdfdocument import PDFDocument 
import os
from fpdf import FPDF
from pathlib import Path
import aspose.words as aw
import ebooklib.epub as ebl
from bs4 import BeautifulSoup as bs
from langdetect import detect

import logging
logging.basicConfig(filename='log.log', encoding='utf-8', level=10)
logging.basicConfig(format='%(asctime)s %(message)s')

class Livre():
    def __init__(self, livre):
        self.nom_fichier = livre
        #on regarde si le fichier est un pdf ou un epub sinon on lève une exception
        if livre.endswith('pdf'):
            self._pdf()
        elif livre.endswith('epub'):
            self._epub()
        else:
            raise ValueError("Impossible d'ouvrir le fichier")
   
    
    def _pdf(self):
        with open(f'livres/{self.nom_fichier}','rb') as f:
            pdf = PdfFileReader(f)
            metadata = pdf.getDocumentInfo()
            self.auteur = metadata.author if metadata.author else 'Inconnu'
            self.titre = metadata.title if metadata.title else 'Pas de titre'

            
            parser = PDFParser(f)
            document = PDFDocument(parser)
        
            tdm = []
            for (level, title, dest, a, structelem) in document.get_outlines(): #On recupère la table des matières
                tdm.append(f"{title}")
            self.tdm = ("\n".join(tdm))
            
                    #création du fichier au format txt
            with open(f'{self.titre}_tdm.txt','w') as f:
                f.write(self.tdm)

            self.doc_tdm()

            page = PdfReader(f'{self.titre}_tdm.pdf').pages[0]
            self.langue = detect(page.extract_text())
        
    def doc_tdm(self):

        #création du fichier au format pdf
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial",size=11)
        with open(f"{self.titre}_tdm.txt","r") as f:
            for x in f:
                x = x.replace("\u2019","'")
                x = x.replace("\u2013","-")
                pdf.cell(200, 10, txt = x, ln = 1, align = 'L')
        pdf.output(f"{self.titre}_tdm.pdf")  
        
        #création du fichier au format epub
        doc = aw.Document(f"{self.titre}_tdm.pdf")
        doc.save(f"{self.titre}_tdm.epub")
  
    
    def _epub(self):
        with epub.open_epub(f'livres/{self.nom_fichier}') as f:
            metadata = f.opf.metadata
            self.auteur = metadata.creators[0][0]
            self.titre = metadata.titles[0][0]
            self.langue = metadata.languages
            
            
            b = ebl.read_epub(f'livres/{self.nom_fichier}')

            tdm_xml = b.get_item_with_href("toc.ncx").get_content()
            tdm_parsed = bs(tdm_xml, features="xml").find_all("navPoint")
            tdm_parsed = list(map(  lambda x: x.find("text").text,tdm_parsed))

            with open(f"{self.titre}_tdm.txt","w") as f:
                f.write("\n".join(tdm_parsed))

            self.doc_tdm()


class Bibli():
    def __init__(self,fichier):
        self.liste_auteurs = dict()
        self.liste_livres = []
        dir_name = r'livres'        
        with open("rapport_livres.txt","w") as g:
            for livre in os.listdir(dir_name):
                    l = Livre(livre)
                    self.liste_livres.append(l)
                    for i in range(len(l.auteur)):
                        if l.auteur[i] in self.liste_auteurs:
                            self.liste_auteurs[l.auteur[i]].append(l.titre)
                        else :
                            self.liste_auteurs.update({l.auteur: [l.titre]})
                    g.write(f"{l.titre} :\n Auteur(s) : {l.auteur}\n Langue(s) : {l.langue}\n Nom du fichier : {l.nom_fichier}\n\n")

        with open("rapport_auteurs.txt","w") as f:
                for i in self.liste_auteurs.keys():
                    f.write(f"{i}:\n")
                    for j in self.liste_auteurs[i]:
                        f.write(f" -{j}\n\n")
                        
        self.rapport_livres()
        self.rapport_auteurs()
                   
      
                   
    def update(self,fichier):
        #On ajoute les nouveaux livres
        with open("fichier",'r') as f:
            for livre in f:
                if (livre in self.liste_livres)==False:#le livre n'est pas encore dans la liste
                    l = Livre(livre)
                    self.liste_livres.append(l)
                    logging.debug(f"{l.titre} ajouté")
                    with open("rapport_livres.txt","a") as g:
                        g.write(f"{l.titre} :\n Auteur(s) : {l.auteur}\n Langue(s) : {l.langue}\n Nom du fichier : {l.nom_livre}\n\n")
                    for i in range(len(l.auteur)):
                        if self.liste_auteurs[l.auteur[i]] in self.liste_auteurs :
                            self.liste_auteurs[l.auteur[i].append(l.titre)]
                            with open("rapport_auteurs.txt","a") as h:
                                l = next(h)
                                while l!="f{l.auteur}:\n}":
                                    l =next(h)
                                h.write(f" -{l.livre}\n\n")
                        else :
                            self.liste_auteurs.update({l.auteur[i]:l.titre})
                            with open("rapport_auteurs.txt","a") as h:
                                h.write(f"{l.auteur}:\n -{l.livre}\n\n")
        
         
        #On supprime les livres qui ne sont plus dans la bibliothèque
        for livre in self.liste_livres:
            if (os.path.exists(livre.nom_livre))==False:
                self.liste_livres.remove(livre)
                self.liste_auteurs[livre.auteur] = self.liste_auteurs[livre.auteur].remove(livre.titre)
                os.remove(f"{livre.titre}_tdm.txt")
                os.remove(f"{livre.titre}_tdm.epub")
                os.remove(f"{livre.titre}_tdm.pdf")
                
                logging.debug(f"{livre.titre} retiré")
                
            #On supprime le livre du rapport des livres
                #On cherche le nombre de ligne du fichier
                with open('rapport_livres.txt', 'r') as file :
                    nb_lines = len(file.readlines())
            
                #On cherche la position du livre à supprimer
                with open('rapport_livres.txt','r') as file:
                    l0 = next(file)
                    k = 1
                    while l0!=f"{livre.titre} :\n":
                        k = k+1
                        l0 = next(file)

                #On enlève les lignes le concernant
                with open('rapport_livres.txt','r') as file:
                    numero_ligne = 1
                    lines =[]
                    for i in range(nb_lines):
                        l=next(file)
                        if numero_ligne in [a for a in range(k,k+8)]:
                            numero_ligne = numero_ligne + 1

                        else:
                            lines.append(l)
                            numero_ligne = numero_ligne + 1
                
                with open('rapport_livres.txt', 'w') as file:
                    file.write("\r\n".join(lines))
        
                
            #On supprime le livre du rapport des auteurs
                with open('rapport_auteurs.txt','r') as file:
                    lines = []
                    l = next(file)
                    if l!=f" -{livre.titre}\n":
                        lines.append(l)
                        l = next(file)
                 
                with open('rapport_auteurs.txt', 'w') as file:
                    file.write("\r\n".join(lines))
                        
        self.rapport_livres()
        self.rapport_auteurs()
                
    def rapport_livres(self):             
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial",size=11)
        with open("rapport_livres.txt","r") as f:
            for x in f:
                x = x.replace("\u2019","'")
                pdf.cell(200, 10, txt = x, ln = 1, align = 'L')
        pdf.output("rapport_livres.pdf")
                    
        doc = aw.Document("rapport_livres.pdf")
        doc.save("rapport_livres.epub")
        
    def rapport_auteurs(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial",size=11)
        with open("rapport_auteurs.txt","r") as f:
            for x in f:
                x = x.replace("\u2019","'")
                pdf.cell(200, 10, txt = x, ln = 1, align = 'L')
        pdf.output("rapport_auteurs.pdf")
                    
        doc = aw.Document("rapport_livres.pdf")
        doc.save("rapport_livres.epub")






