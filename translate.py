try:
    import httplib  # Python 2
except ImportError:
    import http.client as httplib  # Python 3
try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3
import json
import random
import hashlib
from flask_babel import gettext
from config import MS_TRANSLATOR_CLIENT_ID, MS_TRANSLATOR_CLIENT_SECRET

def baidu_translate(text, sourceLang, destLang):
    if MS_TRANSLATOR_CLIENT_ID == "" or MS_TRANSLATOR_CLIENT_SECRET == "":
        return gettext('Error: translation service not configured.')
    httpClient = None
    myurl = '/api/trans/vip/translate'

    salt = random.randint(32768, 65536)
    sign = MS_TRANSLATOR_CLIENT_ID + text + str(salt) + MS_TRANSLATOR_CLIENT_SECRET
    sign = hashlib.md5(sign.encode()).hexdigest()
    if 1:# try:
        # get access token
        myurl = myurl + '?appid=' + MS_TRANSLATOR_CLIENT_ID + '&q=' + quote(text) \
            + '&from=' + sourceLang + '&to=' + destLang + '&salt=' + str(salt) + '&sign=' + sign

        conn = httplib.HTTPSConnection("api.fanyi.baidu.com")
        conn.request('GET', myurl)
        response = json.loads(conn.getresponse().read())
        return response
    if 0:# except:
        return gettext('Error: Unexpected error.')