"""Classes pour gérer les votes sur les différents sites."""
import os
import platform
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
    
    def _accept_cookies(self) -> bool:
        """Accepte le pop-up de cookies en cliquant sur 'autoriser'."""
        try:
            print("[Top-Serveurs] Recherche du pop-up de cookies...")
            time.sleep(3)
            
            # Chercher le bouton "autoriser" (texte spécifique pour top-serveurs.net)
            button_texts = ['autoriser', 'Autoriser', 'AUTORISER']
            
            # Méthode 1 : Chercher par texte exact
            for text in button_texts:
                try:
                    xpath = f"//button[contains(text(), '{text}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                print(f"[Top-Serveurs] Bouton 'autoriser' trouvé: {element.text}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].click();", element)
                                print("[Top-Serveurs] ✅ Cookies autorisés")
                                time.sleep(2)
                                return True
                        except Exception:
                            continue
                except Exception:
                    continue
            
            # Méthode 2 : Chercher tous les boutons et filtrer par texte
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in all_buttons:
                    try:
                        if button.is_displayed() and button.is_enabled():
                            text = button.text.strip()
                            if any(word.lower() in text.lower() for word in ['autoriser', 'autoriser']):
                                print(f"[Top-Serveurs] Bouton 'autoriser' trouvé (tous les boutons): {text}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].click();", button)
                                print("[Top-Serveurs] ✅ Cookies autorisés")
                                time.sleep(2)
                                return True
                    except Exception:
                        continue
            except Exception:
                pass
            
            # Méthode 3 : Chercher avec XPath insensible à la casse
            try:
                xpath_insensitive = "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'autoriser')]"
                elements = self.driver.find_elements(By.XPATH, xpath_insensitive)
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            print(f"[Top-Serveurs] Bouton 'autoriser' trouvé (insensible casse): {element.text}")
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", element)
                            print("[Top-Serveurs] ✅ Cookies autorisés")
                            time.sleep(2)
                            return True
                    except Exception:
                        continue
            except Exception:
                pass
            
            # Méthode 4 : Essayer aussi avec "accepter" au cas où
            fallback_texts = ['accepter', 'Accepter', 'accept', 'Accept']
            for text in fallback_texts:
                try:
                    xpath = f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        try:
                            if element.is_displayed() and element.is_enabled():
                                print(f"[Top-Serveurs] Bouton cookie trouvé (fallback): {element.text}")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                self.driver.execute_script("arguments[0].click();", element)
                                print("[Top-Serveurs] ✅ Cookies acceptés")
                                time.sleep(2)
                                return True
                        except Exception:
                            continue
                except Exception:
                    continue
            
            print("[Top-Serveurs] ⚠️ Bouton 'autoriser' non trouvé automatiquement")
            return False
            
        except Exception as e:
            print(f"[Top-Serveurs] ⚠️ Erreur lors de l'acceptation des cookies: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _handle_cloudflare(self) -> bool:
        """Gère le captcha Cloudflare (Turnstile) - attend passivement la validation automatique."""
        try:
            print("[Top-Serveurs] Vérification du défi Cloudflare...")
            time.sleep(3)
            
            # Chercher l'iframe Cloudflare Turnstile
            cloudflare_selectors = [
                "//iframe[contains(@src, 'challenges.cloudflare.com')]",
                "//iframe[contains(@src, 'cloudflare')]",
                "//iframe[contains(@src, 'turnstile')]",
                "//iframe[contains(@id, 'cf-')]",
                "//iframe[contains(@name, 'cf-')]",
                "//iframe[@title*='challenge']",
                "//iframe[@title*='Widget']",
            ]
            
            iframe = None
            for selector in cloudflare_selectors:
                try:
                    iframes = self.driver.find_elements(By.XPATH, selector)
                    for iframe_elem in iframes:
                        try:
                            if iframe_elem.is_displayed():
                                iframe = iframe_elem
                                iframe_src = iframe_elem.get_attribute('src')
                                print(f"[Top-Serveurs] Iframe Cloudflare détectée: {iframe_src[:50] if iframe_src else 'N/A'}...")
                                break
                        except:
                            continue
                    if iframe:
                        break
                except Exception:
                    continue
            
            if iframe:
                print("[Top-Serveurs] Défi Cloudflare détecté - attente passive de la validation...")
                print("[Top-Serveurs] 💡 Ne pas interagir avec la page, laisser Cloudflare se valider automatiquement...")
                
                # Attendre PASSIVEMENT que Cloudflare se valide (ne rien faire, juste attendre)
                # Vérifier si le bouton de vote devient actif (disabled disparaît)
                max_wait = 60  # Attendre jusqu'à 60 secondes
                initial_url = self.driver.current_url
                
                for i in range(max_wait):
                    try:
                        # Vérifier si le bouton de vote est activé (pas disabled)
                        vote_button = self.driver.find_element(By.ID, "btnSubmitVote")
                        if vote_button.is_enabled():
                            print("[Top-Serveurs] ✅ Bouton de vote activé - Cloudflare validé")
                            time.sleep(2)
                            return True
                    except (NoSuchElementException, Exception):
                        # Le bouton n'existe pas encore ou n'est pas activé
                        pass
                    
                    # Vérifier aussi si l'iframe a disparu
                    try:
                        self.driver.find_element(By.XPATH, "//iframe[contains(@src, 'challenges.cloudflare.com')]")
                        # L'iframe existe encore, continuer à attendre
                    except NoSuchElementException:
                        # L'iframe a disparu, Cloudflare est probablement validé
                        print("[Top-Serveurs] ✅ Iframe Cloudflare disparue - validation probable")
                        time.sleep(2)
                        return True
                    
                    # Vérifier si l'URL a changé (rechargement de page)
                    current_url = self.driver.current_url
                    if current_url != initial_url:
                        print("[Top-Serveurs] ✅ Page rechargée - Cloudflare validé")
                        time.sleep(3)
                        return True
                    
                    # Attendre 1 seconde avant de revérifier
                    time.sleep(1)
                    if i % 10 == 0 and i > 0:
                        print(f"[Top-Serveurs] ⏳ Attente Cloudflare... ({i}/{max_wait}s)")
                
                print("[Top-Serveurs] ⚠️ Timeout lors de l'attente de Cloudflare")
                return False
            else:
                print("[Top-Serveurs] Aucun défi Cloudflare détecté")
                return True
                
        except Exception as e:
            print(f"[Top-Serveurs] ⚠️ Erreur lors de la gestion Cloudflare: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def vote(self) -> bool:
        """Vote sur top-serveurs.net (avec gestion cookies et Cloudflare)."""
        try:
            url = f"https://top-serveurs.net/minecraft/vote/excalia?pseudo={self.pseudo}"
            print(f"[Top-Serveurs] Accès à {url}")
            self.driver.get(url)
            
            # Attendre le chargement initial
            time.sleep(5)
            
            # 1. Accepter les cookies (cliquer sur "autoriser")
            cookies_accepted = self._accept_cookies()
            if not cookies_accepted:
                print("[Top-Serveurs] ⚠️ Bouton 'autoriser' non trouvé automatiquement")
                print("[Top-Serveurs] 💡 Veuillez cliquer sur 'autoriser' manuellement")
                print("[Top-Serveurs] 💡 Appuyez sur Entrée pour continuer...")
                input(">>> ")
            time.sleep(2)
            
            # 2. Définir le cookie vote_player avec le pseudo (AVANT Cloudflare)
            try:
                print(f"[Top-Serveurs] Définition du cookie 'vote_player' avec la valeur '{self.pseudo}'")
                self.driver.add_cookie({
                    'name': 'vote_player',
                    'value': self.pseudo,
                    'domain': 'top-serveurs.net',
                    'path': '/'
                })
                print("[Top-Serveurs] ✅ Cookie 'vote_player' défini")
                # Ne PAS recharger la page maintenant, attendre que Cloudflare se valide
            except Exception as e:
                print(f"[Top-Serveurs] ⚠️ Erreur lors de la définition du cookie: {e}")
            
            # 3. Gérer Cloudflare - attendre passivement qu'il se valide
            cloudflare_resolved = self._handle_cloudflare()
            
            if not cloudflare_resolved:
                print("[Top-Serveurs] ❌ Cloudflare non résolu - le vote ne peut pas continuer")
                return False
            
            # Après que Cloudflare soit validé, recharger pour appliquer le cookie
            print("[Top-Serveurs] Rechargement de la page pour appliquer le cookie...")
            self.driver.refresh()
            time.sleep(4)
            
            # 4. Chercher et cliquer sur le bouton de vote (ID: btnSubmitVote)
            print("[Top-Serveurs] Recherche du bouton de vote...")
            vote_button = None
            
            # Essayer d'abord avec l'ID spécifique
            try:
                vote_button = self.wait_for_clickable(By.ID, "btnSubmitVote", timeout=10)
                if vote_button.is_displayed():
                    print("[Top-Serveurs] Bouton de vote trouvé (ID: btnSubmitVote)")
            except (TimeoutException, NoSuchElementException):
                print("[Top-Serveurs] Bouton avec ID 'btnSubmitVote' non trouvé, recherche alternative...")
                # Fallback sur d'autres sélecteurs
                vote_button_selectors = [
                    "//button[@id='btnSubmitVote']",
                    "//button[contains(text(), 'Voter')]",
                    "//input[@value='Voter']",
                    "//a[contains(text(), 'Voter')]",
                    "//button[contains(@class, 'vote')]",
                    "//input[@type='submit']",
                    "//form//button[@type='submit']",
                ]
                
                for selector in vote_button_selectors:
                    try:
                        vote_button = self.wait_for_clickable(By.XPATH, selector, timeout=5)
                        if vote_button.is_displayed():
                            break
                    except (TimeoutException, NoSuchElementException):
                        continue
            
            if vote_button:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", vote_button)
                time.sleep(0.5)
                vote_button.click()
                print("[Top-Serveurs] ✅ Vote effectué avec succès")
                time.sleep(3)
                return True
            else:
                print("[Top-Serveurs] ⚠️ Bouton de vote non trouvé")
                return False
                
        except Exception as e:
            print(f"[Top-Serveurs] ❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
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
    """Crée et configure le driver Selenium avec undetected-chromedriver."""
    try:
        import undetected_chromedriver as uc
        
        # Utiliser undetected-chromedriver pour éviter la détection (notamment Cloudflare)
        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Forcer l'utilisation de Chrome (pas Edge)
        # Chercher Chrome dans les emplacements courants
        chrome_paths = []
        if platform.system() == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
        elif platform.system() == "Darwin":  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
        else:  # Linux
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ]
        
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                break
        
        if chrome_binary:
            options.binary_location = chrome_binary
            print(f"🔍 Utilisation de Chrome trouvé à: {chrome_binary}")
        else:
            print("⚠️ Chrome non trouvé dans les emplacements standard, utilisation par défaut")
        
        driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)
        print("✅ Navigateur Chrome initialisé (undetected-chromedriver)")
        return driver
        
    except ImportError:
        # Fallback sur Selenium standard si undetected-chromedriver n'est pas disponible
        print("⚠️ undetected-chromedriver non disponible, utilisation de Selenium standard")
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if headless:
            options.add_argument("--headless=new")
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

