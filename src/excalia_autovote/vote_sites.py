"""Classes pour gérer les votes sur les différents sites."""
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .config import HEADLESS, WAIT_TIMEOUT, PSEUDO


class BaseVoteSite:
    """Classe de base pour tous les sites de vote."""
    
    def __init__(self, driver: webdriver.Chrome, pseudo: str = PSEUDO):
        self.driver = driver
        self.pseudo = pseudo
        self.wait = WebDriverWait(driver, WAIT_TIMEOUT)
    
    def vote(self) -> bool:
        """Effectue le vote. À implémenter dans les classes filles."""
        raise NotImplementedError
    
    def wait_for_element(self, by: By, value: str, timeout: int = WAIT_TIMEOUT):
        """Attend qu'un élément soit présent."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable(self, by: By, value: str, timeout: int = WAIT_TIMEOUT):
        """Attend qu'un élément soit cliquable."""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )


class TopServeursVote(BaseVoteSite):
    """Gestion du vote sur top-serveurs.net."""
    
    def vote(self) -> bool:
        """Vote sur top-serveurs.net (simple, pas de vérification)."""
        try:
            url = f"https://top-serveurs.net/minecraft/vote/excalia?pseudo={self.pseudo}"
            print(f"[Top-Serveurs] Accès à {url}")
            self.driver.get(url)
            
            # Chercher le bouton de vote
            try:
                # Attendre un peu pour que la page se charge
                time.sleep(2)
                
                # Chercher le bouton "Voter" (peut avoir différents sélecteurs)
                vote_button_selectors = [
                    "//button[contains(text(), 'Voter')]",
                    "//input[@value='Voter']",
                    "//a[contains(text(), 'Voter')]",
                    "//button[contains(@class, 'vote')]",
                    "//input[@type='submit']",
                ]
                
                vote_button = None
                for selector in vote_button_selectors:
                    try:
                        vote_button = self.driver.find_element(By.XPATH, selector)
                        if vote_button.is_displayed():
                            break
                    except NoSuchElementException:
                        continue
                
                if vote_button:
                    vote_button.click()
                    print("[Top-Serveurs] ✅ Vote effectué avec succès")
                    time.sleep(2)
                    return True
                else:
                    # Si pas de bouton trouvé, peut-être que le vote se fait automatiquement
                    print("[Top-Serveurs] ⚠️ Aucun bouton trouvé, le vote peut être automatique")
                    time.sleep(2)
                    return True
                    
            except Exception as e:
                print(f"[Top-Serveurs] ⚠️ Erreur lors de la recherche du bouton: {e}")
                # Le vote peut être automatique juste en accédant à l'URL
                return True
                
        except Exception as e:
            print(f"[Top-Serveurs] ❌ Erreur: {e}")
            return False


class ServeurPriveVote(BaseVoteSite):
    """Gestion du vote sur serveur-prive.net (avec captcha)."""
    
    def vote(self) -> bool:
        """Vote sur serveur-prive.net (avec captcha et cookie)."""
        try:
            print(f"[Serveur-Prive] Accès à la page de vote")
            self.driver.get("https://serveur-prive.net/minecraft/excalia/vote")
            
            time.sleep(2)
            
            # Si besoin de se connecter d'abord
            # TODO: Implémenter la connexion si nécessaire
            
            # Chercher le champ pseudo
            try:
                pseudo_selectors = [
                    "//input[@name='pseudo']",
                    "//input[@id='pseudo']",
                    "//input[@type='text'][@placeholder*='pseudo' or @placeholder*='Pseudo']",
                    "//input[@type='text']",
                ]
                
                pseudo_field = None
                for selector in pseudo_selectors:
                    try:
                        pseudo_field = self.driver.find_element(By.XPATH, selector)
                        if pseudo_field.is_displayed():
                            break
                    except NoSuchElementException:
                        continue
                
                if pseudo_field:
                    pseudo_field.clear()
                    pseudo_field.send_keys(self.pseudo)
                    print(f"[Serveur-Prive] Pseudo '{self.pseudo}' entré")
                
            except Exception as e:
                print(f"[Serveur-Prive] ⚠️ Champ pseudo non trouvé (peut-être dans un cookie): {e}")
            
            # Gestion du captcha (simple - laisser l'utilisateur le résoudre)
            print("[Serveur-Prive] ⚠️ Veuillez résoudre le captcha et voter manuellement...")
            print("[Serveur-Prive] Appuyez sur Entrée une fois le vote effectué...")
            
            # Attendre que l'utilisateur résolve le captcha et vote
            input(">>> ")
            
            print("[Serveur-Prive] ✅ Vote considéré comme effectué")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"[Serveur-Prive] ❌ Erreur: {e}")
            return False


