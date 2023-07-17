import pytest
from django.urls import reverse


@pytest.fixture
@pytest.mark.django_db
def api_client(client, django_user_model):
    _ = django_user_model.objects.create_user(
        username="test_user", password="test_password"
    )
    client.login(username="test_user", password="test_password")
    return client


@pytest.mark.django_db
def test_unauthorized_request(client):
    url = reverse("table_create")
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_update_table(api_client, dummy_fields):
    url = reverse("table_create")
    data = {"name": "new_dummy_table_1", "fields": dummy_fields}
    response = api_client.post(url, data, content_type="application/json")
    assert response.status_code == 201

    result = response.json()
    assert result
    assert (
        result["id"] > 0
        and result["name"] == "new_dummy_table_1"
        and result["options"] is None
    )

    url = reverse("table_update", kwargs={"id": result["id"]})
    data["name"] = "updated_new_dummy_table_1"
    response = api_client.put(url, data, content_type="application/json")
    assert response.status_code == 200


def test_add_get_rows(api_client, dummy_fields):
    url = reverse("table_create")
    data = {"name": "new_dummy_table_1", "fields": dummy_fields[:2]}
    response = api_client.post(url, data, content_type="application/json")
    result = response.json()
    assert response.status_code == 201
    table_id = result["id"]

    url = reverse("table_create_rows", kwargs={"id": table_id})
    data = {
        "rows": [
            {"dummy_field_1": "ABC", "dummy_field_2": 123},
            {"dummy_field_1": "DEF", "dummy_field_2": 456},
        ]
    }
    response = api_client.post(url, data, content_type="application/json")
    assert response.status_code == 201
    result = response.json()
    assert len(result) == 2

    # retrieve table rows
    url = reverse("table_retrieve_rows", kwargs={"id": table_id})
    response = api_client.get(url)
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2

    for row in result:
        assert row["id"] > 0
        assert row["dummy_field_1"] in ("ABC", "DEF")
        assert row["dummy_field_2"] in (123, 456)
