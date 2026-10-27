"""
https://github.com/EOL/publishing/blob/master/doc/api.md
https://github.com/EOL/publishing/blob/master/doc/trait-schema.md?utm_source=chatgpt.com
https://opentraits.org/datasets/avonet.html
https://opentraits.org/datasets.html
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd


class APIWrapper:
    def __init__(
            self,
            base_url,
            headers,
            timeout,
            auth
    ):
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout
        self.auth = auth

    def request_data(self, endpoint, params={}):

        request_url = "{}{}".format(self.base_url, endpoint)
        response = requests.get(
            request_url,
            params,
            timeout=self.timeout
        )

        print(f"Request URL: {request_url} | Response code: {response.status_code}")

        results = response.json()

        return results


    def build_query(self):
        pass
        endpoint = "/search/1.0.json"

    def format_query(self):
        return super().request(query_url, params=params)
        pass


class ClassicAPI(APIWrapper):
    def __init__(
        self,
        base_url="https://eol.org/api/",
        headers=None,
        auth=None,
        timeout=60
    ):
        super().__init__(base_url=base_url, headers=headers, auth=auth, timeout=timeout)
        self.ping_endpoint = "ping.json"


    def ping_api(self):
        return super().request_data(self.ping_endpoint)

    def search_species(self, species_name):
        endpoint = "/search/1.0.json"
        params = {"q": species_name, "page": 1}

        request_response = super().request_data(endpoint, params=params)
        results = self.inspect_results(request_response, species_name)

        return results

    def inspect_results(self, results, species_name):
        results = results['results']

        valid_species = {}

        for result in results:
            sp_id = result.get("id")
            sp_title = result.get("title")
            sp_link = result.get("link")

            if sp_title == species_name:
                print(f"Sp id: {sp_id}")
                valid_species['name'] = sp_title
                valid_species['id'] = sp_id
                valid_species['page'] = sp_link

            print(
                f"Species ID: {sp_id}",
                f"Taxonomic name: {sp_title}",
                f"Page link: {sp_link}",
                f"---",
                sep="\n"
            )

        if not bool(valid_species):
            print(f"Valid species ID expected to be: {valid_species['id']}")

        return valid_species

    def get_species_traits(self, species_id):
        endpoint = "/species/{}/traits".format(species_id)

    def build_query(self, endpoint):
        pass

    def format_query(self):
        pass

    def request_data(self):
        print("In child")

# Scraping won't work with EoL security
class TraitScrapper(APIWrapper):
    def __init__(
        self,
        base_url="https://eol.org/pages/",
        auth=None,
        timeout=60
    ):
        headers_mozilla = {
                "User-Agent": "Mozilla/5.0"
            }
        super().__init__(base_url=base_url, headers=headers_mozilla, auth=auth, timeout=timeout)

    def request_data(self, url_page):
        response = requests.get(
            url_page,
            headers=self.headers,
            timeout=self.timeout
        )
        if response.status_code == 403:
            print("EOL forbid access!")
        else:
            return response

    def scrape_species(self, species_id):
        url_page = "{}{}/data".format(self.base_url, species_id)

        response = self.request_data(url_page)

        soup = BeautifulSoup(response.text, "html.parser")
        print(soup.title.get_text(strip=True))
        print(soup.get_text(separator="\n", strip=True))