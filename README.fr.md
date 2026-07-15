# domoticz-python-melcloud

*[🇬🇧 English](README.md) · **🇫🇷 Français***

Plugin Domoticz pour climatisations **Mitsubishi Electric** — contrôle **LOCAL
d'abord** (adaptateur WiFi MAC-577IF-2E, HTTP sur le LAN), **cloud MELCloud en
secours**.

> **Fork.** Ce dépôt part de [schurgan/domoticz-python-melcloud](https://github.com/schurgan/domoticz-python-melcloud)
> (v1.0.0), lui-même fork de [gysmo38/domoticz-python-melcloud](https://github.com/gysmo38/domoticz-python-melcloud),
> le plugin cloud d'origine. À partir de la **v2.0.0**, le plugin pilote les
> clims **en direct sur le LAN** et ne descend au cloud qu'en secours : c'est un
> changement d'architecture, pas une simple variante. Aucune remontée vers
> l'amont n'est prévue.

## Fonctionnalités

- **Contrôle local temps réel** (poll 10 s à 5 min, au choix) : marche/arrêt,
  mode, consigne, ventilation, vannes — sans passer par le cloud, latence quasi
  nulle, fonctionne **même sans internet** (cache unités + IP persisté).
- **Cloud MELCloud en secours** automatique : si une clim ne répond plus en
  local, elle est pollée/commandée via le cloud jusqu'à guérison.
- **Température distante** : chaque clim peut réguler sur un thermomètre
  Domoticz de la pièce (paramètre `mac=idx`) au lieu de son capteur interne —
  valeur ré-injectée à chaque poll, arrondie au pas de 0,5° (supérieur en
  froid/sec, inférieur en chaud).
- **Puissance instantanée réelle (W)** + énergie cumulée (kWh) par clim et par
  groupe extérieur (somme multi-split).
- **Verrou télécommande** (sélecteur par clim, local uniquement) :
  Déverrouillé / Power / Mode / Température / Tout.
- **Découverte réseau zéro-config** : IP trouvées par MAC (ARP + scan du LAN,
  sous-réseaux déduits des autres matériels Domoticz — fonctionne aussi en
  conteneur Docker bridge), identité **toujours vérifiée par MAC** avant tout
  envoi, IP révoquée et redécouverte si le DHCP change.
- **Icônes embarquées** (`icons/*.zip`) : installées/reliées automatiquement
  par nom au démarrage — rien à uploader à la main.
- Détection console au sol (modèles `MFZ*`) vs split mural pour les icônes de
  vane adaptées.

## Installation

1. Copier le dossier du plugin dans `domoticz/plugins/` :
   `plugin.py`, `melcloud_local.py`, `pymitsubishi/` (lib vendorée),
   `icons/` (26 zips), `requirements.txt`.
2. Installer les dépendances python (voir ci-dessous).
3. Redémarrer Domoticz, activer « Accept new Hardware Devices », ajouter le
   matériel type « MELCloud plugin ».

### Dépendances (requirements.txt)

La couche locale a besoin de `requests` et `pycryptodome` dans le **python de
Domoticz** (pas un venv à côté). Sans eux, le plugin fonctionne en cloud-only
et l'explique clairement au log.

- **Install classique** :
  ```
  sudo pip3 install -r plugins/domoticz-python-melcloud/requirements.txt
  ```
  (sur Debian récent, ajouter `--break-system-packages`, ou passer par
  `sudo apt install python3-pycryptodome python3-requests`)
- **Domoticz en Docker** — deux options :
  - immédiat : `docker exec <conteneur> pip3 install -r /opt/domoticz/userdata/plugins/domoticz-python-melcloud/requirements.txt`
    (à refaire si le conteneur est recréé) ;
  - durable : intégrer le `requirements.txt` au script de démarrage du conteneur
    (`userdata/customstart.sh` : téléchargement en cache puis install au premier
    lancement — même mécanisme que le plugin Domoticz-Zigbee).

## Paramètres

| Champ | Rôle |
|---|---|
| Email / Password | compte MELCloud (sert au démarrage initial et au secours cloud) |
| Refresh interval wifi (local) | cadence du poll local (défaut 30 s ; `Off` = cloud uniquement) |
| Refresh interval web (cloud) | cadence du poll cloud de secours (5 m conseillé) |
| Remote temp | optionnel : `mac=idx,mac=idx` — thermomètre Domoticz par clim (température distante) |
| Language / Debug | langue MELCloud / niveau de log |
| ID device Internet | optionnel : device Domoticz témoin de la connexion internet (ne suspend que le cloud) |

## Devices créés (par clim)

Mode, Fan, Temp (consigne), Vane Horizontal, Vane Vertical, Room Temp,
Unit Infos, + compteurs kWh (clim et groupe extérieur, avec watts réels),
+ Verrou télécommande (non « utilisé » par défaut).

## Soutien

Ce plugin part d'un plugin existant, mais il a été **largement retravaillé** —
ce n'est pas un copier-coller avec une lib branchée dessus :

- **Débogage de fond du plugin cloud** : fin des crashes SIGABRT (connexion
  concurrente, `onConnect` non idempotent), fin du flapping Marche/Arrêt
  (trames cloud « zéro-ées », anti-rebond sur le Mode), backoff API.
- **Refonte de l'existant** : la consigne est devenue un **vrai Thermostat**
  (0,5°) là où le plugin utilisait depuis toujours un Selector Switch à paliers
  de 1° ; compteurs d'énergie par clim et par groupe extérieur ; GMT Offset
  remplacé par une conversion DST automatique.
- **Contrôle local ajouté de bout en bout** (v2.0.0) : pilotage LAN, découverte
  des IP par MAC, cache hors-ligne, bascule automatique vers le cloud,
  température distante, watts réels, verrou télécommande, icônes embarquées. Il
  s'appuie sur la lib pymitsubishi, mais toute l'intégration Domoticz,
  la découverte réseau et la logique local-first/fallback ont été écrites ici.

Si le plugin vous rend service, vous pouvez m'offrir un café :

**[☕ paypal.me/sebastienRanc](https://paypal.me/sebastienRanc)**

> Choisissez de préférence l'option **« Entre proches »** (et non « bien ou
> service ») : le don arrive alors sans frais.

Pensez aussi aux auteurs sur lesquels ce travail s'appuie :
[gysmo38](https://github.com/gysmo38/domoticz-python-melcloud) et
[schurgan](https://github.com/schurgan/domoticz-python-melcloud) (plugin cloud
d'origine), et [pymitsubishi](https://github.com/pymitsubishi/pymitsubishi)
(protocole local).

## Crédits & versions

Détail complet dans [ReleaseNotes.fr.md](ReleaseNotes.fr.md).

- **v0.x → v1.0.0 (base)** : gysmo38, schurgan, Dalonsic, ChatGPT — plugin cloud
  MELCloud d'origine (https://github.com/schurgan/domoticz-python-melcloud).
- **v1.1.0** : [Bastien1307](https://github.com/Bastien1307),
  ChatGPT — anti-flapping, anti-crash, compteurs kWh, DST auto, backoff.
- **v2.0.0** : [Bastien1307](https://github.com/Bastien1307), Claude — couche
  locale (local-first/cloud-fallback), température distante, watts réels,
  verrou télécommande, icônes embarquées, découverte réseau, cache hors-ligne.
- Couche locale basée sur la lib [pymitsubishi](https://github.com/pymitsubishi/pymitsubishi)
  (MIT, vendorée dans `pymitsubishi/`).
