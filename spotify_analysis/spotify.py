"""
Module to handle all access requests to Spotify web API
"""
import asyncio
import time
import json
import logging
import yaml
import requests
from tqdm import tqdm
from aiohttp import ClientSession


AUTH_URL = 'https://accounts.spotify.com/api/token'
BASE_URL = 'https://api.spotify.com/v1/'


class Spotify:
    """
    Class to handle all access requests to Spotify web API

    Attributes
    ----------
    cred : dict
        Dictionary containing the credentials to connect to
        Spotify's web API (`CLIENT_ID` and `CLIENT_SECRET`)
    access_token : str
        String with access token containing credentials and
        permissions to access Spotify resources. Valid for
        3600 seconds
    headers : dict
        Dictionary containing header with access token to be
        included in Spotify API calls
    metadata : dict
        Dictionary containing the requested metadata stored
        with the uri as keys

    reference : str, default 'tracks'
        String that contains which metadata API should access.
        Example: 'tracks', 'artists', ...
    batch_size : int, default 200
        Integer of size of batch that is processed in one go
        with asyncio (to avoid timeouts of Spotify API)
    sec_wait : int, default 5
        Integer of how many seconds one should wait between
        different batches of uri's (to avoid timeout of API)
    """

    def __init__(self, reference='tracks', batch_size=200, sec_wait=5):

        self.cred = {}
        self.access_token = None
        self.headers = {}
        self.metadata = {}

        self.batch_size = batch_size
        self.sec_wait = sec_wait
        self.reference = reference

    def get_spotify_credentials(self, secret_yaml_file):
        """
        Loads your spotify credentials from a yaml configuration file

        Parameters
        ----------
        secret_yaml_file : str
            The file location of your spotify credentials. Should contain
            your `CLIENT_ID` and `CLIENT_SECRET`
        """

        with open(secret_yaml_file, 'r', encoding='utf-8') as file:
            self.cred = yaml.safe_load(file)

    def get_spotify_access_token(self):
        """
        Store spotify access token and headers to access Spotify's
        resources via calls to web API.

        See https://developer.spotify.com/documentation/web-api/concepts/access-token
        """

        auth_response = requests.post(AUTH_URL,
                                      {'grant_type': 'client_credentials',
                                       'client_id': self.cred['CLIENT_ID'],
                                       'client_secret': self.cred['CLIENT_SECRET']
                                       },
                                      timeout=10)
        auth_response_data = auth_response.json()
        self.access_token = auth_response_data['access_token']

        self.headers = {'Authorization': f'Bearer {self.access_token}'}

    def access_spotify_api(self, uri_list, metadata, n_uri=50):
        """
        Access Spotify metadata via `requests` (i.e. non asynchronous)

        Might be the best option, since too many requests to Spotify API
        will block it because API rate limit exceeded.

        Parameters
        ----------
        uri_list : list of str
            List of Spotify uri's in string format to be accessed
        metadata : list of str
            List of the metadata keys that are requested to be saved
        n_uri : int
            Integer of how many uri's are accessed in the same request
        """

        for ibx in tqdm(range(0, len(uri_list), n_uri)):
            uri = uri_list[ibx:ibx + n_uri]

            if len(uri) == 1:
                url = BASE_URL + self.reference + '/' + uri[0]
            else:
                url = BASE_URL + self.reference + '?ids=' + '%2C'.join(uri)
            res = requests.get(url, headers=self.headers, timeout=10)

            try:
                output = res.json()
                self.fill_metadata_dictionary(output, uri, metadata)
            except AttributeError:
                logging.warning("API request not succesful!")
                logging.warning(res)
                break

    def fill_metadata_dictionary(self, output, list_uri, metadata):
        """
        Fill the metadata dictionary from processed uri. Metadata can
        be 1-deep or 2-deep, and all should (so far) have the same deepness.

        Parameters
        ----------
        output : dict
            Spotify's metadate from given uri in json format
        list_uri : list of str or str
            Spotify uri's in string format to be accessed. List in case
            when multiple uri's are accessed by same request.
        metadata : list of str
            List of the metadata keys that are requested to be saved
        """

        # Create correct output dictionary in case of 1 processed uri
        if len(list_uri) == 1:
            output = {self.reference: [output]}

        # Get metadata 1-deep
        if not isinstance(metadata[0], list):
            for n_uri, uri in enumerate(list_uri):
                self.metadata[uri] = dict.fromkeys(metadata)
                for mdata in metadata:
                    self.metadata[uri][mdata] = output[self.reference][n_uri][mdata]
            return

        # Metadata 2-deep
        if len(metadata[0]) != 2:
            logging.fatal('Can only process metadata that is 1- or 2-deep!')

        for n_uri, uri in enumerate(list_uri):
            metadata_1 = [sublist[0] for sublist in metadata]
            metadata_2 = [sublist[-1] for sublist in metadata]
            self.metadata[uri] = dict.fromkeys(metadata_2)
            for imd, mdata in enumerate(metadata_2):
                output_new = output[self.reference][n_uri][metadata_1[imd]]
                if not isinstance(output_new, list):
                    self.metadata[uri][mdata] = output_new[mdata]
                else:
                    self.metadata[uri][mdata] = output_new[0][mdata]

    def access_spotify_api_async(self, uri_list, metadata):
        """
        Access Spotify metadata via `aiohttp` (i.e. asynchronous).
        First function to process the input in batches

        Note that too many requests to Spotify API will block the
        script because the API rate limit exceeded. This can be
        controlled by `self.batch_size` and `self.sec_wait`. Function
        will terminate in case one API request was not succesful.

        Parameters
        ----------
        uri_list : list of str
            List of Spotify uri's in string format to be accessed
        metadata : list (of list) of str
            List of the metadata keys that are requested to be saved
            In case of double list the requested data is two-layer deep
        """

        # TODO: Add option to access n<=50 ids at once

        total_size = len(uri_list)
        for ibx in tqdm(range(0, total_size, self.batch_size)):
            succes = asyncio.run(self.get_metadata_api(uri_list[ibx:ibx + self.batch_size],
                                                       metadata
                                                       )
                                 )
            if not succes:
                break
            time.sleep(self.sec_wait)

    async def get_metadata_api(self, uri_list, metadata):
        """
        Access Spotify metadata via `aiohttp` (i.e. asynchronous)
        Actual code to access metadata. Should be called in batches
        by `access_spotify_api_async(uri_list, metadata)`

        Parameters
        ----------
        uri_list : list of str
            List of Spotify uri's in string format to be accessed
        metadata : list of str
            List of the metadata keys that are requested to be saved
            In case of double list the requested data is two-layer deep

        Return
        ------
        bool
            Boolean if accessing metadata was succesful. Stop process in
            case of error (typically because API rate limit exceeded)
        """

        base_url = 'https://api.spotify.com/v1/'

        results = []
        queue = asyncio.Queue()
        async with asyncio.TaskGroup() as group:
            for uri in uri_list:
                url = base_url + self.reference + '/' + uri
                group.create_task(self.make_request(url, queue))

        while not queue.empty():
            results.append(await queue.get())

        for res in results:
            try:
                output = json.loads(res['response'])
                uri = res['url'].split('/')[-1]
                self.fill_metadata_dictionary(output, uri, metadata)
            except AttributeError:
                logging.warning("API request not succesful!")
                logging.warning(res)
                return False
        return True

    async def make_request(self, url, queue: asyncio.Queue):
        """
        Asynchronously makes an HTTP GET request to the specified URL
        using the aiohttp library. The ClientSession with custom headers
        created by `get_spotify_access_token()`. The response is stored
        in a dictionary along with the original URL and put into the
        specified asyncio queue. A small sleep of 0.01 seconds is
        introduced to avoid potential blocking issues.

        Parameters
        ----------
        url : str
            The URL to which the GET request is made.
        queue : asyncio.Queue
            An asyncio queue to store the results of the request.
        """

        async with ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                result = {'response': await response.text(),
                          'url': url}
                await queue.put(result)
                await asyncio.sleep(0.01)
