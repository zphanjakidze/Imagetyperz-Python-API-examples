# Imagetyperz captcha API
# -----------------------
# requests lib
try:
    from requests import session
except:
    raise Exception('requests package not installed, try with: \'pip2.7 install requests\'')

import os, ntpath
from base64 import b64encode

# endpoints
# -------------------------------------------------------------------------------------------
CAPTCHA_ENDPOINT = 'http://captchatypers.com/Forms/UploadFileAndGetTextNEW.ashx'
RECAPTCHA_SUBMIT_ENDPOINT = 'http://captchatypers.com/captchaapi/UploadRecaptchaV1.ashx'
RECAPTCHA_RETRIEVE_ENDPOINT = 'http://captchatypers.com/captchaapi/GetRecaptchaText.ashx'
BALANCE_ENDPOINT = 'http://captchatypers.com/Forms/RequestBalance.ashx'
BAD_IMAGE_ENDPOINT = 'http://captchatypers.com/Forms/SetBadImage.ashx'

# user agent used in requests
# ---------------------------
USER_AGENT = 'pythonAPI1.0'

# Captcha class
# -------------------------------
class Captcha:
    def __init__(self, response):
        self._captcha_id = ''
        self._text = ''

        self.parse_response(response)

    # parse response from API, into id and text
    def parse_response(self, response):
        s = response.split('|')
        # we have a captcha only with ID and response
        if len(s) < 2:
            raise Exception('cannot parse response from server: {}'.format(response))

        # normally, would split by 2, but if captcha itself contains | will mess it
        self._captcha_id = s[0]
        self._text = '|'.join(s[1:])      # save text

    @property
    def text(self):
        return self._text

    @property
    def captcha_id(self):
        return self._captcha_id

# Recaptcha class
# ---------------------------------
class Recaptcha:
    def __init__(self, captcha_id):
        self._captcha_id = captcha_id
        self._response = ''

    # set response
    def set_response(self, response):
        self._response = response

    @property
    def captcha_id(self):
        return self._captcha_id

    @property
    def response(self):
        return self._response


