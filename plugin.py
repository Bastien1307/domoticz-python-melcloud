# MELCloud Plugin
# Author: Gysmo/schurgan/Dalonsic/ChatGPT/Claude/Bastien1307, 07.2026
# Version: 2.1.1
#
# Release Notes:
# v2.1.1: Robustesse de l'intervalle cloud (Mode2) : un champ vide/invalide ne
#         plante plus onStart (int('') -> exception), repli 120s comme Mode1.
# v2.1.0: Interface créée au runtime traduite en français si Language = Français
#         (noms de devices et libellés des sélecteurs : modes, ventilation,
#         vannes, verrou télécommande, compteurs). Toute autre langue = anglais.
#         Le formulaire de config reste en anglais (labels figés par Domoticz).
# v2.0.0: Contrôle LOCAL d'abord (adaptateur MAC-577IF-2E via lib vendorée
#         pymitsubishi/), cloud MELCloud en secours. Découverte des IP par MAC
#         (ARP + scan), cache persisté (fonctionne sans internet), température
#         distante par clim (Mode5 : MAC=idx thermomètre) arrondie au pas de 0,5°
#         selon le mode (sup. en froid/sec, inf. en chaud), puissance instantanée
#         réelle dans les compteurs kWh, verrou télécommande (Unit 200+) levé
#         physiquement à l'arrêt du plugin et ré-appliqué au démarrage.
#         Icônes résolues PAR NOM (plus aucun ID en dur) : icônes existantes de
#         l'install si présentes, sinon zips embarqués icons/<Base>.zip (un par
#         icône) via Domoticz.Image ; repli icône standard (7) en dernier recours.
#         Détection console/mural par modèle (MFZ* = console) au lieu du nom.
#         Voir ReleaseNotes.md pour le détail.
# v1.1.0: Consigne en vrai Thermostat (0,5°), fin du flapping Marche/Arrêt et des
#         crashes SIGABRT, compteurs kWh par clim et par groupe extérieur, GMT
#         Offset supprimé (DST auto), device témoin internet, backoff API.
# v1.0.0: Endversion, code Optimierung/Säuberung. (schurgan — base de ce fork)
# v0.9.0: Stabiler JSON-SET, Rate-Limit für UNIT_INFO, Fix Heartbeat / Race Conditions
# v0.8.0: Heartbeat Interval + Spracheinstellung
# v0.7.9: Fehlerbeseitigung Zeile 116 und 330
# v0.7.8: Code optimization
# v0.7.7: Add test on domoticz dummy
# v0.7.6: Fix Auto Mode added
# v0.7.5: Fix somes bugs and improve https connection
# v0.7.4: Sometimes update fail. Update function sync to avoid this
# v0.7.3: Add test in login process and give message if there is some errors
# v0.7.2: Correct bug for onDisconnect, add timeoffset and add update time for last command in switch text
# v0.7.1: Correct bug with power on and power off
# v0.7 : Use builtin https support to avoid urllib segmentation fault on binaries
# v0.6.1 : Change Update function to not crash with RPI
# v0.6 : Rewrite of the module to be easier to maintain
# v0.5.1: Problem with device creation
# v0.5 : Upgrade code to be compliant wih new functions
# v0.4 : Search devices in floors, areas and devices
# v0.3 : Add Next Update information, MAC Address  and Serial Number
#         Add Horizontal vane
#         Add Vertival vane
#         Add Room Temp
# v0.2 : Add sync between Domoticz devices and MELCloud devices
#        Usefull if you use your Mitsubishi remote
# v0.1 : Initial release
"""
<plugin key="MELCloud" version="2.1.1" name="MELCloud plugin" author="gysmo schurgan dalonsic ChatGPT Claude Bastien1307" wikilink="http://www.domoticz.com/wiki/Plugins/MELCloud.html" externallink="http://www.melcloud.com">
    <params>
        <param field="Username" label="Email" width="200px" required="true" />
        <param field="Password" label="Password" width="200px" required="true" password="true"/>
        <param field="Mode1" label="Refresh interval wifi (local)" width="100px">
            <options>
                <option label="Off (cloud only)" value="off"/>
                <option label="10s" value="10"/>
                <option label="20s" value="20"/>
                <option label="30s" value="30" default="true"/>
                <option label="1m" value="60"/>
                <option label="2m" value="120"/>
                <option label="5m" value="300"/>
            </options>
        </param>
        <param field="Mode5" label="Remote temp (mac=idx,mac=idx — optionnel)" width="300px" required="false" />
        <param field="Mode2" label="Refresh interval web (cloud)" width="100px">
            <options>
                <option label="1s" value="1"/>
                <option label="5s" value="5"/>
                <option label="10s" value="10"/>
                <option label="20s - local" value="20"/>
                <option label="1m" value="60"/>
                <option label="2m" value="120" default="true"/>
                <option label="5m - web" value="300"/>
                <option label="10m" value="600"/>
            </options>
        </param>
        <param field="Mode3" label="Language" width="100px">
            <options>
                <option label="English"     value="0" default="true"/>
                <option label="Български"   value="1"/>
                <option label="Čeština"     value="2"/>
                <option label="Dansk"       value="3"/>
                <option label="Deutsch"     value="4"/>
                <option label="Eesti"       value="5"/>
                <option label="Español"     value="6"/>
                <option label="Français"    value="7"/>
                <option label="Հայերեն"     value="8"/>
                <option label="Latviešu"    value="9"/>
                <option label="Lietuvių"    value="10"/>
                <option label="Magyar"      value="11"/>
                <option label="Nederlands"  value="12"/>
                <option label="Norwegian"   value="13"/>
                <option label="Polski"      value="14"/>
                <option label="Português"   value="15"/>
                <option label="Русский"     value="16"/>
                <option label="Suomi"       value="17"/>
                <option label="Svenska"     value="18"/>
                <option label="Italiano"    value="19"/>
                <option label="Українська"  value="20"/>
                <option label="Türkçe"      value="21"/>
                <option label="Ελληνικά"    value="22"/>
                <option label="Hrvatski"    value="23"/>
                <option label="Română"      value="24"/>
                <option label="Slovenščina" value="25"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="None" value="0"  default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Python" value="18"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
        <param field="Mode4" label="ID Domoticz du device testant la connexion Internet (optionnel)" width="200px" required="false" />
    </params>
</plugin>
"""

import math
import os
import sys
import time
import json
from datetime import datetime, timezone
import Domoticz

# Couche locale : le dossier du plugin doit être dans sys.path pour importer
# melcloud_local.py et la lib vendorée pymitsubishi/ (voir VENDORED.txt).
_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
if _PLUGIN_DIR not in sys.path:
    sys.path.insert(0, _PLUGIN_DIR)
try:
    import melcloud_local
except Exception as _e:  # ne doit jamais empêcher le mode cloud de fonctionner
    melcloud_local = None
    _MELCLOUD_LOCAL_IMPORT_ERROR = str(_e)


# ---------------------------------------------------------------------------
# Traduction de l'interface créée au RUNTIME (noms de devices + libellés des
# sélecteurs). Le paramètre Language (Mode3) vaut "7" pour le français ; toute
# autre langue retombe sur l'anglais. Les chaînes ci-dessous sont l'anglais
# « source » ; on n'y touche que si Mode3 == français. NB : ceci ne concerne
# que la CRÉATION des devices — Domoticz ne renomme jamais un device existant,
# et la logique interne (onCommand) n'utilise jamais ces libellés (dispatch par
# numéro d'unité et index de niveau), donc traduire ici est sans risque.
_FR = "7"

# Libellés entiers (noms de devices).
_TR_LABEL = {
    "Mode": "Mode",
    "Fan": "Ventilation",
    "Temp": "Consigne",
    "Vane Horizontal": "Vanne horizontale",
    "Vane Vertical": "Vanne verticale",
    "Room Temp": "Temp. pièce",
    "Unit Infos": "Infos unité",
    "Remote lock": "Verrou télécommande",
    "Consumption": "Consommation",
    "Outdoor group": "Groupe ext.",
}

# Jetons de niveaux (chaînes « a|b|c » des Selector Switch). Un jeton absent de
# la table (ex. les chiffres de vanne) est laissé tel quel.
_TR_LEVEL = {
    "Off": "Arrêt", "Warm": "Chauffage", "Cold": "Refroidissement",
    "Vent": "Ventilation", "Dry": "Séchage", "Auto": "Auto",
    "Level1": "Vitesse1", "Level2": "Vitesse2", "Level3": "Vitesse3",
    "Level4": "Vitesse4", "Level5": "Vitesse5", "Silence": "Silence",
    "Swing": "Oscillation",
    "Unlocked": "Déverrouillé", "Power": "Power", "Mode": "Mode",
    "Temperature": "Température", "All": "Tout",
}


def _is_french():
    try:
        return Parameters.get("Mode3") == _FR
    except Exception:
        return False


def tr(label):
    """Traduit un libellé entier (nom de device) si la langue est le français."""
    return _TR_LABEL.get(label, label) if _is_french() else label


def tr_levels(levels):
    """Traduit une chaîne de niveaux « a|b|c » jeton par jeton, français seul."""
    if not _is_french():
        return levels
    return "|".join(_TR_LEVEL.get(tok, tok) for tok in levels.split("|"))


