import re

RE_SUP = re.compile(r"(&nbsp;<sup>.+</sup>)")
adapters = {
    "Šablonas:t+": lambda body: RE_SUP.sub("", body, count=2),
}
