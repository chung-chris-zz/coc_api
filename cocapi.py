import requests
from requests.exceptions import Timeout


class cocapi:
    def __init__(self, token, clan_tag_str, timeout=10):
        """
        Initialize class parameters
        """    
        self.token = token
        self.clan_tag_str = clan_tag_str
        self.timeout = timeout
        self.end_point = 'https://api.clashofclans.com/v1/'
        self.headers = {
            'Accept': 'application/json',
            'authorization': f'Bearer {token}'
        }


    def api_response(self, uri):
        """
        Get API response
        """
        try:
            r = requests.get(
                f'{self.end_point}{uri}',
                headers=self.headers,
                timeout=self.timeout
                )

            return r.json()
        except Timeout:
            print('The request timed out')
        else:
            print('The request failed but did not time out')
    

    def clan_tag(self):
        """
        Get clan info by clan tag
        """
        uri = f'clans/%23{self.clan_tag_str}'

        return self.api_response(uri)


    def clan_leaguegroup(self):
        """
        Get clan league group data and return response
        """
        uri = f'clans/%23{self.clan_tag_str}/currentwar/leaguegroup'

        return self.api_response(uri)
    

    def cwl_war(self, war_tag):
        """
        Get CWL war data and return response
        """
        uri = f'clanwarleagues/wars/%23{war_tag}'

        return self.api_response(uri)