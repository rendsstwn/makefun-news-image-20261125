#!/usr/bin/env python3
"""Deliver the 25 November 2026 one-picture news roundup.

The picture this program places at /output/entry.png is the front
page bundled beside it as entry.png: thirty items from Wednesday,
25 November 2026, led by the two tankers mined and set ablaze in
the Strait of Hormuz. Every story it carries was verified to
25 November 2026 before it was drawn:

 1. Strait of Hormuz: two tankers hit naval mines and catch fire.
 2. Houthis claim a strike on Saudi Arabia's Ras Tanura refinery.
 3. Ukraine drones set two Rosneft refineries ablaze overnight.
 4. Kyiv seeks 115bn euros in foreign aid for 2027.
 5. Russian strike kills two in Ukraine's Odesa region.
 6. Two Libyan officers die in a Ukraine-claimed drone attack.
 7. Israel kills Hamas security chief Mohammad Abuelouf in Gaza.
 8. Sudan paramilitary drone strikes kill 19 civilians.
 9. Australia signs a Pacific security treaty with Solomon Islands.
10. Colombia frees all hostages from a Cartagena supermarket siege.
11. Six dead in a flooded gold mine in Bogor, Indonesia.
12. Zimbabwe issues an arrest warrant for Robert Mugabe's son.
13. Bangladesh garment workers win a 36% pay rise.
14. Kilmar Abrego Garcia leaves the US for Spain voluntarily.
15. COP31 climate talks end with no agreement.
16. Asia's chip stocks plunge: KOSPI down 6.2%, Nikkei down 2.8%.
17. The Dow closes above 50,000 for the first time.
18. Nvidia falls 5.9% a day after surging 31.5%.
19. Dell posts a record 54.9bn dollar quarter on AI servers.
20. Eurozone inflation rises to 4.0%.
21. Australian inflation rises to 4.9%.
22. EasyJet profit falls 89% as fuel costs soar.
23. Shenzhou-24 docks with Tiangong, carrying Pakistan's astronaut.
24. Amazon buys chip rival Decart.
25. Hackers' AI agents breach a university server.
26. Anthropic shares fall below their IPO price.
27. Hackers reportedly breach a CIA analysis system.
28. Roche's breast cancer pill wins a second FDA approval.
29. Senegal regain the Africa Cup of Nations title in court.
30. GTA VI debuts at 3.79bn dollars, a record launch.

The program itself does nothing but ferry the bundled picture to
the output slot and check the copy by checksum, so every run
leaves exactly the same bytes behind. Standard library only, no
network, no clock, no randomness.
"""

import os
import shutil
from hashlib import sha256
from pathlib import Path

BUNDLED = "entry.png"
MAGIC = b"\x89PNG\r\n\x1a\n"


def bundled_path():
    """The picture shipped beside this program."""
    return Path(__file__).resolve().parent / BUNDLED


def destination():
    """Where the picture goes: /output, or MAKEFUN_OUTPUT_DIR."""
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(folder) / BUNDLED


def fingerprint(path):
    """SHA-256 hex digest of the file at path."""
    return sha256(path.read_bytes()).hexdigest()


def place():
    """Copy the bundled picture out and verify the copy."""
    src = bundled_path()
    blob = src.read_bytes()
    if blob[:8] != MAGIC:
        raise SystemExit("bundled entry.png is not a PNG file")
    dst = destination()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    if fingerprint(dst) != fingerprint(src):
        raise SystemExit("copied entry.png failed its checksum")
    print("entry.png placed: %d bytes, sha256 %s"
          % (dst.stat().st_size, fingerprint(dst)))


if __name__ == "__main__":
    place()
