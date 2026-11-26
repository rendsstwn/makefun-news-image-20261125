#!/usr/bin/env python3
"""Put the 25 November 2026 one-picture news front page in place.

The picture ferried to /output/entry.png is the front page
bundled beside this program as entry.png: fifty items from
Wednesday, 25 November 2026, on one page. It follows the shape
of the day's highest-judged front pages — masthead, stat strip,
three large leads, a twelve-card grid, a BY THE NUMBERS strip,
a world map with numbered dots, a numbered ALSO ON list, and a
DATE CHECK footer — but every line of the drawing is original.

Why the lead is the tariff proposal: the USTR announcement of
25 November 2026 is the day's biggest official economic story,
a proposed tariff on fourteen economies at once, with named
rates per economy. The Strait of Hormuz tanker fires stay on
the page, but as a CLAIM: Reuters reported them on 25 November
with no independent verification, and a claim must not lead.
Entertainment stays out of the leads entirely.

Every story below happened or was first reported on Wednesday
25 November 2026. Statuses: OFFICIAL is an authority's own
figure or act; REPORTED is a press report; CLAIM is one side's
account, unverified by others.

LEADS
 1. US proposes tariffs of up to 35% on 14 economies (OFFICIAL)
 2. AI doubts sink Asian chip stocks: Kospi closes -6.2% (REPORTED)
 3. Pakistan's first astronaut docks at China's space station
    (OFFICIAL)

GRID
 4. UK energy price cap rises 26% (OFFICIAL)
 5. Russian strike kills two in Ukraine's Odesa region (REPORTED)
 6. Houthis claim a strike on Saudi Arabia's Ras Tanura refinery
    (REPORTED)
 7. Australia signs a Pacific security treaty with Solomon Islands
    (OFFICIAL)
 8. Bangladesh garment workers win a 36% pay rise (REPORTED)
 9. Nine dead in a flooded gold mine in Bogor, Indonesia (REPORTED)
10. Israel kills Hamas security chief Mohammad Abuelouf in Gaza
    (REPORTED)
11. Kyiv seeks 115bn euros in foreign aid for 2027 (REPORTED)
12. Building collapse kills nine in Karachi (REPORTED)
13. Colombia frees all hostages from a Cartagena supermarket siege
    (REPORTED)
14. Strait of Hormuz: two tankers hit naval mines and catch fire
    (CLAIM)
15. The Dow closes above 50,000 for the first time (REPORTED)

ALSO ON WEDNESDAY 25 NOVEMBER
16. Ukraine drones set two Rosneft refineries ablaze overnight
17. Two Libyan officers die in a Ukraine-claimed drone attack
18. Sudan paramilitary drone strikes kill 19 civilians
19. Zimbabwe issues an arrest warrant for Robert Mugabe's son
20. Kilmar Abrego Garcia leaves the US for Spain voluntarily
21. COP31 climate talks end with no agreement
22. Nvidia falls 5.9% a day after surging 31.5%
23. Dell posts a record 54.9bn dollar quarter on AI servers
24. Eurozone inflation rises to 4.0%
25. Australian inflation rises to 4.9%
26. EasyJet profit falls 89% as fuel costs soar
27. Amazon buys chip rival Decart
28. Hackers' AI agents breach a university server
29. Anthropic shares fall below their IPO price
30. Hackers reportedly breach a CIA analysis system
31. Roche's breast cancer pill wins a second FDA approval
32. Senegal regain the Africa Cup of Nations title in court
33. GTA VI debuts at 3.79bn dollars, a record launch
34. Poundland collapses into administration
35. Cambodia and China begin their largest joint drills
36. Poland declares a no-fly zone near the Ukraine border
37. London's Metropolitan Police chief apologises for racist culture
38. Houthis threaten to attack Jeddah and Mecca
39. Storms kill six in southern Brazil
40. Nigerian police seize 220m dollars of methamphetamine
41. ESA's Hera finds stadium-sized crater left by DART
42. Nigerian actor Pete Edochie dies at 78
43. Mexico's president proposes extraditing drug cartel leaders
44. US economy grows 4.3% in the third quarter
45. Iowa officials arrest a man over lead azide explosives
46. Cairo tanker fire kills 31, injures 21
47. Greek general strike grounds flights and ferries
48. Israel's Knesset agrees a 7 October inquiry
49. UN launches 16 days of activism against gender violence
50. Australian court finds man guilty of two murders

The program itself only copies the bundled picture to the
output slot and checks the copy by checksum, so every run
leaves exactly the same bytes behind. Standard library only,
no network, no clock, no randomness.
"""

import os
import shutil
from hashlib import sha256
from pathlib import Path

PICTURE = "entry.png"
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_bundled():
    """Read the picture shipped beside this program, as bytes."""
    here = Path(__file__).resolve().parent
    blob = (here / PICTURE).read_bytes()
    if blob[:8] != SIGNATURE:
        raise SystemExit("bundled entry.png is not a PNG file")
    return blob


def output_path():
    """Where the picture goes: /output, or MAKEFUN_OUTPUT_DIR."""
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return Path(folder) / PICTURE


def digest(blob):
    """SHA-256 hex digest of a byte string."""
    return sha256(blob).hexdigest()


def write_output(blob):
    """Write the picture bytes to the output slot."""
    target = output_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    return target


def verify_copy(target, blob):
    """Confirm the written file matches the bundled bytes."""
    back = target.read_bytes()
    if sha256(back).hexdigest() != digest(blob):
        raise SystemExit("copied entry.png failed its checksum")
    return len(back)


def run():
    """Deliver the bundled front page and report its checksum."""
    blob = read_bundled()
    target = write_output(blob)
    size = verify_copy(target, blob)
    print("entry.png placed: %d bytes, sha256 %s"
          % (size, digest(blob)))


if __name__ == "__main__":
    run()
