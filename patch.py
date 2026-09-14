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

# ---------------------------------------------------------------------------
# Bug fix: "Em cada momento um cuidado especial" (Enfold av_tab_section widget)
# leaves a large blank gap below it on first load, which goes away the moment
# a tab is clicked.
#
# Root cause (confirmed by live inspection of the real, unpatched page):
#   - `.av-tab-section-inner-container` computes as `display:table` and each
#     of the 5 slide panels (`[data-av-tab-section-content]`) as
#     `display:table-cell`. Outside of an actual <table>/<tr> structure this
#     makes the browser generate one anonymous table row PER cell instead of
#     one shared row, so the 5 panels stack instead of sitting side by side,
#     and each panel is squeezed to ~100px wide.
#   - Enfold's own JS (`avia_sc_tab_section`) measures each panel's
#     `.av-layout-tab-inner` height while it's in that squeezed, wrapped
#     state and bakes the (wrong, much taller) result into an inline
#     `height:...px` on `.av-layout-tab-inner`. That inflated height is what
#     shows up as blank space below the visible slide.
#   - Clicking a tab re-runs that same measurement function, but by then the
#     click handler forces a correct `display:table-cell` reflow first, so it
#     (accidentally) computes and stores the right height instead - which is
#     exactly why the gap "goes away" the moment you pick any option.
#
# Fix: force the intended side-by-side layout (block + float, 100vw each,
# matching the `translate3d(-N * 100%, 0, 0)` slide logic already used by the
# theme) instead of the broken table layout, and clear the bad inline height
# Enfold's own script stamped onto each panel so the browser sizes them from
# their real content once fonts/images have settled. Nothing else about the
# page is touched.
# ---------------------------------------------------------------------------
patch_script = """
<style id="tab-height-bugfix-css">
.av-tab-section-container.av-tab-slide-transition .av-tab-section-inner-container {
  display: block !important;
}
.av-tab-section-container.av-tab-slide-transition .av-tab-section-inner-container [data-av-tab-section-content] {
  display: block !important;
  float: left !important;
  width: 100vw !important;
}
</style>
<script id="tab-height-bugfix">
(function () {
  function clearBadHeights() {
    document.querySelectorAll('.av-tab-section-container [data-av-tab-section-content] .av-layout-tab-inner').forEach(function (el) {
      el.style.height = '';
    });
  }
  function run() {
    clearBadHeights();
    // Enfold's own script also recalculates on load/resize; keep re-clearing
    // for a few seconds so it can't leave a stale height behind while fonts
    // and lazy-loaded images are still settling.
    var tries = 0;
    var iv = setInterval(function () {
      clearBadHeights();
      tries++;
      if (tries > 10) clearInterval(iv);
    }, 400);
  }
  if (document.readyState === 'complete') run();
  else window.addEventListener('load', run);
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
