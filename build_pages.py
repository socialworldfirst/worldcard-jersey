#!/usr/bin/env python3
"""Generate per-market landing pages (SG / MY / ID) from the MY-layout base.
Base (_base.html) = cashback+jersey v2 (education up, jersey rules down), MY offer (1%, no boost).
SG gets the premium offer (1.2% uncapped + 5.2% new-customer boost). MY/ID share the base offer.
No country name appears in copy (kept generic). Market is identified by URL only.
"""
import re, os

base = open("_base.html").read()
rules_base = open("_rules.html").read() if os.path.exists("_rules.html") else ""

REGION_SWITCH = '''      <div class="regionswitch">
        <div class="globe" id="globeBtn"><img src="assets/globe.webp" alt="Choose region"></div>
        <div class="regionmenu" id="regionMenu">
          <div class="rhead">Choose your market</div>
          <button data-region-tab="sg">Singapore</button>
          <button data-region-tab="sea">Southeast Asia</button>
        </div>
      </div>
'''

BOOST = '''  <!-- NEW CUSTOMER BOOST -->
  <section class="boost wrap">
    <div class="boostcard">
      <div class="beye">New customer</div>
      <div class="bbig">5.2% cashback</div>
      <div class="blab">on your first US$3,000 of spend</div>
      <p>A limited-period boost for new WorldFirst customers.</p>
    </div>
  </section>

'''

MARKETS = {
  "sg": {"threshold": "US$10,000", "portal": "https://portal.worldfirst.com/worldcard?lang=en-GB&region=SG", "premium": True},
  "my": {"threshold": "US$1,000",  "portal": "https://portal.worldfirst.com/worldcard?lang=en-GB&region=MY", "premium": False},
  "id": {"threshold": "US$1,000",  "portal": "https://portal.worldfirst.com/worldcard?lang=en-GB&region=ID", "premium": False},
}

def common(h):
    # 1. remove region switcher + region JS (each page is standalone, values baked)
    h = h.replace(REGION_SWITCH, "")
    h = re.sub(r'<script>.*?</script>', '', h, flags=re.S)
    # 2. subfolder asset paths
    h = h.replace('src="assets/', 'src="../assets/').replace('href="assets/', 'href="../assets/')
    h = h.replace("url('assets/", "url('../assets/").replace('url("assets/', 'url("../assets/')
    # 3. drop country names from copy -> generic
    h = h.replace('<span class="tbd" data-rv="market">Singapore</span>', 'participating markets')
    return h

def build(mk, cfg):
    h = common(base)
    # bake threshold + card portal (JS removed)
    h = h.replace("US$10,000", cfg["threshold"])
    h = h.replace('card-link" href="#"', 'card-link" href="%s"' % cfg["portal"])
    if cfg["premium"]:  # SG offer
        h = h.replace("Earn 1% cashback on your business spend",
                      "Earn 1.2% cashback on your business spend")
        h = h.replace(
          '<h3><span class="rose">1% cashback</span> on card spend</h3><p>Earn up to 1% back on your monthly business card purchases.</p>',
          '<h3><span class="rose">1.2% cashback</span>, uncapped</h3><p>Earn up to 1.2% back on eligible business spend every month, no cap.</p>')
        h = h.replace("  <!-- HOW TO ENTER -->", BOOST + "  <!-- HOW TO ENTER -->")
    os.makedirs(mk, exist_ok=True)
    open(os.path.join(mk, "index.html"), "w").write(h)
    # rules page per market (threshold baked, generic market, subfolder assets)
    if rules_base:
        r = rules_base
        r = r.replace('src="assets/', 'src="../assets/').replace('href="assets/', 'href="../assets/')
        r = r.replace("url('assets/", "url('../assets/").replace('url("assets/', 'url("../assets/')
        r = r.replace('<span class="tbd" data-rv="market">Singapore</span>', 'participating markets')
        r = re.sub(r'<script>.*?</script>', '', r, flags=re.S)
        r = r.replace("US$10,000", cfg["threshold"])
        open(os.path.join(mk, "rules.html"), "w").write(r)
    # report
    print(f"[{mk}] cashback={'1.2%+boost' if cfg['premium'] else '1%'} threshold={cfg['threshold']} "
          f"boost={'yes' if cfg['premium'] else 'no'} switcher_removed={REGION_SWITCH not in h} "
          f"malaysia={'FOUND' if 'malaysia' in h.lower() else 'none'} singapore={'FOUND' if '>Singapore<' in h else 'none'}")

for mk, cfg in MARKETS.items():
    build(mk, cfg)

# root: neutral redirect to sg (ads link straight to /sg /my /id anyway)
open("index.html", "w").write(
  '<!doctype html><meta name="robots" content="noindex">'
  '<meta http-equiv="refresh" content="0; url=./sg/">'
  '<title>WorldFirst</title><a href="./sg/">Continue</a>')

# cleanup base files so they are not served
for f in ["_base.html", "_rules.html"]:
    if os.path.exists(f): os.remove(f)
print("done")
