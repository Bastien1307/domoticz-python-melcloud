# Release Notes — domoticz-python-melcloud

*[🇬🇧 English](ReleaseNotes.md) · **🇫🇷 Français***

## v2.1.2 — 2026 (Bastien1307, Claude)

- Compatibilité pycryptodome : le paquet apt Debian/Raspberry Pi
  (`python3-pycryptodome`) expose le module sous `Cryptodome`, pas `Crypto` :
  `import Crypto` échouait alors que pycryptodome était installé — la couche
  locale se désactivait à tort et tout retombait sur le cloud. Un pont
  `Cryptodome` → `Crypto` est mis en place avant l'import de la lib vendorée, si
  bien que les deux méthodes d'installation (pip et apt) fonctionnent.
  (Remonté par harrykausl sur le forum.)

## v2.1.1 — 2026 (Bastien1307, Claude)

- Intervalle de rafraîchissement cloud (Mode2) robuste au champ vide/invalide :
  un champ vide ne plante plus `onStart` (`int('')` levait une exception), repli
  sur 120 s comme le fait déjà l'intervalle local (Mode1).

## v2.1.0 — 2026 (Bastien1307, Claude)

**Interface en français**
- Les devices et sélecteurs créés au démarrage sont **traduits en français**
  quand le paramètre `Language` vaut Français ; toute autre langue reste en
  anglais. Concerne les noms de devices (Mode, Ventilation, Consigne, Vanne
  horizontale/verticale, Temp. pièce, Infos unité, Verrou télécommande,
  Consommation, Groupe ext.) et les libellés des sélecteurs (modes, vitesses
  de ventilation, oscillation des vannes, niveaux du verrou).
- Le **formulaire de configuration** reste en anglais : ses libellés sont figés
  par Domoticz avant l'exécution du plugin, non traduisibles.
