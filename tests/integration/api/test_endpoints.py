from fastapi.testclient import TestClient
from api.endpoints import app
from api.constants import DATA_ENDPOINT, DATA_INVALIDATION_REASONS_ENDPOINT

client = TestClient(app)


class TestEndpoints:
    @staticmethod
    def test_get_data_when_no_api_key_is_provided_is_not_successful():
        # Arrange

        # Act
        response = client.get(f"/{DATA_ENDPOINT}")

        # Assert
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Field required'
        assert response.json()['detail'][0]['loc'][1] == 'api-key'

    @staticmethod
    def test_get_data_when_valid_api_key_is_provided_is_successfull():
        # Arrange
        expected_keys = {"time", "value", "tags"}

        # Act
        response = client.get(f"/{DATA_ENDPOINT}", headers={"api-key": "user_api_key"})

        # Assert
        response_in_json = response.json()
        assert response.status_code == 200
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])

    @staticmethod
    def test_get_data_when_invalid_api_key_is_provided_raises_exception():
        # Arrange

        # Act
        response = client.get(f"/{DATA_ENDPOINT}", headers={"api-key": "invalid_api_key"})

        # Assert
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid API key'

    @staticmethod
    def test_get_discard_data_when_no_api_key_is_provided_is_not_successful():
        # Arrange

        # Act
        response = client.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}")

        # Assert
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Field required'
        assert response.json()['detail'][0]['loc'][1] == 'api-key'

    @staticmethod
    def test_get_discard_data_when_api_key_is_provided_but_is_not_from_admin_raises_exception():
        # Arrange

        # Act
        response = client.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}", headers={"api-key": "user_api_key"})

        # Assert
        assert response.status_code == 403
        assert response.json()['detail'] == "Insufficient permissions"

    @staticmethod
    def test_get_discard_data_when_api_key_is_provided_and_is_admin_is_successful():
        # Arrange
        expected_keys = {"time", "value", "tags", "reasons"}

        # Act
        response = client.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}", headers={"api-key": "admin_api_key"})

        # Assert
        response_in_json = response.json()
        assert response.status_code == 200
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])
            assert isinstance(element['reasons'], list) and all(isinstance(item, str) for item in element['reasons'])

    @staticmethod
    def test_get_data_only_start_time_given():
        # Arrange
        expected_keys = {"time", "value", "tags"}

        # Act
        response = client.get(f"/{DATA_ENDPOINT}?start_time=2024-04-01T00:00:00", headers={"api-key": "user_api_key"})

        # Assert
        assert response.status_code == 200
        response_in_json = response.json()
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])

    @staticmethod
    def test_get_data_only_end_time_given():
        # Arrange
        expected_keys = {"time", "value", "tags"}

        # Act
        response = client.get(f"/{DATA_ENDPOINT}?end_time=2024-04-02T00:00:00", headers={"api-key": "user_api_key"})

        # Assert
        assert response.status_code == 200
        response_in_json = response.json()
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])

    @staticmethod
    def test_get_data_both_start_and_end_time_given():
        # Arrange
        expected_keys = {"time", "value", "tags"}

        # Act
        response = client.get(f"/{DATA_ENDPOINT}?start_time=2024-04-01T00:00:00&end_time=2024-04-02T00:00:00",
                              headers={"api-key": "user_api_key"})

        # Assert
        assert response.status_code == 200
        response_in_json = response.json()
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])


    @staticmethod
    def test_get_discard_data_only_start_time_given():
        # Arrange
        expected_keys = {"time", "value", "tags", "reasons"}

        # Act
        response = client.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}?start_time=2024-04-01T00:00:00",
                              headers={"api-key": "admin_api_key"})

        # Assert
        assert response.status_code == 200
        response_in_json = response.json()
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])
            assert isinstance(element['reasons'], list) and all(isinstance(item, str) for item in element['reasons'])

    @staticmethod
    def test_get_discard_data_only_end_time_given():
        # Arrange
        expected_keys = {"time", "value", "tags", "reasons"}

        # Act
        response = client.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}?end_time=2024-04-02T00:00:00",
                              headers={"api-key": "admin_api_key"})

        # Assert
        assert response.status_code == 200
        response_in_json = response.json()
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])
            assert isinstance(element['reasons'], list) and all(isinstance(item, str) for item in element['reasons'])

    @staticmethod
    def test_get_discard_data_both_start_and_end_time_given():
        # Arrange
        expected_keys = {"time", "value", "tags", "reasons"}

        # Act
        response = client.get(f"/{DATA_INVALIDATION_REASONS_ENDPOINT}?"
                              f"start_time=2024-04-01T00:00:00&end_time=2024-04-02T00:00:00",
                              headers={"api-key": "admin_api_key"})

        # Assert
        assert response.status_code == 200
        response_in_json = response.json()
        assert isinstance(response_in_json, list)
        for element in response_in_json:
            assert set(element.keys()) == expected_keys
            assert type(element["time"]) == str
            assert isinstance(element['value'], float)
            assert isinstance(element['tags'], list) and all(isinstance(item, str) for item in element['tags'])
            assert isinstance(element['reasons'], list) and all(isinstance(item, str) for item in element['reasons'])
