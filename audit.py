import re, os, urllib.request, urllib.parse

BASE = "https://www.dratereza.com.br"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/120.0 Safari/605.1.15"
OUT = os.path.dirname(os.path.abspath(__file__))

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def is_asset_url(u):
    return ("/wp-content/" in u or "/wp-includes/" in u) and not u.endswith(".php")

# 1. Fetch a FRESH copy of the live original page (untouched, not our patched one)
raw_html = fetch(BASE + "/").decode("utf-8", errors="replace")
print("Fetched fresh original HTML:", len(raw_html), "bytes")

# 2. Extract every reference to a local wp-content/wp-includes asset from the
#    ENTIRE raw HTML - attributes AND any url(...) inside inline <style> blocks
#    or inline style="" attributes. This is broader than the original mirror
#    script, which only looked at href/src/data-src/srcset attributes.
found = set()

attr_pattern = re.compile(r'''(?:href|src|data-src|data-lazy-src|data-bg-image)=["\']([^"\']+)["\']''')
for m in attr_pattern.finditer(raw_html):
    found.add(m.group(1))

srcset_pattern = re.compile(r'''srcset=["\']([^"\']+)["\']''')
for m in srcset_pattern.finditer(raw_html):
    for p in m.group(1).split(","):
        u = p.strip().split(" ")[0]
        if u:
            found.add(u)

url_in_css_pattern = re.compile(r'''url\(\s*['"]?([^'")]+)['"]?\s*\)''')
for m in url_in_css_pattern.finditer(raw_html):
    found.add(m.group(1))

# normalize
abs_urls = set()
for u in found:
    if u.startswith("data:"):
        continue
    if u.startswith("//"):
        u = "https:" + u
    if u.startswith(BASE):
        abs_urls.add(u.split("#")[0])
    elif u.startswith("/") and not u.startswith("//"):
        abs_urls.add((BASE + u).split("#")[0])

asset_urls = sorted(u for u in abs_urls if is_asset_url(u))
print(f"Found {len(asset_urls)} local asset URL references in raw HTML (incl. inline <style>)")

# 3. Also scan every already-downloaded local CSS file for url(...) refs
#    (covers nested references e.g. avia-merged-styles.css -> other assets)
css_files = []
for root, dirs, files in os.walk(OUT):
    for fn in files:
        if fn.endswith(".css"):
            css_files.append(os.path.join(root, fn))

for css_path in css_files:
    try:
        with open(css_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception:
        continue
    # figure out the URL this file was originally fetched from, to resolve relative refs
    rel = os.path.relpath(css_path, OUT)
    origin_url = BASE + "/" + rel.replace(os.sep, "/")
    for m in url_in_css_pattern.finditer(content):
        ref = m.group(1)
        if ref.startswith("data:"):
            continue
        resolved = urllib.parse.urljoin(origin_url, ref)
        if resolved.startswith("//"):
            resolved = "https:" + resolved
        resolved = resolved.split("#")[0]
        if resolved.startswith(BASE) and is_asset_url(resolved):
            asset_urls.append(resolved)

asset_urls = sorted(set(asset_urls))
print(f"Total unique candidate asset URLs (HTML + all local CSS files): {len(asset_urls)}")

# 4. Compare against what's already on disk locally
missing = []
present = []
for u in asset_urls:
    parsed = urllib.parse.urlparse(u)
    local_path = os.path.join(OUT, parsed.path.lstrip("/"))
    if os.path.isfile(local_path):
        present.append(u)
    else:
        missing.append(u)

print(f"Already present locally: {len(present)}")
print(f"MISSING locally: {len(missing)}")
for u in missing:
    print("  MISSING:", u)

# 5. Download everything missing
downloaded = 0
failed = []
for u in missing:
    try:
        content = fetch(u)
        parsed = urllib.parse.urlparse(u)
        local_path = os.path.join(OUT, parsed.path.lstrip("/"))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(content)
        downloaded += 1
    except Exception as e:
        failed.append((u, str(e)))

print(f"\nDownloaded {downloaded} missing files, {len(failed)} failed")
for u, e in failed:
    print("  FAILED:", u, e)
