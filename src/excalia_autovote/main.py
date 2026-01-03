"""Script principal pour l'autovote."""
import sys
import time
from selenium import webdriver
from .vote_sites import (
    TopServeursVote,
    ServeurPriveVote,
    ServeurMinecraftVoteVote,
    ServeurMinecraftVote,
    create_driver,
)
from .config import PSEUDO, HEADLESS


def main():
    """Fonction principale."""
    print("=" * 60)
    print("🎮 Script d'Autovote pour Excalia")
    print("=" * 60)
    print(f"Pseudo utilisé: {PSEUDO}")
    print(f"Mode headless: {HEADLESS}")
    print("=" * 60)
    print()
    
    driver = None
    results = {}
    
    try:
        # Créer le driver Selenium
        print("🔧 Initialisation du navigateur...")
        driver = create_driver(headless=HEADLESS)
        print("✅ Navigateur initialisé\n")
        
        # Liste des sites à voter (dans l'ordre)
        vote_sites = [
            ("Top-Serveurs", TopServeursVote(driver, PSEUDO)),
            ("Serveur-Prive", ServeurPriveVote(driver, PSEUDO)),
            ("Serveur-Minecraft-Vote", ServeurMinecraftVoteVote(driver, PSEUDO)),
            ("Serveur-Minecraft", ServeurMinecraftVote(driver, PSEUDO)),
        ]
        
        # Effectuer les votes
        for site_name, vote_handler in vote_sites:
            print(f"\n{'='*60}")
            print(f"📊 Site: {site_name}")
            print(f"{'='*60}")
            
            try:
                success = vote_handler.vote()
                results[site_name] = success
                
                if success:
                    print(f"✅ {site_name}: Succès")
                else:
                    print(f"❌ {site_name}: Échec")
                    
            except KeyboardInterrupt:
                print(f"\n⚠️ Interruption utilisateur lors du vote sur {site_name}")
                results[site_name] = False
                break
            except Exception as e:
                print(f"❌ {site_name}: Erreur - {e}")
                results[site_name] = False
            
            # Pause entre les sites
            if vote_sites.index((site_name, vote_handler)) < len(vote_sites) - 1:
                print("\n⏳ Pause de 3 secondes avant le prochain site...")
                time.sleep(3)
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES VOTES")
        print("=" * 60)
        for site_name, success in results.items():
            status = "✅ Succès" if success else "❌ Échec"
            print(f"{site_name}: {status}")
        print("=" * 60)
        
        success_count = sum(1 for s in results.values() if s)
        print(f"\nTotal: {success_count}/{len(results)} votes réussis")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            print("\n🔒 Fermeture du navigateur...")
            driver.quit()
            print("✅ Navigateur fermé")
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

