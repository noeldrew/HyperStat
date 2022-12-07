import requests
import json
import datetime
from datetime import datetime, date, timedelta

from dotenv import load_dotenv
from urllib3.exceptions import HTTPError
load_dotenv()
from os import environ



class HyperPassAPI:

    _authorisation_token: str
    _api_base_url: str = 'https://api.stage.hyperspace-ticketing.apptoku.com/api'
    _client_id: str = 'U5MLz5eI57hNELrH8nKSKj61GnW12bgRgf0ycb9N'
    # _client_secret: str = 'eCipyIdmN0tQwxoXsRqBZ0cbtKuzFMRAUSN7JR7ytzkHkHf1cDyzyeydzQdmyfTYOltM07JgqtNYlaOXfeLGfo9CL6oxSgI8LOvdCk2sides0HZgLoN1teAbZ1ZWZamK'
    _client_secret = environ.get('HYPER_PASS_SECRET')
    _event_id: str = 'e91cd3da-01d2-4082-8cd7-138f78dec538'

    def __init__(self):
        return

    def getClientAuthorisationToken(self) -> bool:
        endpoint = self._api_base_url + '/o/token/'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        r = requests.post(url=endpoint, data=data, headers=headers)
        try:
            r.raise_for_status()
            # access JSOn content
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

    def getTicketTypes(self):
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

    def getTimeSlotsToday(self):
        endpoint = self._api_base_url + '/tickets/slots/'
        today = self._getTodayUTC()
        headers = {
            'Authorization': "Bearer " + self._authorisation_token
        }
        data = {
            'event': self._event_id,
            'from_date': today['iso_start_date'],
            'to_date': today['iso_end_date'],
            'allow_overbooking': 'true'
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

    def getTimeSlotsPerDay(self):
        pass

    def createOrder(self):
        pass

    def updateOrderStatus(self):
        pass

    def retrieveOrderById(self):
        pass

    def retrieveOrderByRef(self):
        pass

    def _getTodayUTC(self, utc_offset:int = 4) -> dict:
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
            'start_date': utc_start,
            'end_date': utc_end,
            'iso_start_date': iso_start,
            'iso_end_date': iso_end
        }

    def _formURLParamsString(self, params: dict) -> str:
        param_key_val_list = []
        for key in params.keys():
            param_key_val_list.append('='.join([key, params[key]]))
        rtn_string = '?' + "&".join(param_key_val_list)
        return rtn_string


