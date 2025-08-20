from wikidict import places_cache, svg_cache


for module in [places_cache, svg_cache]:
    with open(getattr(module, "__file__"), mode="w") as fh:
        fh.write("CACHE = {\n")
        for k, v in sorted(set(module.CACHE.items())):
            fh.write(f"    {k!r}: {v!r},\n")
        fh.write("}\n")
