# Release Notes — domoticz-python-melcloud

*[🇬🇧 English](ReleaseNotes.md) · **🇫🇷 Français***

## v2.2.3 — 2026 (Bastien1307, Claude)

- **Uniformisation complète des préfixes de logs.** Chaque ligne annonce
  maintenant sa **source/nature** :
  - « **Cloud :** » — connexion, découverte, lecture des unités/énergie, backoff,
    erreurs HTTP, **gating Internet** (il ne concerne que le cloud) ;
  - « **Local :** » — poll local, découverte IP, température distante, verrou
    télécommande ;
  - « **Cache :** » — chargement/persistance du cache ;
  - « **Icônes :** » — résolution des icônes ;
  - « **Action :** » — commande venue de **Domoticz** (sens Domoticz → clim) ;
  - « **Plugin :** » — cycle de vie (arrêt), création de devices, reflets internes.
- **Commandes** : la ligne d'**envoi** porte la **source réellement utilisée** :
  « Local : commande envoyée … » si le local prend la main, sinon « Cloud :
  commande envoyée … » (la trace de bascule vers le cloud, qui manquait, a été
  ajoutée).
- Nettoyage d'un log debug cryptique hérité (« … infos 2. » → « mise à jour du
  device N (vanne horizontale) »).
- **Nettoyage de code** : 2 lignes de code commentées obsolètes supprimées. Le
  callback `onNotification` (jamais exploité) est **conservé** pour la complétude
  de l'interface de plugin, mais passé en `Debug` (préfixe « Plugin : »), donc
  invisible dans le log courant.

## v2.2.2 — 2026 (Bastien1307, Claude)

- **Cohérence des logs.** Le flux **cloud** est désormais préfixé « **Cloud :** »
  (connexion, découverte bâtiments/zones/étages, liste des unités, énergie,
  backoff, erreurs HTTP), à l'image des préfixes « Local : » / « Cache : » /
  « Icônes : ». On repère immédiatement la **source** de chaque ligne de log.

## v2.2.1 — 2026 (Bastien1307, Claude)

- **Clarté des logs.**
- Le **périmètre de recherche** MELCloud est désormais affiché **entre
  guillemets** (`"Devices"` / `"Areas"` / `"Floors"` — clés brutes de l'API,
  inchangées) au lieu d'être collé au texte. Voir `0 climatisation(s) dans
  "Floors"` est **normal** : les clims sont rangées dans `"Areas"` (les zones).
- Le log de rechargement du cache ne dit plus « **sans cloud** » (trompeur : il a
  lieu à **chaque** démarrage, avant le cloud) mais « **depuis le cache local
  (démarrage immédiat)** ». Le cloud se connecte juste après si internet est là
  et `Mode2 ≠ off`.
- **Typographie française** : espace avant « : » dans tous les logs (plugin.py +
  melcloud_local.py).

## v2.2.0 — 2026 (Bastien1307, Claude)

- **Intervalles local et cloud repensés.**
- **Local (`Refresh interval wifi (local)`)** : ajout du pas **5s** pour une
  interrogation locale ultra-réactive (valeurs autorisées : 5s, 10s, 20s, 30s
  *(défaut)*, 1m, 2m, 5m, ou `Off`).
- **Cloud (`Refresh interval web (cloud)`)** : **suppression des pas trop
  agressifs** (1s / 5s / 10s / 20s) qui déclenchaient le *throttle* MELCloud
  (blocage temporaire du compte). Le cloud commence désormais à **1 minute**,
  avec **5 min par défaut** (valeurs : 1m, 2m, 5m *(défaut)*, 10m, ou `Off`).
- **Nouvelle option « Off » sur le cloud** (comme le local en avait déjà une),
  avec un comportement important à comprendre :
  - Au **démarrage**, le cloud est utilisé **une seule fois** pour **découvrir
    les climatiseurs** (liste des unités + adresses MAC). Cette étape est
    indispensable : sans elle, une **première installation** ne pourrait jamais
    trouver les unités (le local a besoin des MAC pour cibler les adaptateurs).
  - **Une fois la découverte faite**, le cloud devient **totalement muet** :
    plus **aucune** requête cloud, **y compris l'énergie** (le rafraîchissement
    `ListDevices` toutes les 30 min est lui aussi coupé) et plus aucune tentative
    de reconnexion. Tout passe alors par le **local** et le **cache** persisté.
  - **Optimisation** : au démarrage, si le **cache contient déjà toutes les
    unités avec leur MAC**, la découverte cloud est **entièrement sautée** — le
    plugin est muet dès le démarrage, sans le moindre `login`/`ListDevices`. Le
    cloud n'est donc réellement sollicité qu'à la **première** installation
    (cache vide) ou après l'ajout d'une nouvelle clim. (Les compteurs kWh ne sont
    pas touchés sur ce chemin : le local les renseigne ensuite.)
- **Local ET cloud coupés** (`Mode1=off` + `Mode2=off`) : c'est accepté, mais un
  **avertissement clair** (`Domoticz.Error`) est logué au démarrage — après la
  découverte initiale des clims, plus **aucune** donnée n'est rafraîchie.

## v2.1.4 — 2026 (Bastien1307, Claude)

- **Logs entièrement en français**, de façon **fixe** (indépendante du paramètre
  `Language`). Toutes les lignes de log encore anglaises ou mixtes de `plugin.py`
  et `melcloud_local.py` sont traduites : connexion MELCloud, découverte des
  bâtiments / zones / étages, interrogation des unités, commandes envoyées
  (chaud, froid, ventilation, déshumidification, auto, extinction), consigne,
  rafraîchissement de l'énergie, erreurs HTTP, cycle de scan local, etc.
- Motivation : lors d'un dépannage avec un utilisateur d'une autre langue, quand
  je lui demande de chercher telle ligne de log, il doit voir **exactement le
  même texte** que moi.
- Les **noms de devices** (fonction `tr()`) ne changent pas : ils continuent de
  suivre la langue choisie dans le plugin. Seuls les logs sont concernés.
- Nettoyage complémentaire : **tous les commentaires de code** (allemand,
  anglais et accents français manquants) sont passés en français correct, et le
  dernier log encore anglais (résumé `Found N devices in building...` de
  `searchUnits`) a été traduit.

## v2.1.3 — 2026 (Bastien1307, Claude)

- Robustesse : si l'utilisateur supprime les devices d'une clim dans Domoticz
  (en gardant ceux des autres), ils sont désormais **recréés automatiquement**.
  Avant, la création était gardée par `len(Devices)==0` → les devices supprimés
  n'étaient jamais recréés et `onHeartbeat` plantait sur un `KeyError`. Création
  rendue idempotente (par unité) et garantie avant chaque synchronisation.
  (Remonté par harrykausl sur le forum.)

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
