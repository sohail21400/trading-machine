from fyers_api import fyersModel
from fyers_api import accessToken
import webbrowser
import os
import credentials.credentials as cred
import pathlib


def login():
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # getting the path of credentials directory
    credentials_dir = os.path.join(current_file_dir, 'credentials')

    # this loop is gonna run maximum 2 times
    # one is to get data from the internet / or from file
    # if the token is expired which is obtained from either both of the sources
    # then it will run again to get the new token from the internet, not from file
    i = 1
    while i <= 2:
        # token file does not exist or token has expired (i.e. i == 2)
        if not os.path.exists(credentials_dir + '/' + 'fyers_token.txt') or i == 2:
            print("token file not found")
            # Getting new auth token
            session = accessToken.SessionModel(client_id=cred.client_id,
                                               secret_key=cred.secret_key, redirect_uri=cred.redirect_uri,
                                               response_type='code', grant_type='authorization_code',
                                               )
            generateTokenURL = session.generate_authcode()
            webbrowser.open(generateTokenURL)
            print("Login via this URL: ", generateTokenURL)

            auth_code = input("Enter the auth code: ")
            session.set_token(auth_code)
            response = session.generate_token()
            # print(response)

            try:
                access_token = response["access_token"]
                refresh_token = response["refresh_token"]
                with open(credentials_dir + '/' + 'fyers_token.txt', 'w') as f:
                    f.write(access_token)
                with open(credentials_dir + '/' + 'fyers_refresh_token.txt', 'w') as f:
                    f.write(refresh_token)
                return access_token
            except Exception as e:
                print(e, response)
                return

        else:
            # token file exists
            # getting old auth token
            with open(credentials_dir + '/' + 'fyers_token.txt', 'r') as f:
                access_token = f.read()
            with open(credentials_dir + '/' + 'fyers_refresh_token.txt', 'r') as f:
                refresh_token = f.read()

            # checking if token is valid
            # sending a request to get user details
            fyers = fyersModel.FyersModel(
                client_id=cred.client_id, token=access_token, log_path=current_file_dir + '/' + "log")
            response = fyers.get_profile()

            if response['s'] == 'error':
                # token is invalid, we need to get a new token
                print("token is invalid, fetching new token......")
                # rerunning the loop and getting new token from api not from file
                i += 1
            else:
                print("token is valid")
                return access_token


# fyers = fyersModel.FyersModel(client_id=cred.client_id, token="asdf",log_path="/log")
# fyers.get_profile()
login()
