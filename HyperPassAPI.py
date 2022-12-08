import requests
import json
import datetime
from datetime import datetime, date, timedelta

from urllib3.exceptions import HTTPError


class HyperPassAPI:
    _authorisation_token: str
    _api_base_url: str = 'https://api.hyperpass.aya-universe.com/api'
    _client_id: str = 'nkrvwcUrJvFXmvTA6WeQ14RstrSMsYU8tY2BsqSo'
    _client_secret = 'qGBwYN6JNpw5zKNEHsMAu8FtiuCDA7ONh2ugAVJ8XicouhrmJe25TjTsOXeSvyyEsUe7obJpaqNJs5uV4QrJmovQoihL5LbvZhtGMTsXh4gb3rqjcpV4SfGcmgvR4umo'
    _event_id: str = '38f6c672-09e5-4737-9134-3e630d4ea78e'

    _zero_hour: str = '2022-12-07T16:00:00.00'

    def __init__(self):
        return

    def getClientAuthorisationToken(self) -> bool:
        print('getting client authorisation token')
        endpoint = self._api_base_url + '/o/token/'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        data = {
            'grant_type'   : 'client_credentials',
            'client_id'    : self._client_id,
            'client_secret': self._client_secret
        }
        r = requests.post(url=endpoint, data=data, headers=headers)
        try:
            r.raise_for_status()
            json_obj = r.json()
            self._authorisation_token = json_obj['access_token']
            print('Authorisation token:', self._authorisation_token)
            return True

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return False
        except Exception as err:
            print(f'Other error occurred: {err}')
            return False

    def getAllTicketsToDate(self) -> dict:
        print('getting all tickets between dates...')
        print(self._zero_hour, ' => ', self._getNowUTC())

        endpoint = self._api_base_url + '/tickets/purchased/'
        headers = {
            'Authorization': "Bearer " + self._authorisation_token
        }
        data = {
            'event'    : self._event_id,
            'from_date': self._zero_hour,
            'to_date'  : self._getNowUTC()
        }
        endpoint += self._formURLParamsString(data)
        r = requests.get(url=endpoint, headers=headers)
        try:
            r.raise_for_status()
            json_dict = r.json()
            return json_dict['tickets']

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return False
        except Exception as err:
            print(f'Other error occurred: {err}')
            return False

    def getAllTicketsForPastPeriod(self, period_in_hours: int) -> dict:
        print('getting all tickets between dates...')
        print(self._zero_hour, ' => ', self._getNowUTC())

        endpoint = self._api_base_url + '/tickets/purchased/'
        headers = {
            'Authorization': "Bearer " + self._authorisation_token
        }
        data = {
            'event'    : self._event_id,
            'from_date': self._getThenUTC(period_in_hours),
            'to_date'  : self._getNowUTC()
        }
        endpoint += self._formURLParamsString(data)
        r = requests.get(url=endpoint, headers=headers)
        try:
            r.raise_for_status()
            json_dict = r.json()
            return json_dict

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return False
        except Exception as err:
            print(f'Other error occurred: {err}')
            return False

    def getTicketTypes(self):
        print('getting ticket types')
        endpoint = self._api_base_url + '/tickets/types/'
        headers = {
            'Authorization': "Bearer " + self._authorisation_token
        }
        data = {
            'event': self._event_id
        }
        endpoint += self._formURLParamsString(data)
        r = requests.get(url=endpoint, headers=headers)
        try:
            r.raise_for_status()
            json_dict = r.json()
            return json_dict

        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            return False
        except Exception as err:
            print(f'Other error occurred: {err}')
            return False

    def _getTodayUTC(self, utc_offset: int = 4) -> dict:
        today = date.today()
        local_start = datetime(today.year, today.month, today.day, 00, 00, 00)
        local_end = datetime(today.year, today.month, today.day, 23, 59, 59)
        delta = timedelta(hours=utc_offset)
        utc_start = local_start - delta
        utc_end = local_end - delta
        iso_start = utc_start.isoformat()
        iso_end = utc_end.isoformat()

        print(iso_start, iso_end)
        return {
            'start_date'    : utc_start,
            'end_date'      : utc_end,
            'iso_start_date': iso_start,
            'iso_end_date'  : iso_end
        }

    def _getNowUTC(self, utc_offset: int = 4) -> dict:
        now = datetime.now()
        delta = timedelta(hours=utc_offset)
        utc_now = now - delta
        iso_now = utc_now.isoformat()
        return str(iso_now)

    def _getThenUTC(self, then_offset: int, utc_offset: int = 4) -> dict:
        now = datetime.now()
        delta = timedelta(hours=(utc_offset + then_offset))
        utc_then = now - delta
        iso_then = utc_then.isoformat()
        return str(iso_then)

    def _formURLParamsString(self, params: dict) -> str:
        param_key_val_list = []
        for key in params.keys():
            param_key_val_list.append('='.join([key, params[key]]))
        rtn_string = '?' + "&".join(param_key_val_list)
        return rtn_string
