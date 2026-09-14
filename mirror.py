import re, os, sys, urllib.request, urllib.parse

BASE = "https://www.dratereza.com.br"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/120.0 Safari/605.1.15"
OUT = os.path.dirname(os.path.abspath(__file__))

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def save_to_path(url, content):
    # map url path (relative to domain) to local file path
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lstrip("/")
    if path == "":
        path = "index.html"
    local = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(local), exist_ok=True)
    with open(local, "wb") as f:
        f.write(content)
    return local

def is_asset_url(u):
    return ("/wp-content/" in u or "/wp-includes/" in u) and not u.endswith(".php")

# 1. fetch homepage
html_bytes = fetch(BASE + "/")
html = html_bytes.decode("utf-8", errors="replace")
with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("Saved index.html", len(html), "bytes")

# 2. extract asset URLs from HTML (href, src, data-src, srcset)
url_pattern = re.compile(r'''(?:href|src|data-src|data-lazy-src)=["\']([^"\']+)["\']''')
srcset_pattern = re.compile(r'''srcset=["\']([^"\']+)["\']''')
urls = set()
for m in url_pattern.finditer(html):
    urls.add(m.group(1))
for m in srcset_pattern.finditer(html):
    parts = m.group(1).split(",")
    for p in parts:
        u = p.strip().split(" ")[0]
        if u:
            urls.add(u)

# normalize to absolute dratereza URLs
abs_urls = set()
for u in urls:
    if u.startswith("//"):
        u = "https:" + u
    if u.startswith(BASE):
        abs_urls.add(u)
    elif u.startswith("/") and not u.startswith("//"):
        abs_urls.add(BASE + u)

asset_urls = sorted(u for u in abs_urls if is_asset_url(u))
print(f"Found {len(asset_urls)} candidate asset URLs from HTML")

downloaded = {}
css_files = []
failed = []

def download(u):
    if u in downloaded:
        return downloaded[u]
    try:
        content = fetch(u)
        local = save_to_path(u, content)
        downloaded[u] = local
        return local
    except Exception as e:
        failed.append((u, str(e)))
        return None

for u in asset_urls:
    local = download(u)
    if local and local.endswith(".css"):
        css_files.append((u, local))

print(f"Downloaded {len(downloaded)} assets, {len(failed)} failed")

# 3. parse CSS files for additional url(...) references (fonts, bg images)
css_url_pattern = re.compile(r'''url\(\s*['"]?([^'")]+)['"]?\s*\)''')
more_urls = set()
for css_url, local_path in css_files:
    try:
        with open(local_path, "r", encoding="utf-8", errors="replace") as f:
            css_content = f.read()
    except Exception:
        continue
    for m in css_url_pattern.finditer(css_content):
        ref = m.group(1)
        if ref.startswith("data:"):
            continue
        # resolve relative to the css file's own URL
        resolved = urllib.parse.urljoin(css_url, ref)
        if resolved.startswith("//"):
            resolved = "https:" + resolved
        if resolved.startswith(BASE):
            more_urls.add(resolved.split("#")[0])

more_urls = sorted(u for u in more_urls if is_asset_url(u) and u not in downloaded)
print(f"Found {len(more_urls)} additional asset URLs from CSS")
for u in more_urls:
    download(u)

print(f"TOTAL downloaded: {len(downloaded)}, failed: {len(failed)}")
if failed:
    for u, e in failed[:20]:
        print("FAILED:", u, e)

with open(os.path.join(OUT, "_downloaded_manifest.txt"), "w") as f:
    for u, local in sorted(downloaded.items()):
        f.write(f"{u}\t{os.path.relpath(local, OUT)}\n")
