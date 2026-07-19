# -*- coding: utf-8 -*-
"""
melcloud_local.py — Couche de contrôle LOCAL des clims Mitsubishi (adaptateur
MAC-577IF-2E, HTTP port 80) pour le plugin Domoticz MELCloud.

Stratégie « local d'abord, cloud en secours » : ce module parle directement aux
adaptateurs WiFi via la lib vendorée `pymitsubishi/` (aucun cloud). Le plugin
l'utilise pour les polls et les commandes ; en cas d'échec local il retombe sur
le chemin MELCloud historique.

Points clés (validés par la campagne de test du 2026-07-11, voir
scripts/_melcloud_local_test/.docs/PROBE_LOCAL_MITSUBISHI.md sur le Mac) :
- identité TOUJOURS vérifiée par la MAC renvoyée dans la réponse /smart
  (jamais de confiance aveugle à une IP : le DHCP peut redistribuer) ;
- latence d'application ~5 s : une commande n'est PAS relue immédiatement ;
- température distante (set_current_temperature) : la clim régule sur la valeur
  injectée ; à ré-injecter périodiquement (sinon retour capteur interne) ;
- énergie locale : energy_hecto_watt_hour (× 100 = Wh) + puissance instantanée.

Ce module n'importe PAS Domoticz : les logs passent par des callbacks injectés
(log/debug/error) → testable hors Domoticz (stub ou script standalone).
"""

import ipaddress
import re
import socket
import subprocess
import sys
import time

# Compat pycryptodome : la lib vendorée fait `from Crypto...`. Installé par pip,
# pycryptodome fournit le namespace `Crypto` ; mais le paquet Debian/Raspberry Pi
# `python3-pycryptodome` (apt) le fournit sous `Cryptodome` (renommé pour ne pas
# entrer en conflit avec l'ancien pycrypto). Sans ce pont, `import Crypto` échoue
# alors que pycryptodome EST installé -> couche locale désactivée à tort. On
# alias donc Cryptodome -> Crypto avant l'import. La lib vendorée reste inchangée.
if 'Crypto' not in sys.modules:
    try:
        import Crypto  # noqa: F401 (pip pycryptodome : namespace natif)
    except Exception:
        try:
            import Cryptodome
            import Cryptodome.Cipher
            import Cryptodome.Cipher.AES
            import Cryptodome.Random
            import Cryptodome.Util.Padding
            sys.modules['Crypto'] = Cryptodome
            sys.modules['Crypto.Cipher'] = Cryptodome.Cipher
            sys.modules['Crypto.Cipher.AES'] = Cryptodome.Cipher.AES
            sys.modules['Crypto.Random'] = Cryptodome.Random
            sys.modules['Crypto.Util'] = Cryptodome.Util
            sys.modules['Crypto.Util.Padding'] = Cryptodome.Util.Padding
        except Exception:
            pass  # ni Crypto ni Cryptodome : l'import pymitsubishi ci-dessous le dira

# Disponibilité de la couche locale : la lib vendorée exige requests + pycryptodome.
LOCAL_AVAILABLE = False
LOCAL_IMPORT_ERROR = None
try:
    from pymitsubishi import (
        MitsubishiAPI,
        MitsubishiController,
        DriveMode,
        WindSpeed,
        VerticalWindDirection,
        HorizontalWindDirection,
    )
    from pymitsubishi.mitsubishi_parser import RemoteLock
    LOCAL_AVAILABLE = True
except Exception as e:  # ImportError le plus souvent (pycryptodome absent)
    LOCAL_IMPORT_ERROR = str(e)


# --- Mappings valeurs MELCloud <-> protocole local ------------------------------
# Modes : MELCloud utilise 1 Chauffage, 2 Sec, 3 Froid, 7 Ventil, 8 Auto.
# Le protocole local lit AUTO comme 0 (data[9] & 0x07) et l'écrit comme 8.
_MEL_TO_DRIVEMODE = {}
_WS_TO_MEL_FAN = {0: 0, 1: 1, 2: 2, 3: 3, 5: 4, 6: 5}   # WindSpeed.value -> SetFanSpeed
_MEL_FAN_TO_WS = {}
if LOCAL_AVAILABLE:
    _MEL_TO_DRIVEMODE = {1: DriveMode.HEATER, 2: DriveMode.DEHUM, 3: DriveMode.COOLER,
                         7: DriveMode.FAN, 8: DriveMode.AUTO, 0: DriveMode.AUTO}
    _MEL_FAN_TO_WS = {0: WindSpeed.AUTO, 1: WindSpeed.S1, 2: WindSpeed.S2,
                      3: WindSpeed.S3, 4: WindSpeed.S4, 5: WindSpeed.FULL}

