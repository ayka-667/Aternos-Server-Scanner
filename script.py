import os
import random
import re
import time
from mcstatus import JavaServer
from colorama import init, Fore, Style
import socket

init(autoreset=True)

class Couleurs:
    BLEU = Fore.CYAN
    VERT = Fore.LIGHTGREEN_EX
    JAUNE = Fore.LIGHTYELLOW_EX
    ROUGE = Fore.LIGHTRED_EX
    BLANC = Fore.WHITE
    RESET = Style.RESET_ALL
    GRAS = Style.BRIGHT

HUB_KEYWORDS = [
    "this server is offline",
    "get this server more ram",
    "craft.link/ram",
    "starting server",
    "server is offline",
    "please wait",
    "wake up",
    "en file d'attente",
    "démarrage en cours",
    "hub", "lobby",
    "aternos", "exaroton"
]

FICHIER_ATTENTE = "waiting.txt"
FICHIER_SCAN = "scan.txt"
FICHIER_SERVERS = "servers.txt"

serveurs_en_ligne = []
serveurs_en_attente = []

def generer_ips_aternos(nombre=10):
    prefixes = [
        "Survival", "Skyblock", "SMP", "Bedwars", "Anarchy", "Creative",
        "Factions", "Hardcore", "PvP", "Roleplay", "MiniGames", "FactionSMP"
    ]
    suffixes = [
        "Network", "World", "Realm", "Hub", "Craft", "Universe", "MC",
        "Empire", "Kingdom", "Nation", "Legends", "Adventures"
    ]
    ips = []
    for _ in range(nombre):
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        ip = f"{prefix}{suffix}.aternos.me"
        ips.append(ip)
    return ips

def is_hub_motd(motd: str) -> bool:
    motd_lower = motd.lower()
    return any(mot in motd_lower for mot in HUB_KEYWORDS)

def is_server_actif(motd_texte):
    messages_inactifs = [
        "server not found",
        "server offline",
        "offline",
        "failed to query",
        "connection refused"
    ]
    motd_min = motd_texte.lower()
    return not any(msg in motd_min for msg in messages_inactifs)

def nettoyer_motd(motd_texte):
    return re.sub(r"§.", "", motd_texte)

def extraire_texte_motd(motd):
    if hasattr(motd, 'raw') and isinstance(motd.raw, dict):
        texte = motd.raw.get('text', '') or str(motd)
    else:
        texte = str(motd)
    return nettoyer_motd(texte)

def ajouter_serveur_attente(ip):
    if not os.path.exists(FICHIER_ATTENTE):
        with open(FICHIER_ATTENTE, "w", encoding="utf-8") as f:
            f.write(ip + "\n")
        return

    with open(FICHIER_ATTENTE, "r", encoding="utf-8") as f:
        lignes = [line.strip() for line in f.readlines()]

    if ip not in lignes:
        with open(FICHIER_ATTENTE, "a", encoding="utf-8") as f:
            f.write(ip + "\n")

def lire_ips_fichier(nom_fichier=FICHIER_SERVERS):
    if not os.path.isfile(nom_fichier):
        print(f"{Couleurs.ROUGE}Le fichier '{nom_fichier}' est introuvable.{Couleurs.RESET}")
        return []
    with open(nom_fichier, "r", encoding="utf-8") as fichier:
        lignes = fichier.readlines()
    ips = [ligne.strip() for ligne in lignes if ligne.strip()]
    return ips

def ecrire_scan_file(serveurs):
    with open(FICHIER_SCAN, "w", encoding="utf-8") as f:
        f.write("Liste des serveurs en ligne détectés lors du dernier scan :\n\n")
        if not serveurs:
            f.write("Aucun serveur actif détecté.\n")
            return
        for srv in serveurs:
            f.write(f"IP      : {srv['ip']}\n")
            f.write(f"Version : {srv.get('version', 'N/A')}\n")
            f.write(f"Joueurs : {srv['players']}\n")
            f.write(f"Nom     : {srv['motd']}\n")
            f.write("-" * 40 + "\n")

def try_scanner_ip(ip, sauvegarder_attente=True):
    tentatives = 0
    while tentatives < 2:
        try:
            serveur = JavaServer.lookup(ip)
            statut = serveur.status()
            motd = statut.motd
            motd_texte = extraire_texte_motd(motd)
            joueurs = statut.players
            version = statut.version.name if statut.version else "Inconnu"

            if is_hub_motd(motd_texte):
                print(f"{Couleurs.JAUNE}EN ATTENTE : {ip}{Couleurs.RESET}")
                if sauvegarder_attente:
                    ajouter_serveur_attente(ip)
                serveurs_en_attente.append(ip)
            elif is_server_actif(motd_texte):
                print(f"{Couleurs.VERT}EN LIGNE   : {ip} ({joueurs.online}/{joueurs.max} joueurs) - {motd_texte}{Couleurs.RESET}")
                serveurs_en_ligne.append({
                    "ip": ip,
                    "motd": motd_texte,
                    "players": f"{joueurs.online}/{joueurs.max}",
                    "version": version
                })
            else:
                print(f"{Couleurs.ROUGE}INACTIF    : {ip} - MOTD : {motd_texte}{Couleurs.RESET}")
            return
        except Exception as e:
            if isinstance(e, (socket.timeout, TimeoutError)):
                tentatives += 1
                if tentatives == 2:
                    print(f"{Couleurs.ROUGE}TIMEOUT   : {ip} après 2 tentatives{Couleurs.RESET}")
                else:
                    print(f"{Couleurs.JAUNE}Timeout, nouvelle tentative pour {ip}...{Couleurs.RESET}")
                    time.sleep(1)
            else:
                print(f"{Couleurs.ROUGE}ERREUR    : {ip} ({e}){Couleurs.RESET}")
                return