class BasePlugin:

    melcloud_conn = None
    melcloud_baseurl = "app.melcloud.com"
    melcloud_port = "443"
    melcloud_key = None
    melcloud_state = "Not Ready"

    melcloud_urls = {}
    melcloud_urls["login"] = "/Mitsubishi.Wifi.Client/Login/ClientLogin"
    melcloud_urls["list_unit"] = "/Mitsubishi.Wifi.Client/User/ListDevices"
    melcloud_urls["set_unit"] = "/Mitsubishi.Wifi.Client/Device/SetAta"
    melcloud_urls["unit_info"] = "/Mitsubishi.Wifi.Client/Device/Get"

    list_units = []
    dict_devices = {}

    list_switchs = []
    list_switchs.append({"id": 1, "name": "Mode", "typename": "Selector Switch",
                         "image": 16, "levels": "Off|Warm|Cold|Vent|Dry|Auto"})
    list_switchs.append({"id": 2, "name": "Fan", "typename": "Selector Switch",
                         "image": 7, "levels": "Level1|Level2|Level3|Level4|Level5|Auto|Silence"})
    list_switchs.append({"id": 3, "name": "Temp", "typename": "Thermostat"})
    list_switchs.append({"id": 4, "name": "Vane Horizontal", "typename": "Selector Switch",
                         "image": 7, "levels": "1|2|3|4|5|Swing|Auto"})
    list_switchs.append({"id": 5, "name": "Vane Vertical", "typename": "Selector Switch",
                         "image": 7, "levels": "1|2|3|4|5|Swing|Auto"})
    list_switchs.append({"id": 6, "name": "Room Temp", "typename": "Temperature"})
    list_switchs.append({"id": 7, "name": "Unit Infos", "typename": "Text"})

    domoticz_levels = {}
    domoticz_levels["mode"] = {"0": 0, "10": 1, "20": 3, "30": 7, "40": 2, "50": 8}
    domoticz_levels["mode_pic"] = {"0": 9, "10": 15, "20": 16, "30": 7, "40": 11, "50": 9}
    domoticz_levels["fan"] = {"0": 1, "10": 2, "20": 3, "30": 4, "40": 5, "50": 0, "60": 1}
    domoticz_levels["vaneH"] = {"0": 1, "10": 2, "20": 3, "30": 4, "40": 5, "50": 12, "60": 0}
    domoticz_levels["vaneV"] = {"0": 1, "10": 2, "20": 3, "30": 4, "40": 5, "50": 7, "60": 0}
    # Icônes fan/vanes : AUCUN ID en dur — resolus PAR NOM depuis le pack
    # embarques <Base>.zip (un par icone) par _ensure_icons() a chaque demarrage
    # (Images[base].ID, voir ICON_BASES). Valeur 7 = icone standard Domoticz,
    # repli visible si le pack n'a pas pu etre charge (message dans le log).
    # vaneVConsole_pic = variante CONSOLE AU SOL (modeles MFZ*).
    domoticz_levels["fan_pic"] = {"0": 7, "10": 7, "20": 7, "30": 7, "40": 7, "50": 7}
    domoticz_levels["vaneH_pic"] = {"0": 7, "10": 7, "20": 7, "30": 7, "40": 7, "50": 7, "60": 7}
    domoticz_levels["vaneV_pic"] = {"0": 7, "10": 7, "20": 7, "30": 7, "40": 7, "50": 7, "60": 7}
    domoticz_levels["vaneVConsole_pic"] = {"0": 7, "10": 7, "20": 7, "30": 7, "40": 7, "50": 7, "60": 7}

    runCounter = 0
    runAgain = 6

    def __init__(self):
        return

    # Steap 1
    def _cloud_refresh_seconds(self):
        # Intervalle du poll cloud (Mode2). Robuste au champ vide/invalide :
        # certains Domoticz ne stockent pas la valeur du menu déroulant et le
        # renvoient vide -> int('') planterait. On retombe alors sur 120s, comme
        # le défaut du sélecteur (même logique défensive que Mode1).
        raw = str(Parameters.get('Mode2', '') or '').strip()
        try:
            seconds = int(raw)
        except (TypeError, ValueError):
            seconds = 0
        if seconds <= 0:
            Domoticz.Log("Cloud: intervalle Mode2 '{}' invalide -> 120s par défaut.".format(raw))
            seconds = 120
        return seconds

    def onStart(self):
        self.internetWasDown = False
        # ensure instance-local state
        self.list_units = []

        self.heartbeat_interval = 10  # Sekunden
        Domoticz.Heartbeat(self.heartbeat_interval)

        refresh_seconds = self._cloud_refresh_seconds()
        self.runCounter = max(1, int(refresh_seconds / self.heartbeat_interval))

        self.dict_devices = {}
        self.unit_info_last_ts = {}
        self.unit_info_min_interval = 2.0
        self.http_error_count = 0  # backoff sur erreurs HTTP (500/429...)
        # Rafraichissement periodique de la consommation (ListDevices).
        self.energy_interval_beats = 180   # 180 heartbeats x 10s = 30 min
        self.energy_counter = 6            # 1er rafraichissement ~1 min apres start

        #Damit verhindert man, dass alte Listen/States „hängen bleiben“.
        self.melcloud_key = None
        self.melcloud_state = "Not Ready"

        try:
            Domoticz.Debugging(int(Parameters["Mode6"]))
        except Exception:
            Domoticz.Debugging(0)

        # Icônes : résolution par nom (existantes dans Domoticz ou pack embarqué).
        self._ensure_icons()

        # ---------------- Couche LOCALE (WiFi direct, cloud en secours) --------
        self._init_local_layer()
        # Cache persisté (unités + IP) : permet un démarrage 100% local même
        # sans internet/cloud (l'utilisateur peut avoir coupé sa box).
        self._load_config_cache()

        # ---------------- Cloud MELCloud (chemin historique) -------------------
        # Le check internet (Mode4) ne bloque QUE le cloud : le local n'en a
        # pas besoin. S'il n'y a pas d'internet, le heartbeat tentera plus tard.
        self.melcloud_conn = None
        if self._internet_ok():
            self._start_connection()
        return True

    # --- Icônes embarquées ------------------------------------------------------
    # Résolution PAR NOM, jamais par ID : si les icônes existent déjà dans
    # Domoticz (upload manuel historique OU pack déjà chargé), on prend leurs
    # IDs tels quels ; sinon on charge les zips livrés <Base>.zip (un par icône).
    # Mapping niveau->nom de base d'icône.
    ICON_BASES = {
        "fan_pic": {"0": "ClimSilence", "10": "ClimFan1", "20": "ClimFan2",
                    "30": "ClimFan3", "40": "ClimFan4", "50": "ClimAuto"},
        "vaneH_pic": {"0": "ClimGaucheDroite1", "10": "ClimGaucheDroite2",
                      "20": "ClimGaucheDroite3", "30": "ClimGaucheDroite4",
                      "40": "ClimGaucheDroite5", "50": "ClimGaucheDroiteOcillation",
                      "60": "ClimGaucheDroiteAuto"},
        "vaneV_pic": {"0": "ClimHautBas1", "10": "ClimHautBas2", "20": "ClimHautBas3",
                      "30": "ClimHautBas4", "40": "ClimHautBas5",
                      "50": "ClimHautBasOcillation", "60": "ClimHautBasAuto"},
        "vaneVConsole_pic": {"0": "ClimVerticale1", "10": "ClimVerticale2",
                             "20": "ClimVerticale3", "30": "ClimVerticale4",
                             "40": "ClimVerticale4", "50": "ClimVerticaleOcillation",
                             "60": "ClimVerticaleAuto"},
    }

    def _ensure_icons(self):
        # Domoticz ne gère qu'UNE icône par zip de plugin (constaté : avec un
        # zip multi-icônes, seule la dernière ligne d'icons.txt est prise).
        # D'où 26 zips individuels <Base>.zip. Si la Base existe déjà en BDD
        # (icônes uploadées à la main), Domoticz la RELIE au plugin sans rien
        # créer -> pas de doublon, IDs existants conservés.
        try:
            needed = sorted({b for m in self.ICON_BASES.values() for b in m.values()})
            missing_zips = []
            for base in needed:
                if base in Images:
                    continue
                # Zips dans icons/ uniquement (validé en réel le 2026-07-11).
                zip_name = "icons/" + base + ".zip"
                if os.path.isfile(os.path.join(_PLUGIN_DIR, zip_name)):
                    Domoticz.Image(Filename=zip_name).Create()
                else:
                    missing_zips.append(zip_name)
            replaced = 0
            for map_name, bases in self.ICON_BASES.items():
                for level, base in bases.items():
                    if base in Images:
                        self.domoticz_levels[map_name][level] = Images[base].ID
                        replaced += 1
            total = sum(len(m) for m in self.ICON_BASES.values())
            Domoticz.Log("Icônes: {}/{} entrée(s) résolue(s) par nom ; zips manquants: {}".format(
                replaced, total, missing_zips or "aucun"))
            if replaced < total:
                Domoticz.Error("Icônes: résolution incomplète (Images: {}) — les niveaux "
                               "non résolus utilisent l'icône standard (7).".format(
                                   sorted(str(k) for k in Images)))
        except Exception as e:
            Domoticz.Error("Icônes: résolution impossible ({}) — icônes standard (7).".format(e))

    # --- Couche locale : initialisation & helpers ------------------------------
    LOCAL_REFRESH_ALLOWED = (10, 20, 30, 60, 120, 300)

    def _init_local_layer(self):
        self.local = None
        self.local_refresh_seconds = 0
        self.localRunCounter = 1          # 1er poll local au 1er heartbeat
        self.thermo_map = {}              # mac -> idx thermomètre Domoticz
        self._local_ips_saved = {}        # dernier cache d'IP persisté

        raw = str(Parameters.get('Mode1', '') or '').strip().lower()
        if raw == 'off':
            Domoticz.Log("Local: désactivé (Mode1=off), fonctionnement cloud uniquement.")
            return
        try:
            seconds = int(raw)
        except (TypeError, ValueError):
            seconds = -1
        if seconds not in self.LOCAL_REFRESH_ALLOWED:
            # Valeur héritée d'une ancienne config (ex-champ GMT Offset) ou vide :
            # on retombe sur 30s plutôt que de désactiver silencieusement.
            Domoticz.Log("Local: intervalle Mode1 '{}' invalide -> 30s par défaut.".format(raw))
            seconds = 30

        if melcloud_local is None:
            Domoticz.Error("Local: module melcloud_local introuvable ({}) — cloud uniquement.".format(
                globals().get('_MELCLOUD_LOCAL_IMPORT_ERROR', '?')))
            return
        if not melcloud_local.LOCAL_AVAILABLE:
            Domoticz.Error("Local: lib pymitsubishi inutilisable ({}) — installer "
                           "pycryptodome dans le python de Domoticz. Cloud uniquement.".format(
                               melcloud_local.LOCAL_IMPORT_ERROR))
            return

        self.local_refresh_seconds = seconds
        self.local = melcloud_local.LocalLayer(
            log=Domoticz.Log, debug=Domoticz.Debug, error=Domoticz.Error)
        # En Docker bridge, l'interface du conteneur (172.x) ne dit rien du vrai
        # LAN : on déduit le(s) sous-réseau(x) des IPs des autres matériels
        # Domoticz (pont Hue, etc.) via l'API locale.
        self.local.set_subnet_hints(self._lan_hints_from_domoticz())
        Domoticz.Log("Local: activé (poll {}s, cloud en secours toutes les {}s).".format(
            seconds, self._cloud_refresh_seconds()))

        # Mode5 : mapping "mac=idx,mac=idx" pour la température distante.
        raw_map = str(Parameters.get('Mode5', '') or '').strip()
        if raw_map:
            for part in raw_map.replace(';', ',').split(','):
                if '=' not in part:
                    continue
                mac, _, idx = part.partition('=')
                try:
                    self.thermo_map[melcloud_local.norm_mac(mac)] = int(idx.strip())
                except ValueError:
                    Domoticz.Error("Local: entrée Mode5 invalide ignorée: '{}'".format(part))
            if self.thermo_map:
                Domoticz.Log("Local: température distante configurée: {}".format(self.thermo_map))

    def _lan_hints_from_domoticz(self):
        # IPs privées des autres matériels Domoticz (gethardware) -> le vrai LAN,
        # même depuis un conteneur bridge. Même mécanisme API que Mode4.
        import re
        import requests
        ips = []
        try:
            r = requests.get('http://127.0.0.1:8080/json.htm?type=command&param=gethardware',
                             timeout=2)
            for hw in r.json().get('result', []):
                addr = str(hw.get('Address', '') or '')
                m = re.match(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', addr.strip())
                if m:
                    ips.append(m.group(1))
        except Exception as e:
            Domoticz.Debug("LAN hints: gethardware illisible ({})".format(e))
        return ips

    def _internet_ok(self):
        # Device Domoticz optionnel (Mode4) témoin de la connexion internet.
        # Ne gate QUE le chemin cloud.
        if not Parameters.get('Mode4'):
            return True
        status = self.getDomoticzDeviceStatus(int(Parameters['Mode4']))
        if status == 'Off':
            if not self.internetWasDown:
                Domoticz.Error('Connexion Internet absente (device ID {} = Off), cloud suspendu (le local continue).'.format(Parameters['Mode4']))
                self.internetWasDown = True
            return False
        if self.internetWasDown:
            Domoticz.Error('Connexion Internet rétablie.')
            self.internetWasDown = False
        return True

    def _load_config_cache(self):
        # Recharge unités + IP depuis Domoticz.Configuration : démarrage possible
        # sans cloud. Le cloud (UNITS_INIT) rafraîchira/écrasera à son retour.
        try:
            cfg = Domoticz.Configuration()
        except Exception:
            cfg = {}
        units = []
        try:
            units = json.loads(cfg.get('units_cache', '[]'))
        except Exception:
            units = []
        if units and not self.list_units:
            self.list_units = units
            for u in self.list_units:
                u['next_comm'] = False
            Domoticz.Log("Cache: {} unité(s) rechargée(s) sans cloud: {}".format(
                len(units), ", ".join(u.get('name', '?') for u in units)))
        if self.local:
            self.local.set_units([{"mac": u.get('macaddr'), "name": u.get('name')}
                                  for u in self.list_units if u.get('macaddr')])
            try:
                ips = json.loads(cfg.get('local_ips', '{}'))
            except Exception:
                ips = {}
            self._local_ips_saved = dict(ips)
            self.local.set_cached_ips(ips)

    def _persist_config_cache(self):
        # Persiste unités + IP découvertes (Domoticz.Configuration, stocké en BDD).
        try:
            keep = ('name', 'id', 'macaddr', 'sn', 'building_id', 'outdoor_sn', 'idoffset', 'model')
            units = [{k: u.get(k) for k in keep} for u in self.list_units]
            payload = {'units_cache': json.dumps(units)}
            if self.local:
                payload['local_ips'] = json.dumps(self.local.get_ips())
            cfg = Domoticz.Configuration()
            cfg.update(payload)
            Domoticz.Configuration(cfg)
        except Exception as e:
            Domoticz.Debug("Cache: persistance impossible ({})".format(e))

    def onStop(self):
        # Sécurité : ne jamais laisser des télécommandes physiquement bloquées
        # pendant que Domoticz est éteint (le sélecteur garde l'intention, le
        # verrou sera ré-appliqué au prochain démarrage).
        try:
            self._release_locks_on_stop()
        except Exception as e:
            Domoticz.Error("Levée des verrous à l'arrêt impossible: {}".format(e))
        Domoticz.Log("Goodbye from MELCloud plugin.")

    # Steap 3
    def onConnect(self, Connection, Status, Description):
        if Status == 0:
            # Idempotence : lors d'une course de reconnexion, plusieurs objets
            # Connection peuvent se connecter ("connection OK" en double). Une
            # seule doit piloter le login, sinon deux flux de requetes partagent
            # le meme melcloud_state -> desync ("Find 21 buildings"), TypeError
            # ligne 332 et SIGABRT du thread plugin. On n'accepte un onConnect
            # que si on n'est pas deja connecte/en cours de login.
            if self.melcloud_state not in ("Not Ready", "LOGIN_FAILED"):
                Domoticz.Log("MELCloud: connexion supplementaire ignoree (etat {})".format(self.melcloud_state))
                return
            Domoticz.Log("MELCloud connection OK")
            self.melcloud_state = "READY"
            self.melcloud_login()
        else:
            Domoticz.Log("MELCloud connection FAIL: "+Description)

    @staticmethod
    def _utc_to_local(ts_utc):
        # Convertit un timestamp MelCloud (UTC, ex '2026-07-05T22:20:54.005')
        # en heure locale du systeme. astimezone() sans argument applique le
        # fuseau local, DST (ete/hiver) inclus. En cas de format inattendu on
        # renvoie la chaine telle quelle plutot que de lever une exception.
        try:
            s = ts_utc.split(".")[0]  # on ignore les millisecondes
            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(ts_utc)

    # Steap 13
    # Steap 14
    # Steap 16
    # Steap 17
    def extractDeviceData(self, device):
        dev = device.get("Device", {})
        name = device.get("DeviceName", "?")
        did = device.get("DeviceID", "?")

        has_meter = dev.get("HasEnergyConsumedMeter", False)
        raw = dev.get("CurrentEnergyConsumed", None)

        Domoticz.Debug("EnergyCheck: {} (DeviceID {}) HasEnergyConsumedMeter={} RawCurrentEnergyConsumed={}".format(
            name, did, has_meter, raw
        ))

        if not has_meter or raw is None:
            return 0.0

        try:
            return float(raw) / 1000.0
        except Exception:
            return 0.0

    # Steap 10
    # Steap 11
    def searchUnits(self, building, scope, idoffset):
        nr_of_Units = 0
        cEnergyConsumed = 0
        # Search in scope

        def oneUnit(self, device, idoffset, nr_of_Units, cEnergyConsumed, building, scope):
            self.melcloud_add_unit(device, idoffset)
            dev = device.get("Device", {})
            Domoticz.Debug("DeviceLinkCheck {} (DeviceID {}): keys={}".format(
                device.get("DeviceName","?"),
                device.get("DeviceID","?"),
                sorted(list(dev.keys()))
            ))
            idoffset += len(self.list_switchs)
            nr_of_Units += 1
            currentEnergyConsumed = self.extractDeviceData(device)
            cEnergyConsumed += currentEnergyConsumed
            Domoticz.Log("Found {} in building {} {} | EnergyConsumed: {:.3f} kWh".format(
                device.get("DeviceName", "?"),
                building.get("Name", "?"),
                scope,
                currentEnergyConsumed
            ))
            return (nr_of_Units, idoffset, cEnergyConsumed)

        for item in building["Structure"][scope]:
            if scope == u'Devices':
                if item["Type"] == 0:
                    (nr_of_Units, idoffset, cEnergyConsumed) = oneUnit(self, item, idoffset,
                                                                       nr_of_Units, cEnergyConsumed,
                                                                       building, scope)
            elif scope in (u'Areas', u'Floors'):
                for device in item["Devices"]:
                    (nr_of_Units, idoffset, cEnergyConsumed) = oneUnit(self, device, idoffset,
                                                                       nr_of_Units, cEnergyConsumed,
                                                                       building, scope)
                if scope == u'Floors':
                    for device in item["Areas"]:
                        (nr_of_Units, idoffset, cEnergyConsumed) = oneUnit(self, device, idoffset,
                                                                   nr_of_Units, cEnergyConsumed,
                                                                   building, scope)

        text2log = u'Found {} devices in building {} {} of the Type 0 (Aircondition) CurrentEnergyConsumed {:.0f} kWh'
        text2log = text2log.format(str(nr_of_Units), building["Name"], scope, cEnergyConsumed)
        Domoticz.Log(text2log)

        return (nr_of_Units, idoffset, cEnergyConsumed)

    # Steap 6
    # Steap 9
    def onMessage(self, Connection, Data):
        Status = int(Data["Status"])
        if Status == 200:
            self.http_error_count = 0  # reponse OK -> on remet le backoff a zero
            strData = Data["Data"].decode("utf-8", "ignore")
            response = json.loads(strData)
            Domoticz.Debug("JSON REPLY: "+str(response))
            if self.melcloud_state == "LOGIN":
                if ("ErrorId" not in response.keys()) or (response["ErrorId"] is None):
                    Domoticz.Log("MELCloud login successful")
                    self.melcloud_key = response["LoginData"]["ContextKey"]
                    self.melcloud_units_init()
                elif response["ErrorId"] == 1:
                    Domoticz.Log("MELCloud login fail: check login and password")
                    self.melcloud_state = "LOGIN_FAILED"
                else:
                    Domoticz.Log("MELCloud failed with unknown error "+str(response["ErrorId"]))
                    self.melcloud_state = "LOGIN_FAILED"

            elif self.melcloud_state == "UNITS_INIT":
                # Garde anti-crash : en cas de course entre connexions, une
                # reponse de login (dict) peut arriver alors que l'etat est
                # UNITS_INIT. Sans ce garde, "for building in response" itere
                # les cles du dict et building["Structure"] leve TypeError
                # -> exception non geree ayant provoque des SIGABRT.
                if not isinstance(response, list):
                    Domoticz.Error("UNITS_INIT: reponse inattendue (type {}), ignoree.".format(type(response).__name__))
                    return
                # Repartir d'une liste propre : evite les doublons d'unites
                # (Clim traitee 2x) si un re-login survient.
                self.list_units = []
                idoffset = 0
                Domoticz.Log("Find " + str(len(response)) + " buildings")
                for building in response:
                    Domoticz.Log("Find " + str(len(building["Structure"]["Areas"])) +
                                 " areas in building "+building["Name"])
                    Domoticz.Log("Find " + str(len(building["Structure"]["Floors"])) +
                                 " floors in building "+building["Name"])
                    # Search in devices
                    (nr_of_Units, idoffset, cEnergyConsumed) = self.searchUnits(building, "Devices", idoffset)
                    # Search in areas
                    (nr_of_Units, idoffset, cEnergyConsumed) = self.searchUnits(building, "Areas", idoffset)
                    # Search in floors
                    (nr_of_Units, idoffset, cEnergyConsumed) = self.searchUnits(building, "Floors", idoffset)
                self.melcloud_create_units()
            elif self.melcloud_state == "UNIT_INFO":
                # Garde anti-crash : ne traiter que le petit dict attendu.
                if not isinstance(response, dict) or 'DeviceID' not in response:
                    Domoticz.Error("UNIT_INFO: reponse inattendue, ignoree.")
                    return
                for unit in self.list_units:
                    if unit['id'] == response['DeviceID']:
                        # Priorité LOCAL : si l'unité est servie en local, une
                        # réponse cloud (tardive ou périmée) ne doit pas écraser
                        # les données temps réel.
                        if self._unit_local_healthy(unit):
                            Domoticz.Debug("UNIT_INFO cloud ignoré pour {} (local sain)".format(unit['name']))
                            break
                        # Temp ambiante = capteur fiable (non surveille par
                        # dzVents) -> toujours rafraichie, meme si le reste est
                        # rejete, pour ne pas figer l'affichage.
                        unit['room_temp'] = response['RoomTemperature']
                        # VALIDATION DE TRAME (remplace la garde Offline, qui
                        # etait un mauvais signal - vraie ~90% du temps meme quand
                        # tout va bien). Une clim reelle a TOUJOURS un mode valide
                        # (1 Chauf,2 Sec,3 Froid,7 Ventil,8 Auto) ET une consigne
                        # > 0. Les trames "zero-ees" (OperationMode=0 et/ou
                        # SetTemperature<=0) sont des snapshots degrades renvoyes
                        # hors-ligne : ce sont eux qui amorcaient le flapping.
                        # On les rejette (physiquement impossibles).
                        op_mode = response['OperationMode']
                        set_temp = response['SetTemperature']
                        if op_mode not in (1, 2, 3, 7, 8) or set_temp is None or set_temp <= 0:
                            Domoticz.Debug("Trame rejetee {0}: OperationMode={1} SetTemperature={2}".format(
                                unit['name'], op_mode, set_temp))
                            self._update_room_temp(unit)
                            break
                        # Trame valide -> on l'accepte entierement.
                        Domoticz.Log("Update unit {0} information.".format(unit['name']))
                        unit['power'] = response['Power']
                        unit['op_mode'] = op_mode
                        unit['set_temp'] = set_temp
                        unit['set_fan'] = response['SetFanSpeed']
                        unit['vaneH'] = response['VaneHorizontal']
                        unit['vaneV'] = response['VaneVertical']
                        unit['next_comm'] = False
                        Domoticz.Debug("Heartbeat unit info: "+str(unit))
                        self.domoticz_sync_switchs(unit)
                        break
            elif self.melcloud_state == "SET":
                if not isinstance(response, dict) or 'DeviceID' not in response:
                    Domoticz.Error("SET: reponse inattendue, ignoree.")
                    return
                for unit in self.list_units:
                    if unit['id'] == response['DeviceID']:
                        # NextCommunication est en UTC. On convertit vers l'heure
                        # locale du systeme, ce qui gere l'heure ete/hiver (DST)
                        # automatiquement : plus besoin du parametre GMT Offset.
                        next_comm = self._utc_to_local(response['NextCommunication'])
                        unit['next_comm'] = "Update for last command at " + next_comm
                        Domoticz.Log("Next update for command: " + next_comm)
                        self.domoticz_sync_switchs(unit)
            elif self.melcloud_state == "ENERGY_REFRESH":
                # Rafraichissement periodique de la consommation (l'energie n'est
                # que dans ListDevices). On met a jour energy_wh par clim SANS
                # reconstruire list_units, puis on synchronise les compteurs kWh.
                if not isinstance(response, list):
                    Domoticz.Error("ENERGY_REFRESH: reponse inattendue, ignoree.")
                    return
                for dev in self._iter_ata_devices(response):
                    did = dev.get("DeviceID")
                    for unit in self.list_units:
                        if unit['id'] == did:
                            d = dev.get("Device", {})
                            if d.get("HasEnergyConsumedMeter"):
                                try:
                                    unit['energy_wh'] = float(d.get("CurrentEnergyConsumed") or 0)
                                except Exception:
                                    pass
                            break
                self._sync_energy_devices()
            else:
                Domoticz.Log("State not implemented:" + self.melcloud_state)
        else:
            try:
                body = Data.get("Data", b"")
                if isinstance(body, (bytes, bytearray)):
                    body = body.decode("utf-8", "ignore")
                Domoticz.Error("MELCloud HTTP error {} in state {}. Response body: {}".format(
                    Data.get("Status"), self.melcloud_state, str(body)[:200]
                ))
            except Exception as e:
                Domoticz.Error("MELCloud receive error code {} (failed to decode body: {})".format(Data.get("Status"), e))
            # Backoff : sur erreurs HTTP repetees (500/429...), on espace les
            # requetes pour ne pas marteler l'API MelCloud. On repousse le
            # prochain poll de +60s par erreur consecutive, plafonne a 10 min.
            self.http_error_count = getattr(self, 'http_error_count', 0) + 1
            backoff_beats = min(self.http_error_count * 6, 60)  # 6 heartbeats = 60s ; cap 600s
            self.runCounter = max(self.runCounter, backoff_beats)
            Domoticz.Debug("MELCloud backoff: {} erreur(s) consecutive(s) -> prochain poll dans {} heartbeats".format(
                self.http_error_count, backoff_beats))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) +
                     ": Parameter '" + str(Command) + "', Level: " + str(Level))
        # Sélecteurs "verrou télécommande" (Unit >= 200) : fonction locale
        # uniquement (le cloud MELCloud ne l'expose pas).
        if Unit >= self.LOCK_UNIT_BASE:
            return self._command_remote_lock(Unit, Level)
        # Les compteurs kWh (Unit >= 100) ne sont pas des interrupteurs : la
        # logique switch ci-dessous planterait (unite introuvable). On ignore.
        if Unit >= self.ENERGY_UNIT_INDOOR_BASE:
            return True
        # ~ Get switch function: mode, fan, temp ...
        switch_id = Unit
        while switch_id > 7:
            switch_id -= 7
        switch_type = self.list_switchs[switch_id-1]["name"]
        # ~ Get the unit in units array
        current_unit = False
        for unit in self.list_units:
            if (unit['idoffset'] + self.list_switchs[switch_id-1]["id"]) == Unit:
                current_unit = unit
                break
        if switch_type == 'Mode':
            if Level == 0:
                flag = 1
                current_unit['power'] = False
                #current_unit['power'] = 'false'
                Domoticz.Log("Switch Off the unit "+current_unit['name'] +
                             "with ID offset " + str(current_unit['idoffset']))
                Devices[1+current_unit['idoffset']].Update(nValue=0, sValue=str(Level), Image=9)
                Devices[2+current_unit['idoffset']].Update(nValue=0,
                                                           sValue=str(Devices[Unit + 1].sValue))
                Devices[3+current_unit['idoffset']].Update(nValue=0,
                                                           sValue=str(Devices[Unit + 2].sValue))
                Devices[4+current_unit['idoffset']].Update(nValue=0,
                                                           sValue=str(Devices[Unit + 3].sValue))
                Devices[5+current_unit['idoffset']].Update(nValue=0,
                                                           sValue=str(Devices[Unit + 4].sValue))
                Devices[6+current_unit['idoffset']].Update(nValue=0,
                                                           sValue=str(Devices[Unit + 5].sValue))
            elif Level == 10:
                Domoticz.Log("Set to WARM the unit "+current_unit['name'])
                Devices[1+current_unit['idoffset']].Update(nValue=1, sValue=str(Level), Image=15)
            elif Level == 20:
                Domoticz.Log("Set to COLD the unit "+current_unit['name'])
                Devices[1+current_unit['idoffset']].Update(nValue=1, sValue=str(Level), Image=16)
            elif Level == 30:
                Domoticz.Log("Set to Vent the unit "+current_unit['name'])
                Devices[1+current_unit['idoffset']].Update(nValue=1, sValue=str(Level), Image=7)
            elif Level == 40:
                Domoticz.Log("Set to Dry the unit "+current_unit['name'])
                Devices[1+current_unit['idoffset']].Update(nValue=1, sValue=str(Level), Image=11)
            elif Level == 50:
                Domoticz.Log("Set to Auto the unit "+current_unit['name'])
                Devices[1+current_unit['idoffset']].Update(nValue=1, sValue=str(Level), Image=9)
            if Level != 0:
                current_unit['power'] = True
                current_unit['op_mode'] = self.domoticz_levels['mode'][str(Level)]
                flag = 3  # Power (1) + OperationMode (2)
                Devices[2+current_unit['idoffset']].Update(nValue=1,
                                                           sValue=str(Devices[Unit + 1].sValue))
                Devices[3+current_unit['idoffset']].Update(nValue=1,
                                                           sValue=str(Devices[Unit + 2].sValue))
                Devices[4+current_unit['idoffset']].Update(nValue=1,
                                                           sValue=str(Devices[Unit + 3].sValue))
                Devices[5+current_unit['idoffset']].Update(nValue=1,
                                                           sValue=str(Devices[Unit + 4].sValue))
                Devices[6+current_unit['idoffset']].Update(nValue=1,
                                                           sValue=str(Devices[Unit + 5].sValue))
        elif switch_type == 'Fan':
            flag = 8
            current_unit['set_fan'] = self.domoticz_levels['fan'][str(Level)]
            image = self.domoticz_levels['fan_pic'].get(str(Level), 7)
            Domoticz.Log("Change FAN  to value {0} for {1} ".format(self.domoticz_levels['fan'][str(Level)], current_unit['name']))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Level), Image=image)
        elif switch_type == 'Temp':
            flag = 4
            Domoticz.Log("Change Temp to " + str(Level) + " for "+unit['name'])
            current_unit['set_temp'] = str(Level)
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Level))
        elif switch_type == 'Vane Horizontal':
            flag = 256
            current_unit['vaneH'] = self.domoticz_levels['vaneH'][str(Level)]
            image = self.domoticz_levels['vaneH_pic'].get(str(Level), 7)
            Domoticz.Debug("Change Vane Horizontal to value {0} for {1}".format(self.domoticz_levels['vaneH'][str(Level)], current_unit['name']))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Level), Image=image)
        elif switch_type == 'Vane Vertical':
            flag = 16
            current_unit['vaneV'] = self.domoticz_levels['vaneV'][str(Level)]
            pic_map = 'vaneVConsole_pic' if self._is_console(current_unit) else 'vaneV_pic'
            image = self.domoticz_levels[pic_map].get(str(Level), 7)
            Domoticz.Debug("Change Vane Vertical to value {0} for {1}".format(self.domoticz_levels['vaneV'][str(Level)], current_unit['name']))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=str(Level), Image=image)
        else:
            Domoticz.Log("Device not found")
        # ---- Envoi : LOCAL d'abord (immédiat), cloud MELCloud en secours ------
        if not self._send_command_local(current_unit, flag):
            self.melcloud_set_json(current_unit, flag)
        #self.melcloud_set(current_unit, flag)
        return True

    def _send_command_local(self, unit, flag):
        # Traduit le couple (unit, EffectiveFlags MELCloud) en commande locale.
        # Renvoie True si la commande est partie en local (pas de SET cloud),
        # False pour laisser le chemin cloud prendre le relais.
        if not unit or not self._unit_local_healthy(unit):
            return False
        kwargs = {}
        if flag & 1:
            kwargs['power'] = bool(unit.get('power', False))
        if (flag & 2) and unit.get('op_mode') not in ("", None):
            kwargs['op_mode'] = int(unit['op_mode'])
        if (flag & 4) and unit.get('set_temp') not in ("", None):
            kwargs['set_temp'] = float(unit['set_temp'])
        if (flag & 8) and unit.get('set_fan') not in ("", None):
            kwargs['set_fan'] = int(unit['set_fan'])
        if (flag & 16) and unit.get('vaneV') not in ("", None):
            kwargs['vaneV'] = int(unit['vaneV'])
        if (flag & 256) and unit.get('vaneH') not in ("", None):
            kwargs['vaneH'] = int(unit['vaneH'])
        if not kwargs:
            return False
        try:
            ok = self.local.command(unit['macaddr'], **kwargs)
        except Exception as e:
            Domoticz.Error("Local: commande {} en échec ({}) -> bascule cloud".format(
                unit.get('name'), e))
            return False
        if ok:
            Domoticz.Log("Commande LOCALE envoyée à {} {} (confirmation au prochain poll)".format(
                unit.get('name'), kwargs))
            # Trace dans le device texte "Unit Infos" (équivalent du NextCommunication cloud).
            u_txt = self.list_switchs[6]["id"] + unit["idoffset"]
            if u_txt in Devices:
                Devices[u_txt].Update(nValue=1, sValue="Commande locale à " +
                                      datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return True
        Domoticz.Log("Local indisponible pour {} -> commande via cloud".format(unit.get('name')))
        return False

    # --- Verrou télécommande (local uniquement) --------------------------------
    LOCK_UNIT_BASE = 200
    LOCK_LEVEL_TO_FLAGS = {0: 0, 10: 1, 20: 2, 30: 4, 40: 7}  # Unlocked|Power|Mode|Temp|Tout

    def _ensure_lock_devices(self):
        # Sélecteurs de verrou télécommande, créés uniquement si la couche
        # locale est active (fonction inaccessible via le cloud).
        if self.local is None:
            return
        block = len(self.list_switchs)
        for unit in self.list_units:
            idx = unit['idoffset'] // block
            u_lock = self.LOCK_UNIT_BASE + idx
            if u_lock not in Devices:
                Domoticz.Log("Creating lock device: {} - Verrou télécommande (Unit {})".format(
                    unit['name'], u_lock))
                options = {"LevelNames": tr_levels("Unlocked|Power|Mode|Temperature|All"),
                           "LevelOffHidden": "false", "SelectorStyle": "0"}
                Domoticz.Device(Name=unit['name'] + " - " + tr("Remote lock"), Unit=u_lock,
                                TypeName="Selector Switch", Image=9, Options=options,
                                Used=0).Create()

    def _lock_flags_for_unit(self, unit):
        # Flags de verrou voulus d'après le SÉLECTEUR Domoticz de l'unité
        # (source de vérité de l'intention utilisateur). 0 si device absent.
        block = len(self.list_switchs)
        u_lock = self.LOCK_UNIT_BASE + (unit['idoffset'] // block)
        if u_lock not in Devices:
            return 0
        try:
            level = int(float(Devices[u_lock].sValue or 0))
        except (TypeError, ValueError):
            return 0
        return self.LOCK_LEVEL_TO_FLAGS.get(level, 0)

    def _restore_lock_if_wanted(self, unit):
        # Au (re)démarrage : si le sélecteur dit « verrouillé », on ré-applique
        # physiquement le verrou dès que la clim répond en local. Une fois par
        # session ; le device Domoticz n'est pas modifié.
        if unit.get('_lock_restored'):
            return
        unit['_lock_restored'] = True
        flags = self._lock_flags_for_unit(unit)
        if flags:
            try:
                if self.local.set_remote_lock(unit['macaddr'], flags):
                    Domoticz.Log("Verrou télécommande {} ré-appliqué au démarrage (flags {}).".format(
                        unit['name'], flags))
                else:
                    unit['_lock_restored'] = False  # clim pas prête -> réessai au prochain poll
            except Exception as e:
                Domoticz.Error("Verrou télécommande {} : ré-application impossible ({})".format(
                    unit.get('name'), e))

    def _release_locks_on_stop(self):
        # À l'ARRÊT du plugin : déverrouiller physiquement les télécommandes
        # (sans toucher aux devices Domoticz) pour ne pas laisser l'utilisateur
        # bloqué si Domoticz reste éteint. Le démarrage suivant re-verrouille
        # selon l'état des sélecteurs (_restore_lock_if_wanted).
        if self.local is None:
            return
        for unit in self.list_units:
            if not unit.get('macaddr'):
                continue
            if self._lock_flags_for_unit(unit):
                try:
                    if self.local.set_remote_lock(unit['macaddr'], 0):
                        Domoticz.Log("Verrou télécommande {} levé (arrêt du plugin) — "
                                     "sera ré-appliqué au prochain démarrage.".format(unit['name']))
                except Exception as e:
                    Domoticz.Error("Verrou télécommande {} : levée impossible à l'arrêt ({})".format(
                        unit.get('name'), e))

    def _command_remote_lock(self, Unit, Level):
        flags = self.LOCK_LEVEL_TO_FLAGS.get(int(Level))
        if flags is None or self.local is None:
            return True
        block = len(self.list_switchs)
        for unit in self.list_units:
            if self.LOCK_UNIT_BASE + (unit['idoffset'] // block) == Unit:
                ok = False
                try:
                    ok = self.local.set_remote_lock(unit['macaddr'], flags)
                except Exception as e:
                    Domoticz.Error("Local: verrou télécommande {} en échec: {}".format(
                        unit.get('name'), e))
                if ok:
                    Domoticz.Log("Verrou télécommande {} -> flags {}".format(unit['name'], flags))
                    Devices[Unit].Update(nValue=(1 if flags else 0), sValue=str(Level))
                else:
                    Domoticz.Error("Verrou télécommande {} : clim injoignable en local.".format(
                        unit.get('name')))
                break
        return True

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," +
                     Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("MELCloud has disconnected")
        self.melcloud_state = "Not Ready"
        self.melcloud_key = None
        self.melcloud_conn = None   # WICHTIG: Connection-Objekt verwerfen
        self.runAgain = 1           # schneller reconnect

    # Steap 2
    # Steap 21
    def getDomoticzDeviceStatus(self, idx):
        import requests
        try:
            url = 'http://127.0.0.1:8080/json.htm?type=command&param=getdevices&rid={}'.format(idx)
            r = requests.get(url, timeout=2)
            data = r.json()
            if 'result' in data and len(data['result']) > 0:
                return data['result'][0]['Status']  # Devrait être 'On' ou 'Off'
        except Exception as e:
            Domoticz.Error('Erreur en lisant le statut Internet via device {}: {}'.format(idx, str(e)))
        return 'Off'

    def getDomoticzDeviceTemp(self, idx):
        # Température d'un device Domoticz (thermomètre) via l'API JSON locale —
        # même mécanisme éprouvé que getDomoticzDeviceStatus. None si illisible.
        import requests
        try:
            url = 'http://127.0.0.1:8080/json.htm?type=command&param=getdevices&rid={}'.format(idx)
            r = requests.get(url, timeout=2)
            data = r.json()
            if 'result' in data and len(data['result']) > 0:
                temp = data['result'][0].get('Temp')
                if temp is not None:
                    return float(temp)
        except Exception as e:
            Domoticz.Debug('Thermomètre idx {} illisible: {}'.format(idx, str(e)))
        return None

    # --- Couche locale : heartbeat -------------------------------------------
    def _unit_local_healthy(self, unit):
        return (self.local is not None and unit.get('macaddr')
                and self.local.is_healthy(unit['macaddr']))

    @staticmethod
    def _is_console(unit):
        # Console au sol Mitsubishi = famille de modèles MFZ* (ex. MFZ-KT25VG).
        # Le modèle vient de MELCloud (Units[].Model, persisté dans le cache).
        # Repli héritage : l'install historique nommait la console "Clim Chambre".
        model = str(unit.get('model') or '').strip().upper()
        if model:
            return model.startswith('MFZ')
        return unit.get('name') == "Clim Chambre"

    @staticmethod
    def _round_remote_temp(temp, op_mode):
        # La clim encode la température par pas de 0,5° (les dixièmes sont
        # perdus). Arrondi conservateur selon le mode : en FROID/SEC on prend
        # le pas SUPÉRIEUR (surestimer la chaleur -> elle ne s'arrête pas trop
        # tôt), en CHAUD le pas INFÉRIEUR. Auto/Ventil : au plus proche.
        # Un multiple de 0,5 exact reste inchangé (28,0 -> 28,0).
        half_steps = round(float(temp) * 2, 6)  # tue la poussière flottante
        if op_mode in (2, 3):        # 2 = Sec, 3 = Froid
            return math.ceil(half_steps) / 2.0
        if op_mode == 1:             # 1 = Chauffage
            return math.floor(half_steps) / 2.0
        return round(half_steps) / 2.0

    def _local_heartbeat(self):
        if self.local is None or not self.list_units:
            return
        # Découverte progressive tant qu'il manque des IP (1 étape par beat,
        # bornée en durée pour ne pas bloquer le thread du plugin).
        try:
            self.local.discovery_step()
        except Exception as e:
            Domoticz.Error("Local: discovery_step a échoué: {}".format(e))

        self.localRunCounter -= 1
        if self.localRunCounter > 0:
            return
        self.localRunCounter = max(1, int(self.local_refresh_seconds / self.heartbeat_interval))

        for unit in self.list_units:
            mac = unit.get('macaddr')
            if not mac:
                continue
            state = None
            try:
                state = self.local.poll(mac)
            except Exception as e:
                Domoticz.Error("Local: poll {} a échoué: {}".format(unit.get('name'), e))
            if not state:
                continue  # local down -> le chemin cloud prendra le relais
            self._local_sync_unit(unit, state)
            # Re-verrouillage télécommande si le sélecteur le demande (une fois
            # par session, dès que la clim répond — cf. levée à l'arrêt).
            self._restore_lock_if_wanted(unit)
            # Température distante : ré-injectée à chaque poll local (la clim
            # repasse sinon sur son capteur interne après un délai).
            idx = self.thermo_map.get(melcloud_local.norm_mac(mac))
            if idx:
                temp = self.getDomoticzDeviceTemp(idx)
                if temp is not None:
                    # Arrondi au pas de 0,5° selon le mode (sup. en froid/sec,
                    # inf. en chaud) : la clim ignore les dixièmes.
                    temp_inj = self._round_remote_temp(temp, unit.get('op_mode'))
                    if self.local.inject_room_temp(mac, temp_inj):
                        Domoticz.Debug("Local: {} régule sur {}°C (mesuré {}°C, thermo idx {})".format(
                            unit.get('name'), temp_inj, temp, idx))

        # Persistance du cache d'IP quand il change (découverte/révocation).
        current_ips = self.local.get_ips()
        if current_ips != self._local_ips_saved:
            self._local_ips_saved = dict(current_ips)
            self._persist_config_cache()

    def _local_sync_unit(self, unit, state):
        # Recopie l'état local (déjà en valeurs MELCloud-style) dans le dict de
        # l'unité puis synchronise les devices Domoticz. Données temps réel et
        # fiables -> PAS de debounce (contrairement au chemin cloud).
        unit['power'] = state['power']
        unit['op_mode'] = state['op_mode']
        unit['set_temp'] = state['set_temp']
        unit['set_fan'] = state['set_fan']
        unit['vaneH'] = state['vaneH']
        unit['vaneV'] = state['vaneV']
        if state.get('room_temp') is not None:
            unit['room_temp'] = state['room_temp']
        unit['next_comm'] = False
        unit['_src'] = 'local'
        Domoticz.Debug("Local poll {}: {}".format(unit.get('name'), state))
        try:
            self.domoticz_sync_switchs(unit)
        finally:
            unit['_src'] = None
        # Énergie/puissance locales -> compteurs kWh (Wh cumulés + W instantanés).
        if state.get('energy_wh') is not None:
            unit['energy_wh'] = state['energy_wh']
        unit['power_w'] = state.get('power_w') or 0
        self._sync_energy_devices()

    # Steap 20
    def onHeartbeat(self):
        # ---------------- LOCAL (prioritaire, indépendant d'internet) ----------
        self._local_heartbeat()

        # ---------------- CLOUD (secours) ---------------------------------------
        if not self._internet_ok():
            return

        # Unit info
        self.runCounter = self.runCounter - 1
        if (self.runCounter <= 0):
            Domoticz.Debug("Poll unit")
            refresh_seconds = self._cloud_refresh_seconds()
            self.runCounter = max(1, int(refresh_seconds / self.heartbeat_interval))
            if (self.melcloud_conn is not None and (self.melcloud_conn.Connecting() or self.melcloud_conn.Connected())):
               if self.melcloud_state != "LOGIN_FAILED":
                   Domoticz.Debug("Current MEL Cloud Key ID:"+str(self.melcloud_key))
                   for unit in self.list_units:
                       # Une unité servie par le local n'est PAS pollée au cloud
                       # (données cloud périmées vs temps réel local).
                       if self._unit_local_healthy(unit):
                           continue
                       self.melcloud_get_unit_info(unit)
        else:
            Domoticz.Debug("Polling unit in " + str(self.runCounter) + " heartbeats.")
            # Rafraichissement de la consommation UNIQUEMENT sur un beat sans
            # poll d'unites : evite que la reponse ListDevices se telescope avec
            # les reponses UNIT_INFO (elles partagent melcloud_state).
            self.energy_counter -= 1
            if self.energy_counter <= 0:
                self.energy_counter = self.energy_interval_beats
                # L'énergie est fournie en temps réel par le local : le refresh
                # cloud (ListDevices) ne sert que si une unité n'a pas de local sain.
                need_cloud_energy = any(not self._unit_local_healthy(u) for u in self.list_units)
                if (need_cloud_energy and self.list_units and self.melcloud_key is not None
                        and self.melcloud_conn is not None
                        and (self.melcloud_conn.Connecting() or self.melcloud_conn.Connected())
                        and self.melcloud_state not in ("LOGIN_FAILED", "UNITS_INIT", "Not Ready")):
                    Domoticz.Debug("Energy refresh (ListDevices)")
                    self.melcloud_send_data(self.melcloud_urls["list_unit"], None, "ENERGY_REFRESH")
        # Connection
        if (self.melcloud_conn is None or self.melcloud_state == "LOGIN_FAILED" or self.melcloud_state == "Not Ready"):
            self.runAgain = self.runAgain - 1
            if self.runAgain <= 0:
                # _start_connection refuse d'ouvrir une connexion parallele si
                # une est deja vivante -> plus de "connection OK" en double.
                # list_units est purge cote UNITS_INIT, inutile de le faire ici.
                self._start_connection()
                self.runAgain = 6
                self.runCounter = 0
            else:
                Domoticz.Debug("MELCloud https failed. Reconnected in "+str(self.runAgain)+" heartbeats.")

    # Steap 19
    def melcloud_create_units(self):
        Domoticz.Log("Units infos " + str(self.list_units))
        if len(Devices) == 0:
            # Init Devices
            # Creation of switches
            Domoticz.Log("Find " + str(len(self.list_units)) + " devices in MELCloud")
            for device in self.list_units:
                Domoticz.Log("Creating device: " + device['name'] + " with melID " + str(device['id']))
                for switch in self.list_switchs:
                    # Create switchs
                    if switch["typename"] == "Selector Switch":
                        switch_options = {"LevelNames": tr_levels(switch["levels"]), "LevelOffHidden": "false", "SelectorStyle": "1"}
                        Domoticz.Device(Name=device['name'] + " - "+tr(switch["name"]), Unit=switch["id"]+device['idoffset'],
                                        TypeName=switch["typename"], Image=switch["image"], Options=switch_options, Used=1).Create()
                    elif switch["typename"] == "Thermostat":
                        Domoticz.Device(Name=device['name'] + " - "+tr(switch["name"]), Unit=switch["id"]+device['idoffset'],
                                        Type=242, Subtype=1, Used=1).Create()
                    else:
                        Domoticz.Device(Name=device['name'] + " - "+tr(switch["name"]), Unit=switch["id"]+device['idoffset'],
                                        TypeName=switch["typename"], Used=1).Create()
        # Compteurs kWh : creation si absents (installs neuves ET existantes)
        # puis renseignement des valeurs deja connues via ListDevices.
        self._ensure_energy_devices()
        self._sync_energy_devices()
        self._ensure_lock_devices()
        # Couche locale : (re)déclare les unités (MAC) et persiste le cache
        # unités+IP pour les démarrages sans cloud.
        if self.local:
            self.local.set_units([{"mac": u.get('macaddr'), "name": u.get('name')}
                                  for u in self.list_units if u.get('macaddr')])
            self.local.set_cached_ips(self._local_ips_saved)
        self._persist_config_cache()

    def _start_connection(self):
        # Point UNIQUE de creation/ouverture de connexion MELCloud. Refuse d'en
        # ouvrir une seconde tant qu'une est vivante (Connecting/Connected) :
        # c'est la garde qui empeche les connexions paralleles a l'origine des
        # "connection OK" en double, de la desync d'etat et du SIGABRT.
        if self.melcloud_conn is not None and (self.melcloud_conn.Connecting() or self.melcloud_conn.Connected()):
            Domoticz.Debug("MELCloud: connexion deja vivante, pas de nouvelle ouverture")
            return False
        self.melcloud_key = None
        self.melcloud_state = "Not Ready"
        self.melcloud_conn = Domoticz.Connection(Name="MELCloud", Transport="TCP/IP",
                                                 Protocol="HTTPS", Address=self.melcloud_baseurl,
                                                 Port=self.melcloud_port)
        if __name__ == "__main__":
            self.melcloud_conn.bp = self
        self.melcloud_conn.Connect()
        return True

    def _ensure_connected(self):
        # Passe par le point unique _start_connection (garde anti-parallele).
        if self.melcloud_conn is None or not (self.melcloud_conn.Connecting() or self.melcloud_conn.Connected()):
            self._start_connection()
            return False  # pas encore connecte, on reessaiera
        return True  # verbunden oder gerade am Verbinden

    # Steap 5
    # Steap 8
    def melcloud_send_data(self, url, values, state):
        if not self._ensure_connected():
            Domoticz.Debug("MELCloud not connected yet -> skip send (will retry)")
            return True
        self.melcloud_state = state
        if self.melcloud_key is not None:
            headers = {'Content-Type': 'application/x-www-form-urlencoded;',
                       'Host': self.melcloud_baseurl,
                       'User-Agent': 'Domoticz/1.0',
                       'X-MitsContextKey': self.melcloud_key}
            if state == "SET":
                self.melcloud_conn.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': values})
            else:
                self.melcloud_conn.Send({'Verb': 'GET', 'URL': url, 'Headers': headers, 'Data': values})
        else:
            headers = {'Content-Type': 'application/x-www-form-urlencoded;',
                       'Host': self.melcloud_baseurl,
                       'User-Agent': 'Domoticz/1.0'}
            self.melcloud_conn.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': values})
        return True

    def melcloud_send_data_json(self, url, values, state):
        if not self._ensure_connected():
            Domoticz.Debug("MELCloud not connected yet -> skip send (will retry)")
            return True
        # Verhindert überlappende UNIT_INFO Requests -> reduziert 500 massiv
        self.melcloud_state = state

        #self.melcloud_state = state
        if self.melcloud_key is not None:
            headers = {'Content-Type': 'application/json;',
                       'Host': self.melcloud_baseurl,
                       'User-Agent': 'Domoticz/1.0',
                       'X-MitsContextKey': self.melcloud_key}
            if state == "SET":
                self.melcloud_conn.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': values})
            else:
                self.melcloud_conn.Send({'Verb': 'GET', 'URL': url, 'Headers': headers, 'Data': values})
        else:
            headers = {'Content-Type': 'application/x-www-form-urlencoded;',
                       'Host': self.melcloud_baseurl,
                       'User-Agent': 'Domoticz/1.0'}
            self.melcloud_conn.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': values})
        return True

    # Steap 4
    def melcloud_login(self):
        data = "AppVersion=1.34.12.0&Persist=True&Email={0}&Password={1}&Language={2}".format(Parameters["Username"], Parameters["Password"], int(Parameters["Mode3"]))
        data = "AppVersion=1.31.0.0&Email={0}&Password={1}&Language={2}".format(Parameters["Username"], Parameters["Password"], int(Parameters["Mode3"]))
        self.melcloud_send_data(self.melcloud_urls["login"], data, "LOGIN")
        return True

    # Steap 12
    # Steap 15
    def melcloud_add_unit(self, device, idoffset):
        melcloud_unit = {}
        melcloud_unit['name'] = device["DeviceName"]
        melcloud_unit['id'] = device["DeviceID"]
        melcloud_unit['macaddr'] = device["MacAddress"]
        melcloud_unit['sn'] = device["SerialNumber"]
        melcloud_unit['building_id'] = device["BuildingID"]
        melcloud_unit['power'] = ""
        melcloud_unit['op_mode'] = ""
        melcloud_unit['room_temp'] = ""
        melcloud_unit['set_temp'] = ""
        melcloud_unit['set_fan'] = ""
        melcloud_unit['vaneH'] = ""
        melcloud_unit['vaneV'] = ""
        melcloud_unit['next_comm'] = False
        melcloud_unit['idoffset'] = idoffset
        # Energie (Wh) et SN du groupe exterieur, pour les compteurs kWh.
        # CurrentEnergyConsumed n'existe que dans ListDevices (pas dans Device/Get).
        dev = device.get("Device", {})
        try:
            melcloud_unit['energy_wh'] = float(dev.get("CurrentEnergyConsumed") or 0) if dev.get("HasEnergyConsumedMeter") else 0.0
        except Exception:
            melcloud_unit['energy_wh'] = 0.0
        melcloud_unit['outdoor_sn'] = None
        melcloud_unit['model'] = None   # modèle unité intérieure (ex. MFZ-KT25VG)
        for u in dev.get("Units", []):
            if not u.get("IsIndoor", True):
                melcloud_unit['outdoor_sn'] = u.get("SerialNumber")
            elif not melcloud_unit['model']:
                melcloud_unit['model'] = u.get("Model")
        self.list_units.append(melcloud_unit)

    # Steap 7
    def melcloud_units_init(self):
        self.melcloud_send_data(self.melcloud_urls["list_unit"], None, "UNITS_INIT")
        return True

    # --- Compteurs de consommation (kWh) --------------------------------------
    # Plage d'Unit dediee pour NE PAS decaler les blocs par clim existants
    # (1..99 = Mode/Fan/...). 100+ = kWh interieur par clim, 150+ = kWh par
    # groupe exterieur (somme des clims partageant le meme SN exterieur).
    ENERGY_UNIT_INDOOR_BASE = 100
    ENERGY_UNIT_OUTDOOR_BASE = 150

    def _iter_ata_devices(self, response):
        # Parcourt une reponse ListDevices et rend chaque clim (Type 0),
        # ou qu'elle soit (Devices / Areas / Floors + Areas des Floors).
        if not isinstance(response, list):
            return
        for building in response:
            struct = building.get("Structure", {})
            for dev in struct.get("Devices", []):
                if dev.get("Type") == 0:
                    yield dev
            for area in struct.get("Areas", []):
                for dev in area.get("Devices", []):
                    if dev.get("Type") == 0:
                        yield dev
            for floor in struct.get("Floors", []):
                for dev in floor.get("Devices", []):
                    if dev.get("Type") == 0:
                        yield dev
                for area in floor.get("Areas", []):
                    for dev in area.get("Devices", []):
                        if dev.get("Type") == 0:
                            yield dev

    def _outdoor_order(self):
        # Liste ordonnee des SN de groupes exterieurs uniques (ordre d'apparition).
        order = []
        for unit in self.list_units:
            sn = unit.get('outdoor_sn') or "?"
            if sn not in order:
                order.append(sn)
        return order

    def _ensure_energy_devices(self):
        # Cree les compteurs kWh manquants (idempotent : ne touche pas aux
        # devices existants). Fonctionne installs neuves ET existantes.
        block = len(self.list_switchs)
        for unit in self.list_units:
            idx = unit['idoffset'] // block
            u_in = self.ENERGY_UNIT_INDOOR_BASE + idx
            if u_in not in Devices:
                Domoticz.Log("Creating energy device (indoor): {} - Consommation (Unit {})".format(unit['name'], u_in))
                Domoticz.Device(Name=unit['name'] + " - " + tr("Consumption"), Unit=u_in,
                                TypeName="kWh", Used=1).Create()
        for j, sn in enumerate(self._outdoor_order()):
            u_out = self.ENERGY_UNIT_OUTDOOR_BASE + j
            if u_out not in Devices:
                Domoticz.Log("Creating energy device (outdoor): Groupe ext. {} (Unit {})".format(sn, u_out))
                Domoticz.Device(Name=tr("Outdoor group") + " " + str(sn) + " - " + tr("Consumption"), Unit=u_out,
                                TypeName="kWh", Used=1).Create()

    def _sync_energy_devices(self):
        # Met a jour les compteurs kWh : interieur par clim + somme par groupe
        # exterieur. sValue "puissance;energie" (W;Wh). La puissance instantanee
        # vient du LOCAL (power_w) ; le cloud ne la fournit pas (0).
        # Dirty-check via _update_if_changed.
        block = len(self.list_switchs)
        outdoor_totals = {}
        outdoor_watts = {}
        for unit in self.list_units:
            idx = unit['idoffset'] // block
            wh = float(unit.get('energy_wh') or 0)
            watts = int(unit.get('power_w') or 0)
            u_in = self.ENERGY_UNIT_INDOOR_BASE + idx
            if u_in in Devices:
                self._update_if_changed(Devices[u_in], 0, "{};{:.0f}".format(watts, wh))
            sn = unit.get('outdoor_sn') or "?"
            outdoor_totals[sn] = outdoor_totals.get(sn, 0.0) + wh
            outdoor_watts[sn] = outdoor_watts.get(sn, 0) + watts
        for j, sn in enumerate(self._outdoor_order()):
            u_out = self.ENERGY_UNIT_OUTDOOR_BASE + j
            if u_out in Devices:
                self._update_if_changed(Devices[u_out], 0, "{};{:.0f}".format(
                    outdoor_watts.get(sn, 0), outdoor_totals.get(sn, 0.0)))

    def melcloud_set_json(self, unit, flag):
        # Sicherstellen, dass wir saubere Typen haben
        payload = {
            "DeviceID": int(unit["id"]),
            "EffectiveFlags": int(flag),
            "HasPendingCommand": True,
            "Power": bool(unit.get("power", False)),
        }

        # OperationMode nur mitsenden, wenn Flag es auch setzt (2)
        if (flag & 2) and unit.get("op_mode", None) not in ("", None):
            payload["OperationMode"] = int(unit["op_mode"])

        if unit.get("set_temp", None) not in ("", None) and (flag & 4):
            payload["SetTemperature"] = float(unit["set_temp"])

        if unit.get("set_fan", None) not in ("", None) and (flag & 8):
            payload["SetFanSpeed"] = int(unit["set_fan"])

        if unit.get("vaneH", None) not in ("", None) and (flag & 256):
            payload["VaneHorizontal"] = int(unit["vaneH"])

        if unit.get("vaneV", None) not in ("", None) and (flag & 16):
            payload["VaneVertical"] = int(unit["vaneV"])

        data = json.dumps(payload, separators=(",", ":"))
        payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        Domoticz.Debug("SET JSON SEND: {}".format(payload_json))
        self.melcloud_send_data_json(self.melcloud_urls["set_unit"], data, "SET")
        return True

    def melcloud_get_unit_info(self, unit):
        now = time.time()
        device_id = unit.get('id')

        last = self.unit_info_last_ts.get(device_id, 0)
        if (now - last) < self.unit_info_min_interval:
            Domoticz.Debug("Skip UNIT_INFO (rate-limit) for DeviceID {} (delta {:.2f}s)".format(device_id, now - last))
            return True

        self.unit_info_last_ts[device_id] = now

        url = self.melcloud_urls["unit_info"] + "?id=" + str(unit['id']) + "&buildingID=" + str(unit['building_id'])
        self.melcloud_send_data(url, None, "UNIT_INFO")
        return True

    def _update_if_changed(self, dev, nValue, sValue, Image=None):
        # N'ecrit le device que si nValue/sValue changent reellement : evite de
        # re-declencher les scripts dzVents (et donc des SET vers MelCloud) a
        # chaque poll alors que rien n'a bouge. Ceinture-bretelles anti-boucle.
        # L'icone est comparee aussi : apres un changement d'IDs d'icones (pack
        # embarque, icones supprimees/recreees), un device a valeur stable doit
        # quand meme recevoir sa nouvelle icone.
        sValue = str(sValue)
        try:
            if dev.nValue == nValue and str(dev.sValue) == sValue:
                if Image is None or getattr(dev, 'Image', None) == Image:
                    return
        except Exception:
            pass
        if Image is None:
            dev.Update(nValue=nValue, sValue=sValue)
        else:
            dev.Update(nValue=nValue, sValue=sValue, Image=Image)

    def _update_room_temp(self, unit):
        # Met a jour uniquement le device "Room Temp" (id 6) de l'unite, sans
        # toucher au reste. Utilise quand la trame est rejetee (voir onMessage).
        u = self.list_switchs[5]["id"] + unit["idoffset"]
        if u in Devices:
            dev = Devices[u]
            self._update_if_changed(dev, dev.nValue, str(unit['room_temp']))

    def _write_mode_debounced(self, unit, dev, nValue, sValue, Image=None):
        # Anti-rebond sur le SEUL device surveille par dzVents (Mode) : on ne
        # change sa valeur que si elle est confirmee sur 2 lectures de suite.
        # Un rebond MelCloud (valeurs alternees) n'est jamais confirme -> pas de
        # flapping ni de boucle dzVents. Un vrai changement passe au 2e poll.
        key = (nValue, str(sValue))
        if '_mode_applied' not in unit:
            # 1er passage : on s'aligne sur l'etat actuel du device (pas de
            # latence inutile si la valeur lue correspond deja a l'affichage).
            try:
                unit['_mode_applied'] = (dev.nValue, str(dev.sValue))
            except Exception:
                unit['_mode_applied'] = None
        if key == unit.get('_mode_applied'):
            unit['_mode_pending'] = key
            return  # deja affiche, rien a faire
        if key == unit.get('_mode_pending'):
            # meme valeur 2x de suite -> on confirme et on applique
            unit['_mode_applied'] = key
            self._update_if_changed(dev, nValue, str(sValue), Image)
        else:
            # nouveau candidat -> on attend une 2e confirmation, on n'ecrit pas
            unit['_mode_pending'] = key
            Domoticz.Debug("Mode debounce {0}: '{1}' en attente de confirmation".format(unit['name'], sValue))

    def domoticz_sync_switchs(self, unit):
        # Default value in case of problem
        setDomFan = 0
        setDomTemp = 0
        setDomVaneH = 0
        setDomVaneV = 0
        if unit['next_comm'] is not False:
            Devices[self.list_switchs[6]["id"]+unit["idoffset"]].Update(nValue=1, sValue=str(unit['next_comm']))
        else:
            if unit['power']:
                switch_value = 1
                for level, mode in self.domoticz_levels["mode"].items():
                    if mode == unit['op_mode']:
                        setModeLevel = level
            else:
                switch_value = 0
                setModeLevel = '0'
            for level, pic in self.domoticz_levels["mode_pic"].items():
                if level == setModeLevel:
                    setPicID = pic
                    mode_dev = Devices[self.list_switchs[0]["id"]+unit["idoffset"]]
                    if unit.get('_src') == 'local':
                        # Données LOCALES = temps réel fiable : écriture directe
                        # (le debounce ne sert qu'à filtrer les snapshots périmés
                        # du cloud). On aligne l'état du debounce pour un éventuel
                        # retour au chemin cloud sans latence parasite.
                        self._update_if_changed(mode_dev, switch_value, setModeLevel, setPicID)
                        unit['_mode_applied'] = (switch_value, str(setModeLevel))
                        unit['_mode_pending'] = unit['_mode_applied']
                    else:
                        # Mode = SEUL device surveille par dzVents -> ecriture avec
                        # anti-rebond (confirmation sur 2 lectures) pour tuer tout
                        # flapping residuel. Les autres devices s'ecrivent directement.
                        self._write_mode_debounced(unit, mode_dev,
                                                   switch_value, setModeLevel, setPicID)
            for level, fan in self.domoticz_levels["fan"].items():
                if fan == unit['set_fan']:
                    setDomFan = level

            for level, pic in self.domoticz_levels["fan_pic"].items():
                if level == setDomFan:
                    setPicID = pic
                    self._update_if_changed(Devices[self.list_switchs[1]["id"]+unit["idoffset"]],
                                            switch_value, setDomFan, setPicID)

            self._update_if_changed(Devices[self.list_switchs[2]["id"]+unit["idoffset"]],
                                    switch_value, str(unit['set_temp']))

            for level, vaneH in self.domoticz_levels["vaneH"].items():
                if vaneH == unit['vaneH']:
                    setDomVaneH = level

            my_id = self.list_switchs[3]["id"]+unit["idoffset"]
            Domoticz.Debug("Update unit " + str(my_id) + " my information 2. ")
            for level, pic in self.domoticz_levels["vaneH_pic"].items():
                if level == setDomVaneH:
                    setPicID = pic
                    self._update_if_changed(Devices[self.list_switchs[3]["id"]+unit["idoffset"]],
                                            switch_value, setDomVaneH, setPicID)

            for level, vaneV in self.domoticz_levels["vaneV"].items():
                if vaneV == unit['vaneV']:
                    setDomVaneV = level
            if self._is_console(unit):
                vaneV_pic = self.domoticz_levels["vaneVConsole_pic"].items()
            else:
                vaneV_pic = self.domoticz_levels["vaneV_pic"].items()
            for level, pic in vaneV_pic:
                if level == setDomVaneV:
                    setPicID = pic
                    self._update_if_changed(Devices[self.list_switchs[4]["id"]+unit["idoffset"]],
                                            switch_value, setDomVaneV, setPicID)

            self._update_if_changed(Devices[self.list_switchs[5]["id"]+unit["idoffset"]],
                                    switch_value, str(unit['room_temp']))


global _plugin
_plugin = BasePlugin()


def onStart():
    """ On start """
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    """ On stop """
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    """ On connect """
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    """ On message """
    _plugin.onMessage(Connection, Data)


def onCommand(Unit, Command, Level, Hue):
    global _plugin
    """ On command """
    _plugin.onCommand(Unit, Command, Level, Hue)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    """ On notification """
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    """ On disconnect """
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    """ Heartbeat """
    global _plugin
    _plugin.onHeartbeat()


# Tests hors Domoticz : voir tests/ (stub Domoticz.py + test_plugin_local.py,
# harnais lecture seule contre les clims réelles). Non déployés sur le Minix.
