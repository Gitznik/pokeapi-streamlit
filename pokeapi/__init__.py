from itertools import chain
import streamlit as st
import requests
import pandas as pd
from streamlit.connections import ExperimentalBaseConnection
from dataclasses import dataclass
from datetime import timedelta

ttl_duration = float | timedelta | str | None


@dataclass
class ApiResponse:
    count: int
    next: str | None
    previous: str | None
    results: dict


class PokeApiConnection(ExperimentalBaseConnection[requests.Session]):
    """
    Connection for the PokeAPI REST API.

    Args:
        **kwargs: The keyword arguments are passed through to initiating
            a requests.Session object.

    Attributes:
        base_url (str): The base URL to the PokeAPI REST API.
    """

    base_url = "https://pokeapi.co/api/v2"

    def _connect(self, **kwargs) -> requests.Session:
        _ = kwargs
        return requests.session()

    def list_available_endpoints(
        self, ttl: ttl_duration = 3600, **kwargs
    ) -> pd.DataFrame:
        """Lists all available endpoints on the API

        Args:
            ttl (ttl_duration): The maximum time to keep an entry in the cache
            **kwargs: These are passed through to the requests.get method

        Raises:
            requests.HTTPError: Any HTTP error occured

        Returns:
            endpoints (DataFrame): A DataFrame containing all endpoints and their URLs
        """

        @st.cache_data(ttl=ttl)
        def _request(**kwargs) -> pd.DataFrame:
            session = self._instance
            res = session.get(self.base_url, **kwargs)
            res.raise_for_status()
            return pd.DataFrame.from_dict(res.json(), orient="index")

        return _request(**kwargs)

    def list_available_resources(
        self, endpoint: str, limit: int = 20, ttl: int = 3600, **kwargs
    ) -> pd.DataFrame:
        """Lists all available resources within an endpoint

        Args:
            endpoint (str): Which endpoint to execute the API call against
            limit (int): Maximum number of resources per page
            ttl (ttl_duration): The maximum time to keep an entry in the cache
            **kwargs: These are passed through to the requests.get method

        Raises:
            requests.HTTPError: Any HTTP error occured

        Returns:
            endpoints (DataFrame): A DataFrame containing all resources and their
                URLs.
        """

        @st.cache_data(ttl=ttl)
        def _request(endpoint: str, **kwargs) -> pd.DataFrame:
            session = self._instance
            path = [self.base_url, endpoint]
            path = "/".join(path)
            params = {"limit": limit}
            res = session.get(path, params=params, **kwargs)
            res.raise_for_status()
            res = ApiResponse(**res.json())
            marker = res.next
            results = [res.results]
            while marker:
                res = session.get(path, params=params, **kwargs)
                res.raise_for_status()
                res = ApiResponse(**res.json())
                marker = res.next
                results.append(res.results)

            flat_results = chain.from_iterable(results)
            return pd.DataFrame(flat_results)

        return _request(endpoint, **kwargs)

    def get_resource(
        self, endpoint: str, id: str | int, ttl: int = 3600, **kwargs
    ) -> pd.DataFrame:
        """Gets all information about a specific resource in an endpoint

        Args:
            endpoint (str): Which endpoint to execute the API call against
            id (str | int): Either the ID or the name of the resource
            ttl (ttl_duration): The maximum time to keep an entry in the cache
            **kwargs: These are passed through to the requests.get method

        Raises:
            requests.HTTPError: Any HTTP error occured

        Returns:
            endpoints (dict): All information about the resource
        """

        @st.cache_data(ttl=ttl)
        def _request(endpoint: str, id: str | int, **kwargs) -> pd.DataFrame:
            session = self._instance
            path = [self.base_url, endpoint, str(id)]
            path = "/".join(path)
            res = session.get(path, **kwargs)
            res.raise_for_status()
            return res.json()

        return _request(endpoint, id, **kwargs)
