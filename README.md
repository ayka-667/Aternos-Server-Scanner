# 🎯 Aternos Server Scanner
Un outil en Python pour scanner des serveurs Minecraft Aternos et détecter automatiquement ceux qui sont en ligne, hors ligne, ou en attente de démarrage. Idéal pour surveiller vos serveurs favoris ou découvrir ceux lancés par la communauté.

# ✅ Fonctionnalités

- **🔍 Scan automatique d'IP Aternos aléatoires**
- **📂 Lecture et scan depuis un fichier `servers.txt`**
- **📌 Détection des serveurs en attente** (offline mais enregistrés)
- **📄 Génération d’un fichier** `scan.txt` contenant les infos des serveurs en ligne
- **📁 Fichier** `waiting.txt` pour les serveurs en attente, non supprimé entre les sessions
- **🎨 Interface colorée et menu centré**
- **🧼 Nettoyage automatique du terminal entre chaque retour au menu**
- **💾 Ne réécrit pas les IP déjà présentes dans** `waiting.txt`

# 🖥️ Utilisation

**1. Lancer le script**

Avoir Python 3.7+ installé
Lance le script via un fichier `start.bat`
Ou manuellement dans le cmd :
```python script.py```

**2. Choix disponibles dans le menu**
```
 1 - Scanner 20 IP Aternos aléatoires
 2 - Scanner un nombre personnalisé d'IP aléatoires
 3 - Scanner les IP depuis 'servers.txt'
 4 - Rescanner les serveurs en attente
 5 - Quitter
```
> Appuyez sur Entrée pour revenir au menu à tout moment.

# 📁 Fichiers utilisés

- `servers.txt` : Liste d'IP à scanner (une par ligne)
- `waiting.txt` : IP des serveurs détectés comme "en attente" (non démarrés)
- `scan.txt` : Résultat du dernier scan des serveurs en ligne (effacé à chaque scan)

# 🛠️ Dépendances

Aucune bibliothèque externe nécessaire. Le script utilise uniquement des modules standards de Python (`socket`, `json`, `random`, etc.).

# 🤝 Contribution

Tu peux ouvrir une issue pour suggérer des idées ou corriger des bugs.
Pull requests bienvenues.
