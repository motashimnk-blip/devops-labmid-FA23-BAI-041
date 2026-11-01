"""Automated tests for the assignment submission portal."""
import pytest

from portal import create_app, storage


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"
    app = create_app(db_path=str(db_file))
    app.config["TESTING"] = True
    with app.test_client() as c:
        c.db_path = str(db_file)
        yield c


VALID = {
    "name": "Mohtashim Nawaz Khan",
    "reg_no": "FA23-BAI-041",
    "title": "DevOps Lab Mid",
    "url": "https://github.com/example/devops-lab-mid",
}


def test_valid_submission_is_saved_and_listed(client):
    response = client.post("/submit", data=VALID, follow_redirects=True)

    assert response.status_code == 200
    saved = storage.list_submissions(client.db_path)
    assert len(saved) == 1
    assert saved[0]["reg_no"] == "FA23-BAI-041"
    # the new submission must appear in the list on the page
    page = response.get_data(as_text=True)
    assert "DevOps Lab Mid" in page
    assert "https://github.com/example/devops-lab-mid" in page


def test_missing_registration_number_is_rejected(client):
    data = dict(VALID, reg_no="")
    response = client.post("/submit", data=data)

    assert response.status_code == 400
    assert "Registration number is required." in response.get_data(as_text=True)
    assert storage.list_submissions(client.db_path) == []


def test_invalid_url_is_rejected_and_not_saved(client):
    data = dict(VALID, url="not-a-valid-link")
    response = client.post("/submit", data=data)

    assert response.status_code == 400
    assert "Submission URL is not valid" in response.get_data(as_text=True)
    assert storage.list_submissions(client.db_path) == []