- Sans effet sur une installation existante (Domoticz ne renomme jamais un
  device déjà créé) ni sur la logique interne (dispatch par numéro d'unité).

## v2.0.0 — 2026-07-11 (Bastien1307, Claude)

**Contrôle LOCAL d'abord, cloud MELCloud en secours** — changement
d'architecture : le plugin n'est plus un client MELCloud, c'est un pilote LAN
qui garde le cloud en secours. Basé sur une campagne de tests réels des
adaptateurs MAC-577IF-2E (HTTP port 80).

- **Couche locale** (`melcloud_local.py` + lib [pymitsubishi](https://github.com/pymitsubishi/pymitsubishi)
  0.5.2 vendorée dans `pymitsubishi/`) : lecture d'état temps réel et commandes
  (power, mode, consigne, ventilation, vannes) directement sur le LAN.
- **Deux cadences distinctes** au choix : `Refresh interval wifi (local)`
  (10 s à 5 min, ou Off) et `Refresh interval web (cloud)` (secours).
- **Découverte réseau zéro-config** : IP trouvées par MAC (table ARP puis scan
  progressif du LAN ; sous-réseaux déduits des IP des autres matériels Domoticz
  via l'API locale → fonctionne aussi en **conteneur Docker bridge**).
  **Identité toujours vérifiée par la MAC** lue dans la réponse de la clim avant
  tout envoi ; IP révoquée et redécouverte si le DHCP redistribue.
- **Cache persisté** (`Domoticz.Configuration`) : unités + IP → **démarrage et
  fonctionnement 100 % local sans internet**.
- **Bascule automatique** : 3 échecs locaux consécutifs → poll/commandes via le
  cloud, retentatives locales périodiques (auto-guérison). Les protections
  anti-flapping ne s'appliquent plus qu'au chemin cloud (les données locales
  sont fiables → écriture directe, sans debounce).
- `requirements.txt` (`pycryptodome`, `requests`) + intégration
  `customstart.sh` pour les installs Docker. Sans pycryptodome : mode cloud-only
  propre avec message explicite.
- Le device témoin internet (Mode4) ne suspend plus que le chemin cloud.

**Température distante**
- Param `Remote temp` (`mac=idx,mac=idx`) : chaque clim régule sur un
  **thermomètre Domoticz de la pièce**, ré-injecté à chaque poll local. Vide =
  capteur interne (comportement historique).
- Arrondi de la valeur injectée au **pas de 0,5°** selon le mode : SUPÉRIEUR en
  froid/sec, INFÉRIEUR en chaud, au plus proche sinon (la clim ignore les
  dixièmes ; l'arrondi conservateur évite l'arrêt prématuré). Les multiples de
  0,5 exacts restent inchangés.

**Puissance**
- **Puissance instantanée réelle (W)** dans les compteurs kWh (le cloud
  renvoyait toujours 0 W) + somme par groupe extérieur.

**Verrou télécommande** — nouveau sélecteur par clim (Déverrouillé / Power /
Mode / Température / Tout), fonction locale non exposée par le cloud.
- À l'**arrêt du plugin** : les verrous actifs sont **levés physiquement** (sans
  toucher aux sélecteurs Domoticz) — personne ne reste bloqué télécommande en
  main si Domoticz est éteint.
- Au **démarrage** : si un sélecteur dit « verrouillé », le verrou est
  **ré-appliqué** dès que la clim répond en local.

**Icônes & interface**
- Icônes résolues **par nom** — plus aucun ID d'icône codé en dur. Base manquante
  → chargement automatique du zip embarqué `icons/<Base>.zip` ; base déjà en BDD
  (upload manuel historique) → reliée telle quelle, **sans doublon**. Repli icône
  standard si zip absent.
- 26 zips d'icônes embarqués dans `icons/` (constat : Domoticz ne lit qu'UNE
  icône par zip de plugin — un zip multi-icônes ne garde que la dernière ligne
  d'icons.txt).
- Détection **console au sol vs split mural par modèle** (`MFZ*` = console) pour
  les icônes de vane vertical — remplace le nom de pièce codé en dur.
- Les chaînes `if Level == …: image = …` de `onCommand` remplacées par des
  lookups dans les maps (source unique).
- `_update_if_changed` compare aussi l'icône : un device à valeur stable reçoit
  quand même sa nouvelle icône après un changement d'IDs.

**Divers**
- Nettoyage des logs répétitifs (poll local silencieux hors Debug). README
  réécrit + ces ReleaseNotes.

## v1.1.0 — 2026 (Bastien1307, ChatGPT) — sur la base schurgan v1.0.0

Correctifs et ajouts majeurs par rapport au dépôt d'origine
(https://github.com/schurgan/domoticz-python-melcloud) :

- **Consigne = vrai Thermostat** (Type 242/SetPoint, précision 0,5°) au lieu du
  Selector Switch d'origine à paliers de 1° (`16|17|…|31`) — réglage plus
  précis et interface adaptée.
- **Fin du flapping Marche/Arrêt** : validation de trame (rejet des snapshots
  cloud « zéro-és » physiquement impossibles) + anti-rebond sur le sélecteur
  Mode (confirmation sur 2 lectures) + dirty-check des écritures de devices.
- **Fin des crashes SIGABRT** : point unique de connexion avec garde
  anti-parallèle, `onConnect` idempotent, gardes de type sur toutes les
  réponses, purge des unités en double.
- **Compteurs d'énergie (kWh)** par clim (Unit 100+) et par **groupe extérieur**
  (Unit 150+, somme multi-split), rafraîchis périodiquement via ListDevices.
- Champ **GMT Offset supprimé** : conversion UTC→local automatique
  (`astimezone`, DST géré).
- **Device témoin internet** optionnel (Mode4) via l'API JSON locale.
- **Backoff API** sur erreurs HTTP répétées (500/429).

## v0.1 → v1.0.0 (gysmo38, schurgan, Dalonsic, ChatGPT)

Historique du plugin cloud d'origine : voir l'en-tête de `plugin.py` et
https://github.com/schurgan/domoticz-python-melcloud.