def afficher_header():
    print(Couleurs.BLEU + "╔" + "═"*50 + "╗")
    print(Couleurs.BLEU + "║" + Couleurs.GRAS + "        SCANNEUR ATERNOS  - by Ayka               " + Couleurs.BLEU + "║")
    print(Couleurs.BLEU + "╚" + "═"*50 + "╝" + Couleurs.RESET)

def afficher_menu():
    print()
    print(f"{Couleurs.BLEU} 1{Couleurs.RESET} - Scanner 20 IP Aternos aléatoires")
    print(f"{Couleurs.BLEU} 2{Couleurs.RESET} - Scanner un nombre personnalisé d'IP aléatoires")
    print(f"{Couleurs.BLEU} 3{Couleurs.RESET} - Scanner les IP depuis 'servers.txt'")
    print(f"{Couleurs.BLEU} 4{Couleurs.RESET} - Rescanner les serveurs en attente")
    print(f"{Couleurs.BLEU} 5{Couleurs.RESET} - Quitter")
    print()

def lancer_scan(ips, sauvegarder_attente=True, purge_servers_txt=False):
    global serveurs_en_ligne, serveurs_en_attente
    serveurs_en_ligne = []
    serveurs_en_attente = []

    print(f"\n{Couleurs.JAUNE} Début du scan de {len(ips)} serveurs...{Couleurs.RESET}\n")
    for i, ip in enumerate(ips, 1):
        print(f"{Couleurs.BLEU} [{i}/{len(ips)}]{Couleurs.RESET} ", end="")
        try_scanner_ip(ip, sauvegarder_attente=sauvegarder_attente)

    print(f"\n{Couleurs.VERT}Scan terminé.{Couleurs.RESET}\n")
    print(f"{Couleurs.BLEU}Serveurs en ligne détectés :{Couleurs.RESET}")
    if serveurs_en_ligne:
        for srv in serveurs_en_ligne:
            print(f" - {srv['ip']} | {srv['motd']} | Joueurs : {srv['players']}")
    else:
        print("Aucun serveur actif détecté.")

    ecrire_scan_file(serveurs_en_ligne)

    if purge_servers_txt:
        ips_valides_et_attente = set(serveurs_en_attente)
        ips_valides_et_attente.update([srv["ip"] for srv in serveurs_en_ligne])

        with open(FICHIER_SERVERS, "w", encoding="utf-8") as f:
            for ip in sorted(ips_valides_et_attente):
                f.write(ip + "\n")
        print(f"\n{Couleurs.JAUNE}Mise à jour de '{FICHIER_SERVERS}' effectuée : seuls les serveurs valides et en attente sont conservés.{Couleurs.RESET}")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear_console()
        afficher_header()
        afficher_menu()
        choix = input(f"{Couleurs.JAUNE} Choisissez une option : {Couleurs.RESET}").strip()

        if choix == "1":
            ips = generer_ips_aternos(nombre=20)
            lancer_scan(ips)
            input(f"\n{Couleurs.JAUNE}Appuyez sur Entrée pour revenir au menu...{Couleurs.RESET}")
        elif choix == "2":
            n = input(f"{Couleurs.JAUNE}Combien d'IP voulez-vous scanner ? {Couleurs.RESET}")
            try:
                n = int(n)
                if n <= 0:
                    print(f"{Couleurs.ROUGE}Veuillez saisir un nombre supérieur à 0.{Couleurs.RESET}")
                    input("\nAppuyez sur Entrée pour revenir au menu...")
                    continue
                ips = generer_ips_aternos(nombre=n)
                lancer_scan(ips)
                input(f"\n{Couleurs.JAUNE}Appuyez sur Entrée pour revenir au menu...{Couleurs.RESET}")
            except ValueError:
                print(f"{Couleurs.ROUGE}Entrée invalide. Veuillez saisir un nombre.{Couleurs.RESET}")
                input("\nAppuyez sur Entrée pour revenir au menu...")
        elif choix == "3":
            ips = lire_ips_fichier()
            if ips:
                lancer_scan(ips, purge_servers_txt=True)
            input(f"\n{Couleurs.JAUNE}Appuyez sur Entrée pour revenir au menu...{Couleurs.RESET}")
        elif choix == "4":
            ips = lire_ips_fichier(FICHIER_ATTENTE)
            if ips:
                print(f"\n{Couleurs.JAUNE}Rescan des serveurs en attente dans '{FICHIER_ATTENTE}' ({len(ips)} serveurs)...{Couleurs.RESET}\n")
                lancer_scan(ips, sauvegarder_attente=False)
            else:
                print(f"{Couleurs.ROUGE}Aucun serveur en attente à rescanner.{Couleurs.RESET}")
            input(f"\n{Couleurs.JAUNE}Appuyez sur Entrée pour revenir au menu...{Couleurs.RESET}")
        elif choix == "5":
            print(f"{Couleurs.BLEU}Au revoir !{Couleurs.RESET}")
            break
        else:
            print(f"{Couleurs.ROUGE}Option invalide. Réessayez.{Couleurs.RESET}")
            input(f"\nAppuyez sur Entrée pour revenir au menu...")

if __name__ == "__main__":
    main()
