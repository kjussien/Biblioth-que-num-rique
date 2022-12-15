#!/usr/bin/python3

from Projet_Partie1 import Livre, Bibli
import sys

if __name__ == "__main__":
    if(sys.argv[1])=='init':
        Bibli = Bibli(f"\livres")
    elif(sys.argv[1])=='update':
        Bibli.update(f"\livres")
