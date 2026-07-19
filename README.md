# domoticz-python-melcloud

***🇬🇧 English** · [🇫🇷 Français](README.fr.md)*

Domoticz plugin for **Mitsubishi Electric** air conditioners — **LOCAL control
first** (MAC-577IF-2E Wi-Fi adapter, HTTP over the LAN), with **MELCloud as a
fallback**.

> **Fork.** This repository starts from [schurgan/domoticz-python-melcloud](https://github.com/schurgan/domoticz-python-melcloud)
> (v1.0.0), itself a fork of [gysmo38/domoticz-python-melcloud](https://github.com/gysmo38/domoticz-python-melcloud),
> the original cloud-only plugin. As of **v2.0.0** the plugin drives the units
> **directly over the LAN** and only falls back to the cloud when it has to:
> this is an architecture change, not a variant. No upstream merge is planned.

## Features

- **Real-time local control** (poll from 10 s to 5 min): power, mode, setpoint,
  fan speed, vanes — no cloud round-trip, near-zero latency, and it keeps
  working **without an internet connection** (units + IP cache is persisted).
- **Automatic MELCloud fallback**: if a unit stops answering on the LAN, it is
  polled and commanded through the cloud until it recovers.
- **Remote temperature**: each unit can regulate on a Domoticz room thermometer
  (`mac=idx` parameter) instead of its built-in sensor — re-injected on every
  poll, rounded to the nearest 0.5° step (up in cool/dry, down in heat).
- **Real instantaneous power (W)** plus cumulative energy (kWh), per unit and
  per outdoor group (multi-split sum).
- **Remote-control lock** (per-unit selector, local only): Unlocked / Power /
  Mode / Temperature / All.
- **Zero-config network discovery**: IPs resolved by MAC (ARP table + LAN scan,
  subnets inferred from the other Domoticz hardware — works inside a bridged
  Docker container too). Identity is **always verified by MAC** before any
  command is sent; an IP is revoked and rediscovered if DHCP reassigns it.
- **Bundled icons** (`icons/*.zip`): installed and linked by name at startup —
  nothing to upload by hand.
- Floor-console (`MFZ*` models) vs wall-split detection, so vane icons match the
  actual hardware.

## Installation

1. Clone the repository into your Domoticz `plugins/` folder:
   ```
   cd domoticz/plugins
   git clone https://github.com/Bastien1307/domoticz-python-melcloud.git
   ```
   (If you already run another MELCloud plugin, remove or rename its folder
   first — two plugins with the same key cannot coexist.)
2. Install the Python dependencies (see below).
3. Restart Domoticz.
4. In *Setup → Settings → System*, enable **Accept new Hardware Devices**.
5. In *Setup → Hardware*, add a new hardware of type **MELCloud plugin**, fill in
   your MELCloud email and password, and leave the other parameters on their
   defaults for a first run.
6. The devices are created automatically after the first successful login. Local
   control starts as soon as the units are discovered on the LAN (watch the log).

### Upgrading

```
cd domoticz/plugins/domoticz-python-melcloud
git pull
```
then restart Domoticz.

### Hardware requirements

The local layer talks to the **MAC-577IF-2E** Wi-Fi adapter (the standard
Mitsubishi Electric interface fitted to many MSZ units) over plain HTTP on the
LAN. **No hardware modification is needed** — it is the same adapter MELCloud
uses, simply addressed locally instead of through the cloud.

Other adapters (MAC-567IF-E, MAC-587IF-E…) are untested: the plugin should still
work through the cloud path, and will fall back to it automatically if local
control does not answer.

### Dependencies (requirements.txt)

The local layer needs `requests` and `pycryptodome` inside **Domoticz's own
Python** (not a side venv). Without them the plugin still runs cloud-only and
says so clearly in the log.

- **Standard install**:
  ```
  sudo pip3 install -r plugins/domoticz-python-melcloud/requirements.txt
  ```
- **Raspberry Pi / recent Debian**: pip refuses with
  `error: externally-managed-environment` (PEP 668). Install the packages
  through apt instead — this is the clean way on a Pi:
  ```
  sudo apt install python3-pycryptodome python3-requests
  ```
  (`pycryptodome` is the one that matters; `requests` is usually already there.)
  If you'd rather keep pip, add `--break-system-packages` to the pip command
  above. The plugin accepts **either** namespace — `Crypto` (pip's pycryptodome)
  or `Cryptodome` (Debian's `python3-pycryptodome`, which renames it) — so both
  install methods work. To check it's visible to Python:
  `python3 -c "import Crypto" 2>/dev/null && echo Crypto || python3 -c "import Cryptodome" && echo Cryptodome`.
- **Domoticz in Docker** — two options:
  - quick: `docker exec <container> pip3 install -r /opt/domoticz/userdata/plugins/domoticz-python-melcloud/requirements.txt`
    (must be redone if the container is recreated);
  - durable: wire `requirements.txt` into the container start script
    (`userdata/customstart.sh`: cache the wheels, install on first boot — same
    mechanism as the Domoticz-Zigbee plugin).

## Parameters

| Field | Purpose |
|---|---|
| Email / Password | MELCloud account (used for the initial startup and the cloud fallback) |
| Refresh interval wifi (local) | local poll rate (default 30 s; `Off` = cloud only) |
| Refresh interval web (cloud) | fallback cloud poll rate (5 min recommended) |
| Remote temp | optional: `mac=idx,mac=idx` — Domoticz thermometer per unit (remote temperature) |
| Language / Debug | MELCloud language / log level |
| ID device Internet | optional: Domoticz device reflecting internet connectivity (only suspends the cloud path) |

## Devices created (per unit)

Mode, Fan, Temp (setpoint), Vane Horizontal, Vane Vertical, Room Temp, Unit
Infos, plus kWh counters (per unit and per outdoor group, with real watts), plus
the Remote-control lock (not "used" by default).

## Support

This plugin builds on an existing one, but it has been **substantially
reworked** — it is not a copy-paste with a library bolted on:

- **Deep debugging of the cloud plugin**: no more SIGABRT crashes (concurrent
  connections, non-idempotent `onConnect`), no more On/Off flapping (zeroed-out
  cloud frames, Mode debounce), API backoff.
- **Rework of the existing code**: the setpoint is now a **real Thermostat**
  (0.5°) where the plugin had always used a Selector Switch with 1° steps;
  energy counters per unit and per outdoor group; GMT Offset replaced by
  automatic DST conversion.
- **Local control added end to end** (v2.0.0): LAN control, IP discovery by MAC,
  offline cache, automatic cloud fallback, remote temperature, real watts,
  remote-control lock, bundled icons. It builds on the pymitsubishi library, but
  the whole Domoticz integration, the network discovery and the
  local-first/fallback logic were written here.

If the plugin is useful to you, you can buy me a coffee:

**[☕ paypal.me/sebastienRanc](https://paypal.me/sebastienRanc)**

> Please pick the **"Friends and family"** option (rather than "goods and
> services") so the donation arrives without fees.

Spare a thought for the authors this work stands on:
[gysmo38](https://github.com/gysmo38/domoticz-python-melcloud) and
[schurgan](https://github.com/schurgan/domoticz-python-melcloud) (original cloud
plugin), and [pymitsubishi](https://github.com/pymitsubishi/pymitsubishi) (local
protocol).

## Credits & versions

Full detail in [ReleaseNotes.md](ReleaseNotes.md).

- **v0.x → v1.0.0 (base)**: gysmo38, schurgan, Dalonsic, ChatGPT — original
  MELCloud cloud plugin (https://github.com/schurgan/domoticz-python-melcloud).
- **v1.1.0**: [Bastien1307](https://github.com/Bastien1307), ChatGPT —
  anti-flapping, anti-crash, kWh counters, automatic DST, API backoff.
- **v2.0.0**: [Bastien1307](https://github.com/Bastien1307), Claude — local
  layer (local-first / cloud-fallback), remote temperature, real watts,
  remote-control lock, bundled icons, network discovery, offline cache.
- Local layer based on the [pymitsubishi](https://github.com/pymitsubishi/pymitsubishi)
  library (MIT, vendored in `pymitsubishi/`).
