# Création de votre environnement virtuel local.

Il est toujours plus pratique d'avoir un environnement virtuel spécifique à chaque projet.
VSCode permet de le créer facilement qu'on soit sous pip ou conda.

## Installation de l'environnement Jupyter sous VSCode.

La première étape consiste à se crére un environnement adapté à notre projet.
Pour cela sous VSCode appeler l'outil de création d'environnement virtuel.

    Shift-Meta-P "Python: Créer un environnement..."

et en fonction de votre gestionnaire d'environnement vous allez créer un nouvel environnement Python 3.11 .conda ou .venv

Ensuite il vous faudra charger chacun des packages nécessaires, pour cela on va construire un fichier "requirements.txt" minimal qu'il suffira d'intégrer.

En attendant vous pouvez charger directement chaque package dans votre environnement grâce à l'interpréteur de commande intégré.
Une fois l'environnement créé, il suffit de le sélectionner 

    Shift-Meta-P "Python: Sélectionner un interpréteur."

