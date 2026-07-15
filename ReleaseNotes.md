# Release Notes — domoticz-python-melcloud

***🇬🇧 English** · [🇫🇷 Français](ReleaseNotes.fr.md)*

## v2.1.0 — 2026 (Bastien1307, Claude)

**French UI**
- Devices and selectors created at startup are **translated to French** when the
  `Language` parameter is set to French; every other language stays in English.
  Covers device names (Mode, Fan, Setpoint, horizontal/vertical Vane, Room Temp,
  Unit Infos, Remote lock, Consumption, Outdoor group) and selector labels
  (modes, fan speeds, vane swing, lock levels).
- The **configuration form** stays in English: its labels are frozen by Domoticz
  before the plugin runs and cannot be translated.
- No effect on an existing install (Domoticz never renames an existing device)
  nor on the internal logic (dispatch by unit number).

## v2.0.0 — 2026-07-11 (Bastien1307, Claude)

**LOCAL control first, MELCloud as fallback** — architecture change: the plugin
is no longer a MELCloud client, it is a LAN driver that keeps the cloud as a
safety net. Based on a campaign of real-world tests against MAC-577IF-2E
adapters (HTTP, port 80).

- **Local layer** (`melcloud_local.py` + the [pymitsubishi](https://github.com/pymitsubishi/pymitsubishi)
  0.5.2 library, vendored in `pymitsubishi/`): real-time state reads and commands
  (power, mode, setpoint, fan, vanes) straight over the LAN.
- **Two independent poll rates**: `Refresh interval wifi (local)` (10 s to
  5 min, or Off) and `Refresh interval web (cloud)` (fallback).
- **Zero-config network discovery**: IPs resolved by MAC (ARP table, then a
  progressive LAN scan; subnets inferred from the IPs of the other Domoticz
  hardware via the local API → works inside a **bridged Docker container** too).
  **Identity is always verified against the MAC** returned by the unit before
  anything is sent; an IP is revoked and rediscovered if DHCP reassigns it.
- **Persisted cache** (`Domoticz.Configuration`): units + IPs → **startup and
  operation are 100 % local, with no internet**.
- **Automatic failover**: 3 consecutive local failures → polling and commands go
  through the cloud, with periodic local retries (self-healing). The
  anti-flapping guards now apply to the cloud path only (local data is reliable
  → direct writes, no debounce).
- `requirements.txt` (`pycryptodome`, `requests`) + `customstart.sh` wiring for
  Docker installs. Without pycryptodome: clean cloud-only mode with an explicit
  message.
- The internet-witness device (Mode4) now only suspends the cloud path.

**Remote temperature**
- `Remote temp` parameter (`mac=idx,mac=idx`): each unit regulates on a
  **Domoticz room thermometer**, re-injected on every local poll. Empty = the
  built-in sensor (historical behaviour).
- The injected value is rounded to a **0.5° step** depending on the mode: UP in
  cool/dry, DOWN in heat, nearest otherwise (the unit ignores tenths; the
  conservative rounding avoids stopping too early). Exact multiples of 0.5 are
  left untouched.

**Power**
- **Real instantaneous power (W)** in the kWh counters (the cloud always
  reported 0 W) + per-outdoor-group sum.

**Remote-control lock** — new per-unit selector (Unlocked / Power / Mode /
Temperature / All), a local-only feature the cloud does not expose.
- **On plugin shutdown**: active locks are **physically released** (without
  touching the Domoticz selectors) — nobody is left stuck with a dead remote in
  hand if Domoticz is switched off.
- **On startup**: if a selector says "locked", the lock is **re-applied** as soon
  as the unit answers locally.

**Icons & interface**
- Icons resolved **by name** — no hard-coded icon IDs left. Missing base → the
  bundled `icons/<Base>.zip` is loaded automatically; base already in the
  database (historical manual upload) → linked as-is, **with no duplicate**.
  Falls back to a standard icon if the zip is absent.
- 26 icon zips bundled in `icons/` (finding: Domoticz only reads ONE icon per
  plugin zip — a multi-icon zip keeps just the last line of icons.txt).
- **Floor-console vs wall-split detection by model** (`MFZ*` = console) for the
  vertical vane icons — replaces a hard-coded room name.
- The `if Level == …: image = …` chains in `onCommand` replaced by map lookups
  (single source of truth).
- `_update_if_changed` now compares the icon too: a device whose value is stable
  still receives its new icon after an ID change.

**Misc**
- Repetitive logs cleaned up (local poll is silent outside Debug). README
  rewritten, plus these release notes.

## v1.1.0 — 2026 (Bastien1307, ChatGPT) — on top of schurgan v1.0.0

Fixes and major additions relative to the upstream repository
(https://github.com/schurgan/domoticz-python-melcloud):

- **Setpoint = a real Thermostat** (Type 242/SetPoint, 0.5° precision) instead of
  the original Selector Switch with 1° steps (`16|17|…|31`) — finer control and a
  fitting UI.
- **End of the On/Off flapping**: frame validation (rejecting physically
  impossible "zeroed-out" cloud snapshots) + debounce on the Mode selector
  (confirmation over 2 reads) + dirty-check on device writes.
- **End of the SIGABRT crashes**: a single connection point with a
  no-parallel guard, idempotent `onConnect`, type guards on every response,
  duplicate units purged.
- **Energy counters (kWh)** per unit (Unit 100+) and per **outdoor group**
  (Unit 150+, multi-split sum), refreshed periodically via ListDevices.
- **GMT Offset field removed**: automatic UTC→local conversion (`astimezone`,
  DST handled).
- Optional **internet-witness device** (Mode4) through the local JSON API.
- **API backoff** on repeated HTTP errors (500/429).

## v0.1 → v1.0.0 (gysmo38, schurgan, Dalonsic, ChatGPT)

History of the original cloud plugin: see the header of `plugin.py` and
https://github.com/schurgan/domoticz-python-melcloud.
