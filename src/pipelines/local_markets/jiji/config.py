# config.py
class BrowserConfig:
    LOGIN_URL = "https://www.jiji.ng/login.html"
    EMAIL_FIELD = "input.qa-login-field"
    PASSWORD_FIELD = "input.qa-password-field"
    LOGIN_BUTTON = "button:has-text('SIGN IN')"
    LOGIN_TIMEOUT = 30  # seconds