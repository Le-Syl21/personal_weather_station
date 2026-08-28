# Changelog

## 1.1.0

**Upgrading is safe: no entity is renamed or removed on its own.** The two
changes that would move things are offered in
**Settings → System → Repairs** and only happen if you accept them. Ignore them
to keep everything exactly as it is.

### Fixed

- **A parameter sent with an empty value no longer breaks the whole request.**
  Both protocols send a key with no value when the matching sensor has nothing
  to report — the WSLink API document does it in its own upload example, for
  `t1feels` and `t1heat`. Those raised inside the update loop, which aborted the
  request, lost every parameter that came after them and answered HTTP 500. An
  empty value now simply leaves its sensor `unknown`.
- A single unusable parameter is logged and skipped instead of costing you the
  others; the response reports how many were skipped.
- A request without a station identifier now answers **HTTP 400**. It answered
  200 while the log claimed otherwise.
- A payload arriving while an entity was still being added no longer raises.
- The integration no longer forces its logger to `DEBUG`, which overrode the
  `logger:` configuration.
- The HTTP endpoints are registered once per Home Assistant run instead of
  stacking a new route on every reload.
- The station key is compared with `hmac.compare_digest`, and `PASSWORD` /
  `wspw` are matched case-insensitively like every other parameter.
- Repairs for a rejected request are keyed on the station identifier rather than
  the source address. Behind a proxy such as the WSLink add-on every station
  shares one address, so a station getting through cleared the warning raised for
  another one.
- Replaced the `CONCENTRATION_*` constants deprecated for removal in Home
  Assistant 2027.8. Same values, so nothing changes for existing statistics.

### Added

- **North calibration.** Once a station reports a wind direction, its device page
  gains a `Wind direction offset` number and two buttons,
  *Set north from current* and *Reset wind offset*. Hold the vane at geographic
  north, press, done. A `Wind direction (raw)` diagnostic keeps the uncorrected
  reading so a calibration can be checked or redone. The offset is stored in the
  config entry, not as a restored state, so a recorder purge cannot lose it.
- **Entities and values survive a restart.** They are rebuilt from the registries
  at startup instead of waiting for the station's next upload.
- **A silent station is marked unavailable** instead of showing a frozen reading
  forever. The delay is configurable in the options (15 minutes by default, `0`
  to disable).
- **A `Last update` diagnostic** per station, which stays readable precisely when
  the station has gone quiet. It uses the payload timestamp (`dateutc` or
  `datetime`) when the station clock looks trustworthy.
- **A setup flow that says what to do next.** The integration has no "add device"
  button — the station creates its own device when it posts — so adding it now
  ends on the exact settings to enter, including this instance's address. Until a
  station has posted, a repair brings those instructions back and waits with you
  for the first upload, telling you what to check if nothing arrives. The same
  instructions stay reachable from the integration's own settings, for whenever a
  second station is added.
- **Rejected requests are reported in Repairs**, with the source IP address. A
  wrong station key used to be invisible unless debug logging was on, while
  being the most likely reason for a station never showing up. Rejections are
  also logged at `WARNING` now.
- **A station can be deleted** from its device page. It comes back if it posts
  again.
- **Translations in all 64 languages Home Assistant supports**, sensor names
  included. Eight are reviewed (`de`, `en-GB`, `es`, `es-419`, `fr`, `it`, `pt`,
  `pt-BR`); the rest are complete but await proofreading — corrections welcome,
  see [CONTRIBUTING.md](CONTRIBUTING.md).
- A test suite driving a real Home Assistant instance, run in CI.
- The WSLink walkthrough in the readme is now illustrated, and says the two
  things that were missing: the URL takes no `http://`, and **Confirm & Exit** is
  what actually writes the settings to the station.

### Changed

- **Requires Home Assistant 2025.3.0 or later**, now declared. Earlier releases
  already needed it without saying so.
- Declared as a single-instance integration: one endpoint, one station key, any
  number of stations posting to it.
- Saving the options form no longer reloads the integration, and no longer wipes
  the per-station wind calibration.
- **New stations get shorter entity IDs.** Up to 1.0.8 the station name appeared
  twice, as in `sensor.my_station_my_station_outdoor_temperature`. Stations
  already known to Home Assistant keep their IDs, including for sensors that
  appear later, so one station never mixes two naming styles. Entity IDs stay in
  English whatever your language, so a dashboard survives being shared.
- **New stations expose water leak and connection readings as binary sensors**,
  reading *Wet* / *Dry* and *Connected* / *Disconnected* instead of `1` / `0`.
  Battery levels deliberately stay percentages, which is what the low-battery
  alerts and long-term statistics work on.

### Known fix during development

- The onboarding repair used to close as *successfully repaired* when the wait
  ran out without a station showing up, and disappeared — while its own text
  promised it would stay. Home Assistant deletes a repair for any fix flow
  ending that is not an abort.

### Optional migrations

Both appear in **Settings → System → Repairs** and can be ignored.

| Migration | What it does | What it costs |
|---|---|---|
| Shorten entity IDs | Renames `sensor.x_x_outdoor_temperature` to `sensor.x_outdoor_temperature` | History and long-term statistics follow the rename. **Automations, scripts, scenes and dashboards do not** — update them yourself. |
| Convert status readings | Turns the 27 connection and leak sensors into binary sensors | Changing platform is not a rename: the old entities are removed and rebuilt. **Their raw history is lost** (these readings have no long-term statistics), and anything pointing at them must be updated. |
