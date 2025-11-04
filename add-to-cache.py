from wikidict import caches

# Regexp for search & replace:
# `- \[ \] \d+-\d+-\d+ \d+:\d+:\d+ WARNING:wikidict\.svg:\d+ \[new SVG\] `
new_data: dict[str, str] = dict([

])
print(len(new_data))
caches.expand_cache_file("svg", new_data)
