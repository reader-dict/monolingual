from wikidict import caches

new_data: dict[str, str] = dict([

])
print(len(new_data))
caches.expand_cache_file("svg", new_data)
