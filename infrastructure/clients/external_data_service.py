import requests
from fastapi import HTTPException


class ExternalDataService:
    @staticmethod
    def fetch_data_from_server():
        url = "http://localhost:28462"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch data from server")
