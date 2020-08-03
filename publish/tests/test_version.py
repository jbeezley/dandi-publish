from django.core.exceptions import ValidationError
import pytest

from publish.models import Version
from .fuzzy import TIMESTAMP_RE


@pytest.mark.django_db
def test_version_make_version_nosave(dandiset):
    # Without saving, the output should be reproducible
    version_str_1 = Version.make_version(dandiset)
    version_str_2 = Version.make_version(dandiset)
    assert version_str_1 == version_str_2


@pytest.mark.django_db
def test_version_make_version_save(mocker, dandiset, version_factory):
    # Given an existing version at the current time, a different one should be allocated
    make_version_spy = mocker.spy(Version, 'make_version')
    version_1 = version_factory(dandiset=dandiset)
    make_version_spy.assert_called_once()

    version_str_2 = Version.make_version(dandiset)
    assert version_1.version != version_str_2


@pytest.mark.django_db
def test_version_from_girder(dandiset_factory, mock_girder_client):
    dandiset = dandiset_factory(draft_folder_id='magic_draft_folder_id')
    version = Version.from_girder(dandiset, mock_girder_client)
    assert version


@pytest.mark.django_db
def test_version_from_girder_no_metadata(dandiset, mock_girder_client):
    # this test relies on DandisetFactory producing a dandiset with a draft_folder_id
    # that is considered invalid when used with Version.from_girder and the mocked
    # girder client.
    with pytest.raises(ValidationError, match='has no "meta" field.'):
        Version.from_girder(dandiset, mock_girder_client)


@pytest.mark.django_db
def test_version_rest_list(api_client, version):
    assert api_client.get(f'/api/dandisets/{version.dandiset.identifier}/versions/').data == {
        'count': 1,
        'next': None,
        'previous': None,
        'results': [
            {
                'dandiset': {
                    'identifier': version.dandiset.identifier,
                    'created': TIMESTAMP_RE,
                    'updated': TIMESTAMP_RE,
                },
                'version': version.version,
                'name': version.name,
                'description': version.description,
                'created': TIMESTAMP_RE,
                'updated': TIMESTAMP_RE,
                'count': 0,
            }
        ],
    }


@pytest.mark.django_db
def test_version_rest_retrieve(api_client, version):
    assert api_client.get(
        f'/api/dandisets/{version.dandiset.identifier}/versions/{version.version}/'
    ).data == {
        'dandiset': {
            'identifier': version.dandiset.identifier,
            'created': TIMESTAMP_RE,
            'updated': TIMESTAMP_RE,
        },
        'version': version.version,
        'name': version.name,
        'description': version.description,
        'created': TIMESTAMP_RE,
        'updated': TIMESTAMP_RE,
        'count': 0,
        'metadata': version.metadata,
    }
