============================================================================================
Python API
============================================================================================
You can use the API by importing the imagetypersapi.py file and by using the ImagetypersAPI
class.
============================================================================================
Below you have some examples on how to use the API library (taken from main.py)
--------------------------------------------------------------------------------------------
from imagetypersapi import ImageTypersAPI

username = 'testuesrname'
password = '************'

ita = ImageTypersAPI(username, password)      # init imagetyperz api obj

# check account balance
# ---------------------------
balance = ita.account_balance()                       # get account balance
print 'Balance: {}'.format(balance)                 # print balance

# solve normal captcha
print 'Waiting for captcha to be solved ...'
# -----------------------------------------------------------------------------------------------
captcha_text = ita.solve_captcha('captcha.jpg', case_sensitive = True)  # solve captcha, with case sensitive arg True
print 'Captcha text: {}'.format(captcha_text)       # print captcha solved text
# -----------------------------------------------------------------------------------------------

# solve recaptcha
# ---------------
# check: http://www.imagetyperz.com/Forms/recaptchaapi.aspx on how to get page_url and googlekey
# -----------------------------------------------------------------------------------------------
page_url = 'https://imagetyperz.com/wp-login.php'
sitekey = '6LdlvgUTAAAAANXvG6Oo0odap_L3oZ29fRZ3LEbr'
captcha_id = ita.submit_recaptcha(page_url, sitekey)        # submit captcha first, to get ID

# check if it's still in progress (waiting to be solved), every 10 seconds
print 'Waiting for recaptcha to be solved ...'
while ita.in_progress():    # while it's still in progress
	sleep(10)               # sleep for 10 seconds and recheck

recaptcha_response = ita.retrieve_recaptcha(captcha_id)           # captcha_id is optional, if not given, will use last captcha id submited
print 'Recaptcha response: {}'.format(recaptcha_response)         # print google response

# other examples
# --------------------------------------------------------------------------------------
# ita = ImageTyperzAPI('testingfor', 'testingfor', 60)       # use a timeout of 60 seconds on requests
# ita = ImageTyperzAPI('testingfor', 'testingfor', 60, 5)    # use timeout and ref id

# submit recaptcha with proxy (checks API docs for more info)
# captcha_id = ita.submit_recaptcha(page_url, sitekey, '127.0.0.1:1234', 'HTTP')

# print ita.captcha_id               # get the last captcha solved id
# print ita.captcha_text             # get the last captcha solved text

# print ita.recaptcha_id             # get last recaptcha solved id
# print ita.recaptcha_response       # get last recaptcha solved response

# print ita.set_captcha_bad(captcha_id)        # set last captcha as bad, or set it by using ID
# print ita.error                    # get the last error encountered
======================================================================================================
[*] Requires PHP installed