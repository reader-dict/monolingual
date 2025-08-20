import sys

from wikidict import caches

kind = sys.argv[1]
key = sys.argv[2]
value = sys.argv[3]
caches.expand_cache_file(kind, {key: value})
