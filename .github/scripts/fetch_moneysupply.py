#!/usr/bin/env python3
"""Fetch Global Broad Money ("Big 4": US, Eurozone, Japan, China) from FRED's keyless CSV export
(fredgraph.csv - no API key needed, same URL FRED's own "Download Data" button uses) and write
data/moneysupply/latest.json for the mvrv-dashboard Money Supply chart.

Each country's aggregate is converted to USD billions so the four are directly comparable/summable.
Three things about this can't be verified from outside a real network (this script only runs where
FRED is actually reachable, i.e. inside the GitHub Actions runner):

1. Exact FRED series IDs, and whether they're still being updated. Confirmed empirically (a first
   real run of this script, 2026-08-22): the IMF-sourced M2 series this script originally used for
   Eurozone/Japan/China ("MYAGM2<CC>M189*") are all discontinued (last rows 2017/2017/2019) - only
   the US M2 series (M2SL) is genuinely still live. Each non-US country therefore lists more than one
   CANDIDATE series (see COUNTRIES below), tried in order - the OECD-sourced M3 ("Broad Money",
   "*M657S") candidates are the ones actually expected to be live going forward, with the original
   IMF M2 ID kept as a last-resort fallback. Using M3 instead of M2 for those countries is a
   disclosed, deliberate substitution (see the frontend's methodology section), not a silent one -
   this script records which measure/series actually got used per country in the output.
2. The value's unit multiplier (millions vs. billions of national currency) isn't in the CSV
   itself, only in FRED's page metadata, which this script deliberately does not depend on.
3. Whether a candidate that looks right by (1) and (2) is actually still being updated at all.

All three are handled empirically rather than assumed: every candidate is fetched, checked for
staleness (newest row not too old), and checked against a rough real-world plausibility band
(EXPECTED_USD_BN, generous: 0.35x-3x) trying both a "values are already billions" and a "values are
millions" reading - the first candidate that passes every check wins. A country where no candidate
passes is skipped for this run (previous data in latest.json stays as-is) - never written with
stale or implausible numbers. The aggregate ("big4") sums whichever countries currently have data
(minimum 2, see MIN_COUNTRIES_FOR_AGGREGATE) rather than requiring all four, so it isn't held
hostage by whichever single country's data source happens to be broken this week.
"""
import csv
import io
import json
import sys
import datetime
import urllib.request
import urllib.error

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
UA = "Mozilla/5.0 (compatible; altcoin-dashboard-moneysupply-fetch/1.0; +https://github.com/hofmiker/altcoin-dashboard)"
OUT_PATH = "data/moneysupply/latest.json"

# Each country lists candidate series in priority order - {id, measure, fx, fx_dir}. "fx"/"fx_dir"
# apply to that candidate's OWN currency conversion (all candidates for one country share the same
# national currency, so in practice these repeat, but keeping them per-candidate costs nothing and
# stays correct if that ever isn't true). expected_usd_bn is a rough current order-of-magnitude used
# only for the empirical unit-scale sanity check described in the module docstring - not written out.
COUNTRIES = {
    "US": {
        "label": "USA", "expected_usd_bn": 21500,
        "candidates": [
            {"id": "M2SL", "measure": "M2", "fx": None, "fx_dir": None},
        ],
    },
    "EZ": {
        "label": "Eurozone", "expected_usd_bn": 16000,
        "candidates": [
            {"id": "MABMM301EZM657S", "measure": "M3", "fx": "DEXUSEU", "fx_dir": "mul"},
            {"id": "MYAGM2EZM196N", "measure": "M2", "fx": "DEXUSEU", "fx_dir": "mul"},
        ],
    },
    "JP": {
        "label": "Japan", "expected_usd_bn": 7500,
        "candidates": [
            {"id": "MABMM301JPM657S", "measure": "M3", "fx": "DEXJPUS", "fx_dir": "div"},
            {"id": "MYAGM2JPM189S", "measure": "M2", "fx": "DEXJPUS", "fx_dir": "div"},
        ],
    },
    "CN": {
        "label": "China", "expected_usd_bn": 42000,
        "candidates": [
            {"id": "MABMM301CNQ657S", "measure": "M3", "fx": "DEXCHUS", "fx_dir": "div"},
            {"id": "MYAGM2CNM189N", "measure": "M2", "fx": "DEXCHUS", "fx_dir": "div"},
        ],
    },
}
MAX_AGE_DAYS = 400            # a series whose newest row is older than this is treated as dead/discontinued
MIN_ROWS = 24                  # need at least ~2 years of rows to be worth showing
PLAUSIBLE_LO, PLAUSIBLE_HI = 0.35, 3.0   # multiplicative band around expected_usd_bn
FORWARD_FILL_MONTHS = 6         # how long a country's monthly value may be carried forward to fill the aggregate
MIN_COUNTRIES_FOR_AGGREGATE = 2  # "Big 4" only means something once at least this many actually have data


