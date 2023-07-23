from itertools import chain
import streamlit as st
import requests
import pandas as pd
from streamlit.connections import ExperimentalBaseConnection
from dataclasses import dataclass


@dataclass
class ApiResponse:
    count: int
    next: str | None
    previous: str | None
    results: dict


class PokeApiConnection(ExperimentalBaseConnection[requests.Session]):
    base_url = "https://pokeapi.co/api/v2"

    def _connect(self, **kwargs) -> requests.Session:
        _ = kwargs
        return requests.session()

    def list_available_endpoints(self, ttl: int = 3600, **kwargs):
        @st.cache_data(ttl=ttl)
        def _request(**kwargs) -> pd.DataFrame:
            session = self._instance
            res = session.get(self.base_url, **kwargs)
            res.raise_for_status()
            return pd.DataFrame.from_dict(res.json(), orient="index")

        return _request(**kwargs)

    def list_available_resources(
        self, endpoint: str, ttl: int = 3600, **kwargs
    ) -> pd.DataFrame:
        @st.cache_data(ttl=ttl)
        def _request(endpoint: str, **kwargs) -> pd.DataFrame:
            session = self._instance
            path = [self.base_url, endpoint]
            path = "/".join(path)
            res = ApiResponse(**session.get(path, **kwargs).json())
            marker = res.next
            results = [res.results]
            while marker:
                res = ApiResponse(**session.get(marker, **kwargs).json())
                marker = res.next
                results.append(res.results)

            flat_results = chain.from_iterable(results)
            return pd.DataFrame(flat_results)

        return _request(endpoint, **kwargs)

    def query(
        self, endpoint: str, id: str | int, ttl: int = 3600, **kwargs
    ) -> pd.DataFrame:
        @st.cache_data(ttl=ttl)
        def _request(endpoint: str, id: str | int, **kwargs) -> pd.DataFrame:
            session = self._instance
            path = [self.base_url, endpoint, str(id)]
            path = "/".join(path)
            res = session.get(path, **kwargs)
            res.raise_for_status()
            return res.json()

        return _request(endpoint, id, **kwargs)
