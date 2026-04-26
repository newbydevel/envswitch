import pytest
from envswitch.tag import add_tag, remove_tag, list_tags, find_profiles_by_tag, TagError
from envswitch.storage import save_profiles


@pytest.fixture
def tmp_store(tmp_path):
    path = tmp_path / "profiles.json"
    profiles = {
        "dev": {"DB_HOST": "localhost"},
        "prod": {"DB_HOST": "prod.db"},
        "staging": {"DB_HOST": "staging.db", "__tags__": ["preexisting"]},
    }
    save_profiles(profiles, path)
    return path


def test_add_tag_success(tmp_store):
    tags = add_tag("dev", "backend", store_path=tmp_store)
    assert "backend" in tags


def test_add_tag_persists(tmp_store):
    add_tag("dev", "backend", store_path=tmp_store)
    assert "backend" in list_tags("dev", store_path=tmp_store)


def test_add_tag_duplicate_raises(tmp_store):
    add_tag("dev", "backend", store_path=tmp_store)
    with pytest.raises(TagError, match="already exists"):
        add_tag("dev", "backend", store_path=tmp_store)


def test_add_tag_nonexistent_profile_raises(tmp_store):
    with pytest.raises(TagError, match="not found"):
        add_tag("ghost", "mytag", store_path=tmp_store)


def test_remove_tag_success(tmp_store):
    add_tag("dev", "backend", store_path=tmp_store)
    tags = remove_tag("dev", "backend", store_path=tmp_store)
    assert "backend" not in tags


def test_remove_tag_not_present_raises(tmp_store):
    with pytest.raises(TagError, match="not found"):
        remove_tag("dev", "nonexistent", store_path=tmp_store)


def test_remove_tag_nonexistent_profile_raises(tmp_store):
    with pytest.raises(TagError, match="not found"):
        remove_tag("ghost", "mytag", store_path=tmp_store)


def test_list_tags_empty(tmp_store):
    assert list_tags("dev", store_path=tmp_store) == []


def test_list_tags_with_preexisting(tmp_store):
    assert list_tags("staging", store_path=tmp_store) == ["preexisting"]


def test_list_tags_nonexistent_profile_raises(tmp_store):
    with pytest.raises(TagError, match="not found"):
        list_tags("ghost", store_path=tmp_store)


def test_find_profiles_by_tag(tmp_store):
    add_tag("dev", "backend", store_path=tmp_store)
    add_tag("prod", "backend", store_path=tmp_store)
    results = find_profiles_by_tag("backend", store_path=tmp_store)
    assert set(results) == {"dev", "prod"}


def test_find_profiles_by_tag_no_match(tmp_store):
    results = find_profiles_by_tag("nonexistent", store_path=tmp_store)
    assert results == []


def test_find_profiles_by_tag_preexisting(tmp_store):
    results = find_profiles_by_tag("preexisting", store_path=tmp_store)
    assert results == ["staging"]
