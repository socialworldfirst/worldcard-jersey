#!/usr/bin/env python3
"""Reuse the old rotating platform-logo belt (beltscroll) from index-jun22.html.
Place it directly under the hero, above Why World Card, on all 3 market pages.
Remove the old static .tools row. Self-contained logo PNGs (../assets/logos/)."""
import re, os

OLD = "/Users/steven/Documents/Claude/wf_argentina_sg/index-jun22.html"
src = open(OLD).read()

# 1. extract belt CSS  (from the '/* colourful app-icon belt */' marker to just before the next comment)
m = re.search(r'(/\* colourful app-icon belt \*/.*?)\n\s*/\* promo', src, re.S)
belt_css = m.group(1).strip()

# 2. extract belt HTML section
belt_html = re.search(r'<section class="belt">.*?</section>', src, re.S).group(0)

# 3. point logo PNGs at the new project's own copies (relative from /sg /my /id)
belt_html = belt_html.replace(
    "https://socialworldfirst.github.io/worldfirst-argentina-sg/assets/logos/",
    "../assets/logos/")

belt_block = "  <!-- WORKS WITH TOOLS (belt, moved up under hero) -->\n  " + belt_html + "\n"

for mk in ["sg", "my", "id"]:
    p = f"{mk}/index.html"
    h = open(p).read()
    # a) remove the old static tools section
    h = re.sub(r'\s*<!-- WORKS WITH TOOLS -->\s*<section class="tools wrap">.*?</section>', '', h, flags=re.S)
    # b) add belt CSS before </style>
    if belt_css not in h:
        h = h.replace('</style>', '\n  ' + belt_css + '\n</style>', 1)
    # c) insert belt right before the Why World Card section (i.e. straight after hero)
    h = re.sub(r'(\n  <!-- WHY WORLD CARD)', '\n' + belt_block + r'\1', h, count=1)
    open(p, "w").write(h)
    print(f"[{mk}] belt_css={'yes' if '.beltscroll' in h or 'beltscroll' in h else 'NO'} "
          f"belt_section={'yes' if '<section class=\"belt\">' in h else 'NO'} "
          f"old_tools_removed={'yes' if 'class=\"tools wrap\"' not in h else 'NO'} "
          f"logos_relative={h.count('../assets/logos/')}")
print("done")
