"""Configuration pour le script d'autovote."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
# Chercher .env dans le répertoire racine du projet
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Essayer aussi de charger depuis le répertoire courant
    load_dotenv()

# Pseudo à utiliser pour les votes
PSEUDO = os.getenv("PSEUDO", "Wallans")

# Identifiants pour serveur-prive.net (si nécessaire)
SERVEUR_PRIVE_LOGIN = os.getenv("SERVEUR_PRIVE_LOGIN", "")
SERVEUR_PRIVE_PASSWORD = os.getenv("SERVEUR_PRIVE_PASSWORD", "")

# URLs de vote
VOTE_URLS = {
    "top_serveurs": "https://top-serveurs.net/minecraft/vote/excalia?pseudo={pseudo}",
    "serveur_prive": "https://serveur-prive.net/minecraft/excalia/vote",
    "serveur_minecraft_vote": "https://serveur-minecraft-vote.fr/serveurs/playexcaliafr-1214-calamity-update-s1.1718/vote",
    "serveur_minecraft": "https://serveur-minecraft.com/2168?pseudo={pseudo}",
}

# Configuration Selenium
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
WAIT_TIMEOUT = int(os.getenv("WAIT_TIMEOUT", "10"))

