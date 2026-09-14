import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

CDN = "https://cdn.jsdelivr.net/gh/Aiello-Digital/dratereza-original-clone@main"

# Rewrite local WP asset URLs to jsDelivr CDN (mirrored copy), keep every other
# external URL (Google Fonts, GTM, GA, Maps, etc.) untouched.
before_count = html.count("https://www.dratereza.com.br/wp-content/") + html.count("https://www.dratereza.com.br/wp-includes/")
html = html.replace("https://www.dratereza.com.br/wp-content/", CDN + "/wp-content/")
html = html.replace("https://www.dratereza.com.br/wp-includes/", CDN + "/wp-includes/")
print(f"Rewrote {before_count} local asset URL occurrences to jsDelivr CDN")

# Bug fix patch: the Enfold "tab section" widget (avia_sc_tab_section) has a
# known height-calculation bug where .av-tab-section-inner-container ends up
# with a height far taller than the visible tab (a large blank gap below the
# "Em cada momento um cuidado especial" section), which "fixes itself" once
# the theme's own recalculation runs (e.g. after a tab click). This patch
# forces the correct height proactively/continuously for a few seconds after
# load and after each tab click, without touching the original theme files.
patch_script = """
<script id="tab-height-bugfix">
(function () {
  function fixTabSection(root) {
    if (!root || root.offsetParent === null) return; // hidden (e.g. mobile fallback variant)
    var inner = root.querySelector('.av-tab-section-inner-container');
    var titles = root.querySelectorAll('.av-tab-section-tab-title-container .av-section-tab-title');
    var sections = root.querySelectorAll(':scope > .av-tab-section-outer-container .av_tab_section, .av_tab_section');
    if (!inner || !titles.length || !sections.length) return;
    var idx = 0;
    for (var i = 0; i < titles.length; i++) {
      if (titles[i].classList.contains('av-active-tab-title')) { idx = i; break; }
    }
    var active = sections[idx];
    if (!active) return;
    var contentInner = active.querySelector('.av-layout-tab-inner') || active;
    var h = contentInner.scrollHeight;
    if (h > 0 && Math.abs(parseInt(inner.style.height, 10) - h) > 2) {
      inner.style.height = h + 'px';
    }
  }
  function fixAll() {
    document.querySelectorAll('.av-tab-section-container').forEach(fixTabSection);
  }

  document.addEventListener('DOMContentLoaded', fixAll);
  window.addEventListener('load', function () {
    var tries = 0;
    var iv = setInterval(function () {
      fixAll();
      tries++;
      if (tries > 16) clearInterval(iv); // keep correcting for ~8s while lazy content/images settle
    }, 500);
  });
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.av-section-tab-title')) {
      setTimeout(fixAll, 50);
      setTimeout(fixAll, 700);
    }
  });
})();
</script>
"""

if "</body>" in html:
    html = html.replace("</body>", patch_script + "\n</body>", 1)
else:
    html += patch_script

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Patched index.html written")
