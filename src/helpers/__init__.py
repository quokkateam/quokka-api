import urllib
import sys

if sys.version_info[0] < 3:
  unquote = urllib.unquote
else:
  unquote = urllib.parse.unquote


def decode_url_encoded_str(string):
  return unquote(string)