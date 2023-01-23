import jwt
import bcrypt
import logging
import json
import requests
import streamlit as st
from datetime import datetime, timedelta
import extra_streamlit_components as stx

from .hasher import Hasher
from .utils import generate_random_pw

from .exceptions import CredentialsError, ForgotError, RegisterError, ResetError, UpdateError

logger = logging.getLogger(__name__)
BACKEND_HOST_PORT = "http://172.17.0.1:5000"


class Authenticate:
    """
    This class will create login, logout, register user, reset password, forgot password,
    forgot username, and modify user details widgets.
    """

    def __init__(self, cookie_name: str, key: str, cookie_expiry_days: int = 30, test_mode: bool = False):
        """
        Create a new instance of "Authenticate".

        Parameters
        ----------
        cookie_name: str
            The name of the JWT cookie stored on the client's browser for passwordless reauthentication.
        key: str
            The key to be used for hashing the signature of the JWT cookie.
        cookie_expiry_days: int
            The number of days before the cookie expires on the client's browser.
        preauthorized: list
            The list of emails of unregistered users authorized to register.
        """
        self.test_mode = test_mode
        self.cookie_name = cookie_name
        self.key = key
        self.cookie_expiry_days = cookie_expiry_days
        self.cookie_manager = stx.CookieManager()

        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'username' not in st.session_state:
            st.session_state['username'] = None
        if 'logout' not in st.session_state:
            st.session_state['logout'] = None

    def _token_encode(self) -> str:
        """
        Encodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The JWT cookie for passwordless reauthentication.
        """
        return jwt.encode(
            {'username': st.session_state['username'], 'exp_date': self.exp_date}, self.key, algorithm='HS256'
        )

    def _token_decode(self) -> str:
        """
        Decodes the contents of the reauthentication cookie.

        Returns
        -------
        str
            The decoded JWT cookie for passwordless reauthentication.
        """
        try:
            return jwt.decode(self.token, self.key, algorithms=['HS256'])
        except:
            return False

    def _set_exp_date(self) -> str:
        """
        Creates the reauthentication cookie's expiry date.

        Returns
        -------
        str
            The JWT cookie's expiry timestamp in Unix epoch.
        """
        return (datetime.utcnow() + timedelta(days=self.cookie_expiry_days)).timestamp()

    def _check_cookie(self):
        """
        Checks the validity of the reauthentication cookie.
        """
        self.token = self.cookie_manager.get(self.cookie_name)
        if self.token is not None:
            self.token = self._token_decode()
            if self.token is not False:
                if not st.session_state['logout']:
                    if self.token['exp_date'] > datetime.utcnow().timestamp():
                        if 'username' in self.token:
                            st.session_state['username'] = self.token['username']
                            st.session_state['authentication_status'] = "logged_in"

    def _user_exists(self, username: str):
        return requests.get(f"{BACKEND_HOST_PORT}/user_exists", json={"login": username}).json()

    def _check_credentials(self, username: str, password: str) -> bool:
        """
        Checks the validity of the entered credentials.

        Parameters
        ----------
        inplace: bool
            Inplace setting, True: authentication status will be stored in session state,
            False: authentication status will be returned as bool.
        Returns
        -------
        bool
            Validity of entered credentials.
        """

        if self.test_mode:
            return True

        if self._user_exists(username):
            try:
                r = requests.get(f"{BACKEND_HOST_PORT}/login_user", json={"login": username, "password": password})
                return r.json()
            except Exception as e:
                print(e)
        else:
            return False

    def login(self, form_name: str, location: str = 'main') -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered,
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if st.session_state['authentication_status'] != "logged_in":
            self._check_cookie()
            if st.session_state['authentication_status'] != "logged_in":
                login_form = st.form("Login")
                login_form.subheader(form_name)
                username = login_form.text_input('Username').lower()
                password = login_form.text_input('Password', type='password')

                if login_form.form_submit_button('Login'):
                    if self._check_credentials(username, password):
                        st.session_state['authentication_status'] = "logged_in"
                        st.session_state['username'] = username
                    else:
                        st.session_state['authentication_status'] = "wrong_credentials"
                        st.session_state['username'] = None

    def logout(self, button_name: str, location: str = 'main'):
        """
        Creates a logout button.

        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button i.e. main or sidebar.
        """
        if location not in ['main', 'sidebar']:
            raise ValueError("Location must be one of 'main' or 'sidebar'")
        if location == 'main':
            if st.button(button_name):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state['logout'] = True
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None
        elif location == 'sidebar':
            if st.sidebar.button(button_name):
                self.cookie_manager.delete(self.cookie_name)
                st.session_state['logout'] = True
                st.session_state['username'] = None
                st.session_state['authentication_status'] = None

    def _register_credentials(self, username: str, password: str):
        """
        Adds to credentials dictionary the new user's information.

        Parameters
        ----------
        username: str
            The username of the new user.
        password: str
            The password of the new user.
        """

        requests.post(f"{BACKEND_HOST_PORT}/add_users", json={"login": username, "password": password})

    def register_user(self, form_name: str, location: str = 'main') -> bool:
        """
        Creates a password reset widget.

        Parameters
        ----------
        form_name: str
            The rendered name of the password reset form.
        location: str
            The location of the password reset form i.e. main or sidebar.
        preauthorization: bool
            The pre-authorization requirement, True: user must be pre-authorized to register,
            False: any user can register.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """

        register_user_form = st.form('Register user')
        register_user_form.subheader(form_name)
        new_username = register_user_form.text_input('Username').lower()
        new_password = register_user_form.text_input('Password', type='password')
        new_password_repeat = register_user_form.text_input('Repeat password', type='password')

        if register_user_form.form_submit_button('Register'):
            if len(new_username) and len(new_password) > 0:
                if self.test_mode or not self._user_exists(new_username):
                    if new_password == new_password_repeat:
                        if not self.test_mode:
                            self._register_credentials(new_username, new_password)
                        return True
                    else:
                        raise RegisterError('Passwords do not match')
                else:
                    raise RegisterError('Username already taken')
            else:
                raise RegisterError('Please enter an email, username, name, and password')
