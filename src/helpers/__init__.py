import urllib
import sys
import random

if sys.version_info[0] < 3:
  unquote = urllib.unquote
  quote = urllib.quote
else:
  unquote = urllib.parse.unquote
  quote = urllib.parse.quote


def decode_url_encoded_str(string):
  return unquote(string)


def url_encode_str(string):
  return quote(string)


def random_subset(iterator, K):
  result = []
  N = 0

  for item in iterator:
    N += 1
    if len(result) < K:
      result.append(item)
    else:
      s = int(random.random() * N)
      if s < K:
        result[s] = item

  return result