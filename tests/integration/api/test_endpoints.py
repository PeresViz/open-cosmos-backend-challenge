from fastapi.testclient import TestClient
from api.endpoints import app

client = TestClient(app)


class TestEndpoints:
    @staticmethod
    def test_get_data_when_no_api_key_is_provided_is_not_successful():
        # Arrange

        # Act
        response = client.get("/data")

        # Assert
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Field required'
        assert response.json()['detail'][0]['loc'][1] == 'api_key'

    @staticmethod
    def test_get_data_when_valid_api_key_is_provided_is_successfull():
        # Arrange
        expected_keys = {"time", "value", "tags"}

        # Act
        response = client.get("/data?api_key=user_api_key")

        # Assert
        response_in_json = response.json()
        assert response.status_code == 200
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], list) and all(isinstance(item, int) for item in element['value'])
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])

    @staticmethod
    def test_get_data_when_invalid_api_key_is_provided_raises_exception():
        # Arrange

        # Act
        response = client.get("/data?api_key=invalid_api_key")

        # Assert
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid API key'

    @staticmethod
    def test_get_discard_data_when_no_api_key_is_provided_is_not_successful():
        # Arrange

        # Act
        response = client.get("/discard_reasons")

        # Assert
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Field required'
        assert response.json()['detail'][0]['loc'][1] == 'api_key'

    @staticmethod
    def test_get_discard_data_when_api_key_is_provided_but_is_not_from_admin_raises_exception():
        # Arrange

        # Act
        response = client.get("/discard_reasons?api_key=user_api_key")

        # Assert
        assert response.status_code == 403
        assert response.json()['detail'] == "Insufficient permissions"

    @staticmethod
    def test_get_discard_data_when_api_key_is_provided_and_is_admin_is_successful():
        # Arrange
        expected_keys = {"time", "reasons"}

        # Act
        response = client.get("/discard_reasons?api_key=admin_api_key")

        # Assert
        response_in_json = response.json()
        assert response.status_code == 200
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['reasons'], list) and all(isinstance(item, str) for item in element['reasons'])
