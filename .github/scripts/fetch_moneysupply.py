#!/usr/bin/env python3
"""Fetch Global M2 ("Big 4": US, Eurozone, Japan, China) from FRED's keyless CSV export
(fredgraph.csv - no API key needed, same URL FRED's own "Download Data" button uses) and
write data/moneysupply/latest.json for the mvrv-dashboard Money Supply chart.

Each country's M2 is converted to USD billions so the four are directly comparable/summable.
Two things about this conversion can't be verified from outside a real network (this script
only runs where FRED is actually reachable, i.e. inside the GitHub Actions runner):

1. Exact FRED series IDs. M2SL (US) is well-established. The IMF-sourced "MYAGM2<CC>M189*"
   IDs used for EZ/JP/CN are less certain - some countries' series under that naming pattern
   are discontinued, with an unconfirmed different ID actually carrying live data instead.
2. The value's unit multiplier (millions vs. billions of national currency) isn't in the CSV
   itself, only in FRED's page metadata, which this script deliberately does not depend on.

Both are handled empirically rather than assumed: each country's converted value is checked
against a rough real-world plausibility band (EXPECTED_USD_BN, generous: 0.35x-3x), trying
both a "values are already billions" and a "values are millions" reading and keeping whichever
one lands in-band. A country whose fetch fails outright or whose result lands in neither
reading's band is skipped for this run (previous data in latest.json stays as-is, the
dashboard keeps showing the last good snapshot) - never written with implausible numbers.
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

# seriesId of the M2 aggregate + (optional) FX series converting its national currency to USD,
# and a rough expected order-of-magnitude (USD billions, current-ish) used only for the unit
# sanity check described in the module docstring above - not written to the output.
COUNTRIES = {
    "US": {"label": "USA",        "m2": "M2SL",           "fx": None,      "fx_dir": None, "expected_usd_bn": 21500},
    "EZ": {"label": "Eurozone",   "m2": "MYAGM2EZM196N",  "fx": "DEXUSEU", "fx_dir": "mul", "expected_usd_bn": 16000},
    "JP": {"label": "Japan",      "m2": "MYAGM2JPM189S",  "fx": "DEXJPUS", "fx_dir": "div", "expected_usd_bn": 7500},
    "CN": {"label": "China",      "m2": "MYAGM2CNM189N",  "fx": "DEXCHUS", "fx_dir": "div", "expected_usd_bn": 42000},
}
MAX_AGE_DAYS = 400          # a series whose newest row is older than this is treated as dead/discontinued
MIN_ROWS = 24                # need at least ~2 years of monthly rows to be worth showing
PLAUSIBLE_LO, PLAUSIBLE_HI = 0.35, 3.0   # multiplicative band around expected_usd_bn
FORWARD_FILL_MONTHS = 6       # how long a country's monthly value may be carried forward to fill the aggregate


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


def convert_series_to_usd_bn(m2_series, fx_series, fx_dir, expected_usd_bn):
    """Returns (converted [(date, usd_bn)], scale_used) or (None, None) if no reading is plausible."""
    def raw_usd(m2_val, m2_date):
        if fx_series is None:
            return m2_val
        fx = fx_rate_for(fx_series, m2_date)
        if fx is None or fx == 0:
            return None
        return m2_val * fx if fx_dir == "mul" else m2_val / fx

    latest_date, latest_m2 = m2_series[-1]
    latest_raw = raw_usd(latest_m2, latest_date)
    if latest_raw is None:
        return None, None

    for scale, name in ((1.0, "billions"), (0.001, "millions")):
        candidate_bn = latest_raw * scale
        if PLAUSIBLE_LO * expected_usd_bn <= candidate_bn <= PLAUSIBLE_HI * expected_usd_bn:
            converted = []
            for d, v in m2_series:
                ru = raw_usd(v, d)
                if ru is None:
                    continue
                converted.append((d, round(ru * scale, 3)))
            return converted, name
    log(f"    unit sanity check failed: latest={latest_raw:.1f} (raw) is implausible for "
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
    lags, then sums only the months where all four countries have a (real or filled) value."""
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
        if all(m in filled[cc] for cc in filled):
            total = sum(filled[cc][m] for cc in filled)
            big4.append({"date": m + "-01", "valueUsdBn": round(total, 3)})
    return big4


def main():
    countries_out = {}
    fx_cache = {}
    for cc, cfg in COUNTRIES.items():
        log(f"Fetching {cc} ({cfg['label']}): M2 series {cfg['m2']}" +
            (f", FX series {cfg['fx']}" if cfg["fx"] else " (already USD)"))
        try:
            m2_series = fetch_csv_series(cfg["m2"])
        except Exception as e:
            log(f"  SKIP {cc}: M2 fetch failed: {e}")
            continue
        fx_series = None
        if cfg["fx"]:
            if cfg["fx"] not in fx_cache:
                try:
                    fx_cache[cfg["fx"]] = fetch_csv_series(cfg["fx"])
                except Exception as e:
                    log(f"  SKIP {cc}: FX fetch ({cfg['fx']}) failed: {e}")
                    fx_cache[cfg["fx"]] = None
            fx_series = fx_cache[cfg["fx"]]
            if fx_series is None:
                continue
        converted, scale_used = convert_series_to_usd_bn(m2_series, fx_series, cfg["fx_dir"], cfg["expected_usd_bn"])
        if converted is None:
            log(f"  SKIP {cc}: no plausible USD conversion found")
            continue
        log(f"  OK {cc}: {len(converted)} rows, latest {converted[-1][0]} = {converted[-1][1]:.0f} USD Bn "
            f"(source values read as {scale_used})")
        countries_out[cc] = {
            "label": cfg["label"],
            "m2SeriesId": cfg["m2"],
            "fxSeriesId": cfg["fx"],
            "unit": "USD Bn",
            "data": [{"date": d, "value": v} for d, v in converted],
        }

    if not countries_out:
        log("No country succeeded at all - aborting without writing anything.")
        sys.exit(1)

    month_series = {cc: to_month_series([(row["date"], row["value"]) for row in c["data"]])
                     for cc, c in countries_out.items()}
    big4 = build_big4(month_series) if len(countries_out) == 4 else []
    if len(countries_out) < 4:
        log(f"Only {len(countries_out)}/4 countries succeeded - Big4 aggregate needs all four, "
            f"leaving it empty this run (individual country lines are still written).")

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