_DRIVEMODE_TO_MEL = {"AUTO": 8, "HEATER": 1, "DEHUM": 2, "COOLER": 3, "FAN": 7}


def norm_mac(mac):
    """Normalise une MAC en minuscules avec ':' (accepte '-', octets non paddés)."""
    parts = str(mac).strip().lower().replace("-", ":").split(":")
    if len(parts) == 6:
        return ":".join(p.zfill(2) for p in parts)
    # format sans séparateur (MELCloud renvoie parfois 'aabbccddeeff')
    s = re.sub(r"[^0-9a-f]", "", str(mac).lower())
    if len(s) == 12:
        return ":".join(s[i:i + 2] for i in range(0, 12, 2))
    return str(mac).strip().lower()


def _noop(_msg):
    pass


class LocalLayer:
    """Gère la découverte des IP et le dialogue local avec chaque clim.

    Utilisation par le plugin :
      layer = LocalLayer(log=..., debug=..., error=...)
      layer.set_units([{"mac": ..., "name": ...}, ...])
      layer.set_cached_ips({mac: ip})          # cache persisté (Configuration)
      layer.discovery_step()                    # à appeler au heartbeat si IP manquantes
      st = layer.poll(mac)                      # -> dict champs MELCloud-style ou None
      layer.command(mac, power=True, op_mode=3) # -> bool
      layer.inject_room_temp(mac, 21.5)         # -> bool
    """

    # Après N échecs consécutifs, l'unité est « local down » ; on retente quand
    # même une fois tous les RETRY_EVERY appels de poll (auto-guérison).
    FAIL_THRESHOLD = 3
    RETRY_EVERY = 10

    def __init__(self, log=_noop, debug=_noop, error=_noop):
        self.log = log
        self.debug = debug
        self.error = error
        self.units = {}   # mac -> {"name", "ip", "fail", "skip", "last_ok"}
        self._scan_pool = []      # IPs candidates restantes pour la découverte
        self._scan_round = 0
        self._subnet_hints = []   # sous-réseaux fournis par le plugin (ex. via API Domoticz)

    def set_subnet_hints(self, ips_or_nets):
        """Indices de sous-réseaux LAN (IPs d'autres matériels Domoticz, etc.).
        Indispensable en conteneur Docker bridge : l'interface locale est en
        172.x et ne dit rien du vrai LAN."""
        for item in ips_or_nets or []:
            try:
                net = ipaddress.ip_network(str(item) + "/24", strict=False)
                # is_private est trop laxiste : il accepte 0.0.0.0/8 et 127/8
                # (valeurs "pas d'adresse" fréquentes dans gethardware).
                if (net.is_private
                        and not net.subnet_of(ipaddress.ip_network("0.0.0.0/8"))
                        and not net.subnet_of(ipaddress.ip_network("127.0.0.0/8"))
                        and str(net) not in [str(n) for n in self._subnet_hints]):
                    self._subnet_hints.append(net)
            except ValueError:
                continue
        if self._subnet_hints:
            self.debug("Local: sous-réseaux suggérés: {}".format(
                ", ".join(str(n) for n in self._subnet_hints)))

    # ------------------------------------------------------------------ setup --
    def set_units(self, units):
        """units = liste de dicts avec au moins 'mac' et 'name'."""
        for u in units:
            mac = norm_mac(u["mac"])
            if mac not in self.units:
                self.units[mac] = {"name": u.get("name", mac), "ip": None,
                                   "fail": 0, "skip": 0, "last_ok": 0}

    def set_cached_ips(self, ips):
        """Injecte le cache MAC->IP persisté (vérifié à la 1re utilisation réelle)."""
        for mac, ip in (ips or {}).items():
            mac = norm_mac(mac)
            if mac in self.units and ip:
                self.units[mac]["ip"] = str(ip)
                self.debug("Local: IP cache {} -> {}".format(mac, ip))

    def get_ips(self):
        """Cache MAC->IP courant (à persister via Domoticz.Configuration)."""
        return {mac: u["ip"] for mac, u in self.units.items() if u["ip"]}

    def is_healthy(self, mac):
        u = self.units.get(norm_mac(mac))
        return bool(u and u["ip"] and u["fail"] < self.FAIL_THRESHOLD)

    def status_text(self):
        out = []
        for mac, u in self.units.items():
            state = "OK" if self.is_healthy(mac) else ("down" if u["ip"] else "IP inconnue")
            out.append("{} [{}] ip={} fail={}".format(u["name"], state, u["ip"], u["fail"]))
        return " ; ".join(out) if out else "aucune unité"

    # ------------------------------------------------------------ découverte --
    @staticmethod
    def _read_arp():
        """Table ARP/voisins du système : {mac: ip}. Best-effort (Linux/mac)."""
        table = {}
        try:  # Linux natif ou conteneur host-network
            with open("/proc/net/arp") as f:
                for line in f.readlines()[1:]:
                    cols = line.split()
                    if len(cols) >= 4 and ":" in cols[3]:
                        table[norm_mac(cols[3])] = cols[0]
        except OSError:
            pass
        if not table:
            for cmd in (["ip", "neigh", "show"], ["arp", "-an"]):
                try:
                    out = subprocess.run(cmd, capture_output=True, text=True,
                                         timeout=4).stdout
                    for m in re.finditer(
                            r"(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F]{1,2}(?::[0-9a-fA-F]{1,2}){5})",
                            out):
                        table[norm_mac(m.group(2))] = m.group(1)
                    if table:
                        break
                except (OSError, subprocess.SubprocessError):
                    continue
        return table

    def _candidate_subnets(self):
        """Sous-réseaux /24 plausibles, par ordre de fiabilité : IP connues/en
        cache, indices fournis par le plugin (IPs d'autres matériels Domoticz),
        interface locale, et replis domestiques usuels si on est manifestement
        dans un conteneur (interface en 172.16-31.x : le bridge Docker ne dit
        rien du vrai LAN)."""
        nets = []
        for u in self.units.values():
            if u["ip"]:
                try:
                    nets.append(ipaddress.ip_network(u["ip"] + "/24", strict=False))
                except ValueError:
                    pass
        nets.extend(self._subnet_hints)
        iface_net = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.connect(("8.8.8.8", 80))  # n'émet rien : sert à choisir l'IP source
            ip = s.getsockname()[0]
            s.close()
            iface_net = ipaddress.ip_network(ip + "/24", strict=False)
            if iface_net.is_private:
                nets.append(iface_net)
        except OSError:
            pass
        # Interface dans la plage bridge Docker -> replis LAN domestiques usuels.
        if iface_net is not None and iface_net.subnet_of(ipaddress.ip_network("172.16.0.0/12")):
            for fallback in ("192.168.1.0/24", "192.168.0.0/24"):
                nets.append(ipaddress.ip_network(fallback))
        seen, out = set(), []
        for n in nets:
            if str(n) not in seen:
                seen.add(str(n))
                out.append(n)
        return out

    def _identify(self, ip):
        """Interroge http://ip/smart et renvoie la MAC de la clim, ou None."""
        api = None
        try:
            api = MitsubishiAPI(device_host_port=ip)
            api.api_timeout = (1.5, 3)
            controller = MitsubishiController(api=api)
            state = controller.fetch_status()
            return norm_mac(state.mac) if getattr(state, "mac", None) else None
        except Exception:
            return None
        finally:
            try:
                if api:
                    api.close()
            except Exception:
                pass

    def _adopt(self, mac, ip):
        self.units[mac]["ip"] = ip
        self.units[mac]["fail"] = 0
        self.log("Local: clim {} trouvée en {} (vérifiée par MAC)".format(
            self.units[mac]["name"], ip))

    def discovery_step(self, max_probes=8):
        """Une étape de découverte (appelée au heartbeat tant qu'il manque des IP).

        1) table ARP (gratuit) ; 2) sinon, balayage progressif des /24 candidats :
        test TCP:80 rapide (0.3 s) puis identification /smart des ports ouverts.
        Renvoie True si toutes les unités ont une IP.
        """
        missing = [mac for mac, u in self.units.items() if not u["ip"]]
        if not missing:
            return True

        arp = self._read_arp()
        for mac in list(missing):
            ip = arp.get(mac)
            if ip and self._identify(ip) == mac:
                self._adopt(mac, ip)
                missing.remove(mac)
        if not missing:
            return True

        # Balayage progressif : (re)construit le pool si épuisé.
        if not self._scan_pool:
            self._scan_round += 1
            subnets = self._candidate_subnets()
            for net in subnets:
                self._scan_pool.extend(str(h) for h in net.hosts())
            if not self._scan_pool:
                self.error("Local: impossible de deviner le sous-réseau (conteneur "
                           "isolé ?) — découverte suspendue jusqu'au prochain cycle.")
                return False
            self.log("Local: cycle de scan {} ({} adresses : {})".format(
                self._scan_round, len(self._scan_pool),
                ", ".join(str(n) for n in subnets)))

        taken, opened = 0, []
        while self._scan_pool and taken < max_probes:
            ip = self._scan_pool.pop(0)
            taken += 1
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            try:
                if s.connect_ex((ip, 80)) == 0:
                    opened.append(ip)
            finally:
                s.close()
        for ip in opened:
            mac = self._identify(ip)
            if mac in self.units and not self.units[mac]["ip"]:
                self._adopt(mac, ip)
        return all(u["ip"] for u in self.units.values())

    def revoke_ip(self, mac):
        """Révoque une IP qui ne répond plus (elle sera redécouverte)."""
        mac = norm_mac(mac)
        u = self.units.get(mac)
        if u and u["ip"]:
            self.log("Local: IP {} de {} révoquée (ne répond plus)".format(
                u["ip"], u["name"]))
            u["ip"] = None
            u["fail"] = 0
            self._scan_pool = []  # forcer une reconstruction du pool au prochain passage

    # ------------------------------------------------------------------ accès --
    def _controller(self, ip):
        api = MitsubishiAPI(device_host_port=ip)
        api.api_timeout = (1.5, 3)
        return api, MitsubishiController(api=api)

    def _with_unit(self, mac, action, verify_mac=True):
        """Exécute `action(controller)` sur l'unité, avec gestion des échecs.

        Vérifie l'identité (MAC lue == MAC attendue) au premier fetch. Gère le
        compteur d'échecs + le backoff de retentative. Renvoie le résultat de
        l'action, ou None en cas d'échec/indisponibilité.
        """
        mac = norm_mac(mac)
        u = self.units.get(mac)
        if u is None or not u["ip"]:
            return None
        if u["fail"] >= self.FAIL_THRESHOLD:
            u["skip"] += 1
            if u["skip"] < self.RETRY_EVERY:
                return None  # local down : on ne retente que périodiquement
            u["skip"] = 0
        api = None
        try:
            api, controller = self._controller(u["ip"])
            state = controller.fetch_status()
            got = norm_mac(getattr(state, "mac", "") or "")
            if verify_mac and got and got != mac:
                # L'IP a changé de propriétaire (DHCP) : révoquer, ne rien envoyer.
                self.error("Local: MAC inattendue en {} (attendu {}, lu {}) — IP révoquée".format(
                    u["ip"], mac, got))
                self.revoke_ip(mac)
                return None
            result = action(controller)
            u["fail"] = 0
            u["last_ok"] = time.time()
            return result
        except Exception as e:
            u["fail"] += 1
            self.debug("Local: échec {} ({}/{}) sur {}: {}".format(
                u["name"], u["fail"], self.FAIL_THRESHOLD, u["ip"], e))
            if u["fail"] == self.FAIL_THRESHOLD:
                self.log("Local: {} injoignable en local — bascule cloud (retentatives périodiques)".format(
                    u["name"]))
            return None
        finally:
            try:
                if api:
                    api.close()
            except Exception:
                pass

    # ------------------------------------------------------------------- poll --
    def poll(self, mac):
        """Lit l'état local et le convertit en champs « MELCloud-style ».

        Renvoie un dict {power, op_mode, set_temp, set_fan, vaneH, vaneV,
        room_temp, power_w, energy_wh} ou None si le local est indisponible.
        """
        def _read(controller):
            st = controller.state
            g = st.general
            if g is None:
                return None
            mode_name = g.drive_mode.name if hasattr(g.drive_mode, "name") else None
            op_mode = _DRIVEMODE_TO_MEL.get(mode_name)
            if op_mode is None:
                # valeur brute inattendue -> on la transmet telle quelle
                op_mode = int(getattr(g.drive_mode, "value", g.drive_mode))
            ws = g.wind_speed.value if hasattr(g.wind_speed, "value") else int(g.wind_speed)
            vane_v = g.vertical_wind_direction.value if hasattr(g.vertical_wind_direction, "value") else int(g.vertical_wind_direction)
            vane_h = g.horizontal_wind_direction.value if hasattr(g.horizontal_wind_direction, "value") else int(g.horizontal_wind_direction)
            out = {
                "power": (g.power_on_off.name == "ON") if hasattr(g.power_on_off, "name") else bool(g.power_on_off),
                "op_mode": op_mode,
                "set_temp": float(g.temperature),     # = fine_temperature (PAS coarse)
                "set_fan": _WS_TO_MEL_FAN.get(ws, 0),
                "vaneH": vane_h,
                "vaneV": vane_v,
                "room_temp": None,
                "power_w": None,
                "energy_wh": None,
            }
            sensors = getattr(st, "sensors", None)
            if sensors is not None and sensors.inside_temperature_1_fine is not None:
                out["room_temp"] = float(sensors.inside_temperature_1_fine)
            energy = getattr(st, "energy", None)
            if energy is not None:
                out["power_w"] = int(getattr(energy, "power_watt", 0) or 0)
                hwh = getattr(energy, "energy_hecto_watt_hour", None)
                if hwh is not None:
                    out["energy_wh"] = float(hwh) * 100.0  # hectowatt-heure -> Wh
            return out

        return self._with_unit(mac, _read)

    # --------------------------------------------------------------- commandes --
    def command(self, mac, power=None, op_mode=None, set_temp=None,
                set_fan=None, vaneH=None, vaneV=None):
        """Envoie une commande groupée (changeset) en valeurs MELCloud-style.

        Renvoie True si la commande a été acceptée (la relecture fidèle demande
        ~5 s ; le poll suivant confirmera). None/False si local indisponible.
        """
        def _apply(controller):
            cs = controller.changeset()
            if power is not None:
                from pymitsubishi.mitsubishi_parser import PowerOnOff
                cs.set_power(PowerOnOff.ON if power else PowerOnOff.OFF)
            if op_mode is not None:
                dm = _MEL_TO_DRIVEMODE.get(int(op_mode))
                if dm is not None:
                    cs.set_mode(dm)
            if set_temp is not None:
                cs.set_temperature(float(set_temp))
            if set_fan is not None:
                ws = _MEL_FAN_TO_WS.get(int(set_fan))
                if ws is not None:
                    cs.set_fan_speed(ws)
            if vaneH is not None:
                try:
                    cs.set_horizontal_vane(HorizontalWindDirection(int(vaneH)))
                except ValueError:
                    pass
            if vaneV is not None:
                try:
                    cs.set_vertical_vane(VerticalWindDirection(int(vaneV)))
                except ValueError:
                    pass
            if cs.empty:
                return True
            controller.apply_changeset(cs)
            return True

        return self._with_unit(mac, _apply) is True

    def inject_room_temp(self, mac, temp_celsius):
        """Température distante : la clim régule sur cette valeur (à ré-injecter
        périodiquement). temp_celsius=None => retour au capteur interne."""
        def _inject(controller):
            controller.set_current_temperature(
                None if temp_celsius is None else float(temp_celsius))
            return True

        return self._with_unit(mac, _inject) is True

    def set_remote_lock(self, mac, flags):
        """Verrou télécommande physique. flags = somme RemoteLock (0 déverrouillé,
        1 Power, 2 Mode, 4 Température ; 7 = tout verrouillé)."""
        def _lock(controller):
            controller.set_remote_lock(RemoteLock(int(flags)))
            return True

        return self._with_unit(mac, _lock) is True