def log(msg):
    print(msg, file=sys.stderr)


def fetch_csv_series(series_id):
    url = FRED_CSV_URL.format(series_id)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/csv"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        text = resp.read().decode("utf-8", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) < 2:
        raise RuntimeError("empty CSV")
    out = []
    for r in rows[1:]:
        if len(r) < 2:
            continue
        date_s, raw = r[0].strip(), r[1].strip()
        if not date_s or raw in (".", ""):
            continue
        try:
            val = float(raw)
        except ValueError:
            continue
        try:
            datetime.date.fromisoformat(date_s)
        except ValueError:
            continue
        out.append((date_s, val))
    out.sort(key=lambda x: x[0])
    if len(out) < MIN_ROWS:
        raise RuntimeError(f"only {len(out)} usable rows (need >= {MIN_ROWS})")
    newest = datetime.date.fromisoformat(out[-1][0])
    if (datetime.date.today() - newest).days > MAX_AGE_DAYS:
        raise RuntimeError(f"newest row ({out[-1][0]}) is stale (series likely discontinued)")
    return out


def fx_rate_for(fx_series, target_date):
    """Most recent FX rate on or before target_date; falls back to the nearest rate after it
    (within the series) if target_date predates the whole FX series."""
    target = datetime.date.fromisoformat(target_date)
    best = None
    for d, v in fx_series:
        dd = datetime.date.fromisoformat(d)
        if dd <= target and (best is None or dd > datetime.date.fromisoformat(best[0])):
            best = (d, v)
    if best:
        return best[1]
    after = [(d, v) for d, v in fx_series if datetime.date.fromisoformat(d) > target]
    return after[0][1] if after else None


def convert_series_to_usd_bn(raw_series, fx_series, fx_dir, expected_usd_bn):
    """Returns (converted [(date, usd_bn)], scale_used) or (None, None) if no reading is plausible."""
    def raw_usd(val, date_s):
        if fx_series is None:
            return val
        fx = fx_rate_for(fx_series, date_s)
        if fx is None or fx == 0:
            return None
        return val * fx if fx_dir == "mul" else val / fx

    latest_date, latest_val = raw_series[-1]
    latest_raw = raw_usd(latest_val, latest_date)
    if latest_raw is None:
        return None, None

    for scale, name in ((1.0, "billions"), (0.001, "millions")):
        candidate_bn = latest_raw * scale
        if PLAUSIBLE_LO * expected_usd_bn <= candidate_bn <= PLAUSIBLE_HI * expected_usd_bn:
            converted = []
            for d, v in raw_series:
                ru = raw_usd(v, d)
                if ru is None:
                    continue
                converted.append((d, round(ru * scale, 3)))
            return converted, name
    log(f"      unit sanity check failed: latest={latest_raw:.1f} (raw) is implausible for "
        f"expected~{expected_usd_bn} in either billions or millions reading")
    return None, None


def month_key(date_s):
    return date_s[:7]


def to_month_series(series):
    """One value per calendar month (last observation of that month wins), sorted ascending."""
    by_month = {}
    for d, v in series:
        by_month[month_key(d)] = v
    return dict(sorted(by_month.items()))


