# Excalia Autovote

Script Python pour automatiser les votes sur plusieurs sites de classement de serveurs Minecraft.

## 🚀 Installation

### Prérequis

- Python 3.13 ou supérieur
- Google Chrome installé sur votre système (Selenium utilise ChromeDriver qui sera installé automatiquement)

### Installation des dépendances

1. Installer les dépendances :
```bash
pip install -e .
```

Ou avec Poetry :
```bash
poetry install
```

## ⚙️ Configuration

1. Copier le fichier `env.example` vers `.env` :
```bash
cp env.example .env
```

2. Éditer le fichier `.env` et configurer :
   - `PSEUDO` : Votre pseudo Minecraft
   - `SERVEUR_PRIVE_LOGIN` : Login pour serveur-prive.net (si nécessaire)
   - `SERVEUR_PRIVE_PASSWORD` : Mot de passe pour serveur-prive.net (si nécessaire)
   - `HEADLESS` : `True` pour un navigateur invisible, `False` pour voir le navigateur
   - `WAIT_TIMEOUT` : Timeout en secondes pour les attentes Selenium

## 📋 Sites supportés

1. **Top-Serveurs.net** - Simple, pas de vérification
2. **Serveur-Prive.net** - Avec captcha simple (résolution manuelle)
3. **Serveur-Minecraft-Vote.fr** - Pseudo pré-rempli, bouton "voter en étant déconnecté"
4. **Serveur-Minecraft.com** - Pseudo dans l'URL, case à cocher

## 🎯 Utilisation

Lancer le script :
```bash
python -m excalia_autovote.main
```

Ou avec Poetry :
```bash
poetry run python -m excalia_autovote.main
```

## ⚠️ Notes importantes

- Pour **Serveur-Prive.net**, le script s'arrêtera pour vous permettre de résoudre le captcha manuellement. Appuyez sur Entrée une fois terminé.
- Assurez-vous d'avoir Chrome installé sur votre système (Selenium utilise ChromeDriver).
- Respectez les conditions d'utilisation des sites de vote.

## 📝 Structure du projet

```
excalia-autovote/
├── src/
│   └── excalia_autovote/
│       ├── __init__.py
│       ├── config.py          # Configuration
│       ├── vote_sites.py      # Classes pour chaque site
│       └── main.py            # Script principal
├── env.example                # Exemple de configuration
├── pyproject.toml
└── README.md
```

