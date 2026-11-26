# Sanctions Ledger

Keep a dated record of Canada’s consolidated sanctions entries. Inspect listed identities, regulatory references and changes between captures.

Open https://coolcode.ca/sanctionsledger/

<!-- coolcode:guide -->
Open an entry to inspect its identity fields and linked regulation. The diary reports additions, absences and changed source entries between captures. An absence from the consolidated XML is not by itself proof of legal delisting.
<!-- /coolcode:guide -->

The opening comparison uses two saved captures of the same regime, schedule and item. It shows the values of one changed source field and the capture dates. When the latest capture has no suitable comparison, a dated source entry appears instead.

## Sources and interpretation

Global Affairs Canada’s consolidated XML is a reference list and has no force of law. The controlling regulations may change before the consolidated source is updated. Follow the linked regulation for legal interpretation.

Entries are matched by regime, schedule and item number. Country-Pays is a regime label, not always a geographic country. Identity-field changes within the same slot are labelled source changes rather than assumed legal corrections.

The first capture is a baseline, not thousands of new sanctions. Source listing date, source update date and our capture date have different meanings. Later absence from the file does not itself establish a legal delisting.

## Collection and archive

Schedule: **Daily** (`11 10 * * *`, UTC). GitHub schedules are best effort. Scheduled and manual runs collect, validate, commit dated snapshots and deploy. A first code push also collects if no saved dataset exists. Other code pushes rebuild the saved dataset offline.

`data/current.json` contains the latest normalized source records and metadata. `archive/YYYY-MM/*.json.gz` retains distinct captured versions; `data/history.json` lists them. Identical data checks update the check time without manufacturing a change. An initial capture is labelled baseline. Archive data is tracked in Git and does not expire with Actions artifacts. The site has snapshot selection, filtering, source detail, CSV export and an RSS change feed.

The default build needs no network. Failed source validation does not replace the published dataset. Optional `HEALTHCHECKS_PING_URL` sends start/success/failure pings for collection runs; no accuracy email is implied.

```sh
python3 -m pip install -r requirements.txt
python3 scripts/collect.py
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

## Privacy

Search and filters are local to the browser; no upstream request is made by filtering. Public data collection runs in GitHub Actions. The shared CoolCode counter records aggregate page opens, without searches or filter values. The explorer and collector run without Cloudflare changes. To enable shared visit counts and private issue reports, add `sanctionsledger` to the existing `coolcode-visitor-api` Worker’s `toolList` and deploy it, if not already registered. See the [batch setup notes](https://github.com/jsdyer/jsdyer.github.io/blob/main/docs/tier1-tools.md).

## Software and attribution

Application code is MIT licensed; upstream data retains its original licence and attribution. Follow the source links for original records and terms.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
