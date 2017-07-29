# Imagetyperz captcha API test
# ------------------------------
from imagetypersapi import ImageTypersAPI
from time import sleep

# solve captcha
def test_api():
    username = 'user name here'
    password = 'password here'

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
    page_url = 'page url here'
    sitekey = 'key code here'
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

# main method
def main():
    try:
        test_api()     # test captcha API
    except Exception, ex:
        print '[!] Error occured: {}'.format(ex)

if __name__ == "__main__":
    main()