# API class
# -----------------------------------------
class ImageTypersAPI:
    def __init__(self, username, password, timeout = 120, ref_id = 0):
        self._username = username
        self._password = password

        self._ref_id = '{}'.format(ref_id)      # save as str
        self._timeout = timeout
        self._session = session()       # init a new session

        self._normal_captcha = None            # save last solved captcha
        self._recaptcha = None

        self._error = None              # keep track of last error

        self._headers = {               # use this user agent
            'User-Agent' : USER_AGENT
        }

    # solve normal captcha
    def solve_captcha(self, image_path, case_sensitive = False):
        # check if image/file exists
        if not os.path.exists(image_path): raise Exception('captcha image does not exist: {}'.format(image_path))

        # read image/captcha
        with open(image_path, 'rb') as f:
            image_data = b64encode(f.read())

        data = {}
		# init dict params  (request params)
        data['action'] = 'UPLOADCAPTCHA'
        data['username'] = self._username
        data['password'] = self._password
        data['chkCase'] = '1' if case_sensitive else '0'
        data['file'] = image_data
        # update with refid
        data['refid'] = self._ref_id

        # make request with all data
        response = self._session.post(CAPTCHA_ENDPOINT, data=data,
                                      headers=self._headers, 
                                      timeout=self._timeout)
        response_text = response.text.encode('utf-8')  # get text from response

        # check if we got an error
        # -------------------------------------------------------------
        if 'ERROR:' in response_text and response_text.split('|') != 2:
            response_err = response_text.split('ERROR:')[1].strip()
            self._error = response_err
            raise Exception(response_err)  # raise Ex

        c = Captcha(response_text)  # init captcha from response
        self._normal_captcha = c  # save last captcha to obj
        return c.text

    # submit recaptcha to system
    # SET PROXY AS WELL
    # -------------------
    # ----------------------------------
    # ------------------------------
    def submit_recaptcha(self, page_url, sitekey, proxy = None, proxy_type = None):
        # check if page_url and sitekey are != None
        if not page_url: raise Exception('provide a valid page_url')
        if not sitekey: raise Exception('provide a valid sitekey')

        data = {}       # create data obj here, we might need it for proxy

        # check proxy and set dict (request params) accordingly
        if proxy:   # if proxy is given, check proxytype
            if not proxy_type:
                raise Exception('proxy was provided, but no proxy_type')
            # we have both proxy and type at this point
            data['proxy'] = proxy
            data['proxytype'] = proxy_type

        # init dict params  (request params)
        data['action'] = 'UPLOADCAPTCHA'
        data['username'] = self._username
        data['password'] = self._password
        data['pageurl'] = page_url
        data['googlekey'] = sitekey
        # update with refid
        data['refid'] = self._ref_id

        # make request with all data
        response = self._session.post(RECAPTCHA_SUBMIT_ENDPOINT, data=data,
                                      headers=self._headers, timeout=self._timeout)
        response_text = response.text.encode('utf-8')  # get text from response

        # check if we got an error
        # -------------------------------------------------------------
        if 'ERROR:' in response_text and response_text.split('|') != 2:
            response_err = response_text.split('ERROR:')[1].strip()
            self._error = response_err
            raise Exception(response_err)  # raise Ex

        self._recaptcha = Recaptcha(response_text)      # init recaptcha obj with captcha_id (which is in the resp)

        return self._recaptcha.captcha_id           # return the ID

    # retrieve recaptcha
    def retrieve_recaptcha(self, captcha_id = None):
        # if captcha id is not specified, use the ID of the last captcha submited
        if not captcha_id:
            if not self._recaptcha: raise Exception('no recaptcha was submited previously, submit a captcha'
                                                  ' first or give captcha_id as argument')     # raise it
            captcha_id = self._recaptcha.captcha_id

        # create params dict (multipart)
        data = {
            'action': 'GETTEXT',
            'username': self._username,
            'password': self._password,
            'captchaid': captcha_id,
            # update with refid
            'refid' : self._ref_id
        }

        # make request with all data
        response = self._session.post(RECAPTCHA_RETRIEVE_ENDPOINT, data=data,
                                      headers=self._headers, timeout=self._timeout)
        response_text = response.text.encode('utf-8')  # get text from response

        # check if we got an error
        # -------------------------------------------------------------
        if 'ERROR:' in response_text and response_text.split('|') != 2:
            response_err = response_text.split('ERROR:')[1].strip()
            # if error is different than NOT_DECODED, save it to obj
            if response_err != 'NOT_DECODED': self._error = response_err

            raise Exception(response_err)  # raise Ex

        self._recaptcha.set_response(response_text)     # set response to recaptcha obj

        return response_text            # return response

    # check if captcha is still being decoded
    def in_progress(self, captcha_id = None):
        try:
            self.retrieve_recaptcha(captcha_id)     # retrieve captcha
            return False                             # captcha got decoded
        except Exception, ex:
            if 'NOT_DECODED' in str(ex):        # if NOT_DECODED in response, it's 'OK'
                return True

            raise       # raise Exception if different error

    # get account balance
    def account_balance(self):
        data = {
            "action": "REQUESTBALANCE",
            "username": self._username,
            "password": self._password,
            "submit": "Submit"
        }

        response = self._session.post(BALANCE_ENDPOINT, data=data,
                                      headers=self._headers, timeout=self._timeout)
        response_text = response.text.encode('utf-8')

        # check if we have an error
        if 'ERROR:' in response_text:
            response_err = response_text.split('ERROR:')[1].strip()     # split the string
            self._error = response_err                                  # save error to obj
            raise Exception(response_err)                               # raise

        return '${}'.format(response_text)        # we don't, return balance

    # set captcha bad, if given id, otherwise set the last one
    def set_captcha_bad(self, captcha_id):
        # check if we have solved a captcha
        if not self._normal_captcha: raise Exception('no captcha id given and no captcha solved before')

        data = {
            "action": "SETBADIMAGE",
            "username": self._username,
            "password": self._password,
            "imageid": captcha_id,
            "submit": "Submissssst"
        }

        # make request
        response = self._session.post(BAD_IMAGE_ENDPOINT, data=data,
                                      headers=self._headers, timeout=self._timeout)
        response_text = response.text.encode('utf-8')

        # check if we have an error
        if 'ERROR:' in response_text:
            response_err = response_text.split('ERROR:')[1].strip()     # split the string
            self._error = response_err                                  # save error to obj
            raise Exception(response_err)                               # raise

        return response_text  # we don't, return balance

    # get last captcha text
    @property
    def captcha_text(self):
        if not self._normal_captcha: return ''     # if captcha is not set yet, return nothing
        return self._normal_captcha.text           # return text

    # get last captcha id
    @property
    def captcha_id(self):
        if not self._normal_captcha: return ''  # if captcha is not set yet, return nothing
        return self._normal_captcha.captcha_id          # return id

    # get last recaptcha id
    @property
    def recaptcha_id(self):
        if not self._recaptcha: return ''       # return none if none
        return self._recaptcha.captcha_id       # return id

    # get last recaptcha response
    @property
    def recaptcha_response(self):
        if not self._recaptcha: return ''       # return nothing if not set yet
        return self._recaptcha.response         # return response

    # get last error
    @property
    def error(self):
        return self._error