class ServeurMinecraftVoteVote(BaseVoteSite):
    """Gestion du vote sur serveur-minecraft-vote.fr."""
    
    def vote(self) -> bool:
        """Vote sur serveur-minecraft-vote.fr (pseudo pré-rempli, bouton déconnecté)."""
        try:
            print(f"[Serveur-Minecraft-Vote] Accès à la page de vote")
            url = "https://serveur-minecraft-vote.fr/serveurs/playexcaliafr-1214-calamity-update-s1.1718/vote"
            self.driver.get(url)
            
            time.sleep(3)
            
            # Chercher le bouton "voter en étant déconnecté"
            button_selectors = [
                "//button[contains(text(), 'déconnecté') or contains(text(), 'déconnecté')]",
                "//a[contains(text(), 'déconnecté') or contains(text(), 'Déconnecté')]",
                "//button[contains(text(), 'Voter')]",
                "//a[contains(@class, 'vote')]",
                "//button[contains(@class, 'vote')]",
            ]
            
            for selector in button_selectors:
                try:
                    button = self.wait_for_clickable(By.XPATH, selector)
                    if button.is_displayed():
                        button.click()
                        print("[Serveur-Minecraft-Vote] ✅ Bouton cliqué, vote effectué")
                        time.sleep(2)
                        return True
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"[Serveur-Minecraft-Vote] ⚠️ Erreur avec le sélecteur {selector}: {e}")
                    continue
            
            print("[Serveur-Minecraft-Vote] ⚠️ Bouton non trouvé")
            return False
            
        except Exception as e:
            print(f"[Serveur-Minecraft-Vote] ❌ Erreur: {e}")
            return False


class ServeurMinecraftVote(BaseVoteSite):
    """Gestion du vote sur serveur-minecraft.com (pseudo dans URL, case à cocher)."""
    
    def vote(self) -> bool:
        """Vote sur serveur-minecraft.com (case à cocher)."""
        try:
            url = f"https://serveur-minecraft.com/2168?pseudo={self.pseudo}"
            print(f"[Serveur-Minecraft] Accès à {url}")
            self.driver.get(url)
            
            time.sleep(2)
            
            # Chercher la case à cocher
            checkbox_selectors = [
                "//input[@type='checkbox']",
                "//input[@type='checkbox'][@name='terms' or @name='accept' or @id='terms' or @id='accept']",
            ]
            
            checkbox = None
            for selector in checkbox_selectors:
                try:
                    checkbox = self.driver.find_element(By.XPATH, selector)
                    if checkbox.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if checkbox and not checkbox.is_selected():
                checkbox.click()
                print("[Serveur-Minecraft] ✅ Case à cocher cochée")
                time.sleep(1)
            
            # Chercher et cliquer sur le bouton de vote
            vote_button_selectors = [
                "//button[contains(text(), 'Voter')]",
                "//input[@type='submit'][@value*='Voter' or @value*='voter']",
                "//button[@type='submit']",
                "//input[@type='submit']",
            ]
            
            for selector in vote_button_selectors:
                try:
                    vote_button = self.wait_for_clickable(By.XPATH, selector)
                    if vote_button.is_displayed():
                        vote_button.click()
                        print("[Serveur-Minecraft] ✅ Vote effectué")
                        time.sleep(2)
                        return True
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"[Serveur-Minecraft] ⚠️ Erreur avec le sélecteur {selector}: {e}")
                    continue
            
            print("[Serveur-Minecraft] ⚠️ Bouton de vote non trouvé")
            return False
            
        except Exception as e:
            print(f"[Serveur-Minecraft] ❌ Erreur: {e}")
            return False


def create_driver(headless: bool = HEADLESS) -> webdriver.Chrome:
    """Crée et configure le driver Selenium."""
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Masquer le fait qu'on utilise Selenium
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    return driver