def build_big4(country_month_series):
    """Forward-fills each country up to FORWARD_FILL_MONTHS to smooth out differing reporting
    lags, then sums whichever countries have a (real or filled) value that month - not all four,
    so one broken/lagging country doesn't blank out the whole aggregate (see
    MIN_COUNTRIES_FOR_AGGREGATE for the floor on how few is still meaningful)."""
    all_months = sorted({m for s in country_month_series.values() for m in s})
    filled = {cc: {} for cc in country_month_series}
    for cc, series in country_month_series.items():
        last_val, last_idx = None, -999
        for i, m in enumerate(all_months):
            if m in series:
                last_val, last_idx = series[m], i
            if last_val is not None and (i - last_idx) <= FORWARD_FILL_MONTHS:
                filled[cc][m] = last_val
    big4 = []
    for m in all_months:
        have = [cc for cc in filled if m in filled[cc]]
        if len(have) >= MIN_COUNTRIES_FOR_AGGREGATE:
            total = sum(filled[cc][m] for cc in have)
            big4.append({"date": m + "-01", "valueUsdBn": round(total, 3), "countries": sorted(have)})
    return big4


def fetch_country(cc, cfg, fx_cache):
    for cand in cfg["candidates"]:
        log(f"Fetching {cc} ({cfg['label']}): {cand['measure']} series {cand['id']}" +
            (f", FX series {cand['fx']}" if cand["fx"] else " (already USD)"))
        try:
            raw_series = fetch_csv_series(cand["id"])
        except Exception as e:
            log(f"    candidate {cand['id']} failed: {e}")
            continue
        fx_series = None
        if cand["fx"]:
            if cand["fx"] not in fx_cache:
                try:
                    fx_cache[cand["fx"]] = fetch_csv_series(cand["fx"])
                except Exception as e:
                    log(f"    FX fetch ({cand['fx']}) failed: {e}")
                    fx_cache[cand["fx"]] = None
            fx_series = fx_cache[cand["fx"]]
            if fx_series is None:
                continue
        converted, scale_used = convert_series_to_usd_bn(raw_series, fx_series, cand["fx_dir"], cfg["expected_usd_bn"])
        if converted is None:
            continue
        log(f"  OK {cc}: {cand['measure']} {cand['id']}, {len(converted)} rows, latest {converted[-1][0]} = "
            f"{converted[-1][1]:.0f} USD Bn (source values read as {scale_used})")
        return {
            "label": cfg["label"],
            "measure": cand["measure"],
            "seriesId": cand["id"],
            "fxSeriesId": cand["fx"],
            "unit": "USD Bn",
            "data": [{"date": d, "value": v} for d, v in converted],
        }
    log(f"  SKIP {cc}: no candidate series passed (fetch/freshness/plausibility)")
    return None


def main():
    countries_out = {}
    fx_cache = {}
    for cc, cfg in COUNTRIES.items():
        result = fetch_country(cc, cfg, fx_cache)
        if result:
            countries_out[cc] = result

    if not countries_out:
        log("No country succeeded at all - aborting without writing anything.")
        sys.exit(1)

    month_series = {cc: to_month_series([(row["date"], row["value"]) for row in c["data"]])
                     for cc, c in countries_out.items()}
    big4 = build_big4(month_series) if len(countries_out) >= MIN_COUNTRIES_FOR_AGGREGATE else []
    if len(countries_out) < MIN_COUNTRIES_FOR_AGGREGATE:
        log(f"Only {len(countries_out)} countr{'y' if len(countries_out)==1 else 'ies'} succeeded - "
            f"need >= {MIN_COUNTRIES_FOR_AGGREGATE} for a meaningful aggregate, leaving Big4 empty this run "
            f"(individual country lines are still written).")

    fetched_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    as_of = max(c["data"][-1]["date"] for c in countries_out.values())
    out = {
        "fetchedAt": fetched_at,
        "source": "FRED (fredgraph.csv, keyless CSV export)",
        "asOf": as_of,
        "countries": countries_out,
        "big4": big4,
    }

    import os
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"as_of={as_of}")
    print(f"countries_ok={','.join(sorted(countries_out))}")
    print(f"big4_rows={len(big4)}")


if __name__ == "__main__":
    main()
