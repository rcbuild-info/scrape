from scrapy.dupefilters import RFPDupeFilter
from scrapy.utils.request import request_fingerprint

import hashlib
import urlparse

class Dupefilter (RFPDupeFilter):
  def request_fingerprint(self, request):
    # Order matters to lizard-rc.se.
    if urlparse.urlparse(request.url).netloc == "lizard-rc.se":
      fp = hashlib.sha1()
      fp.update(request.method)
      fp.update(request.url)
      fp.update(request.body or b'')
      return fp.hexdigest()
    return request_fingerprint(request)
