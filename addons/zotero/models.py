# -*- coding: utf-8 -*-

from addons.base.models import BaseCitationsNodeSettings, BaseOAuthUserSettings
from django.db import models
from framework.exceptions import HTTPError
from pyzotero import zotero, zotero_errors
from addons.zotero import \
    settings  # TODO: Move `settings` to `apps.py` when deleting
from addons.zotero.serializer import ZoteroSerializer
from website.citations.providers import CitationsOauthProvider

# TODO: Don't cap at 200 responses. We can only fetch 100 citations at a time. With lots
# of citations, requesting the citations may take longer than the UWSGI harakiri time.
# For now, we load 200 citations max and show a message to the user.
MAX_CITATION_LOAD = 200

class Zotero(CitationsOauthProvider):
    name = 'Zotero'
    short_name = 'zotero'
    _oauth_version = 1

    client_id = settings.ZOTERO_CLIENT_ID
    client_secret = settings.ZOTERO_CLIENT_SECRET

    auth_url_base = 'https://www.zotero.org/oauth/authorize'
    callback_url = 'https://www.zotero.org/oauth/access'
    request_token_url = 'https://www.zotero.org/oauth/request'
    default_scopes = ['all']

    serializer = ZoteroSerializer

    def handle_callback(self, response):

        return {
            'display_name': response['username'],
            'provider_id': response['userID'],
            'profile_url': 'https://zotero.org/users/{}/'.format(
                response['userID']
            ),
        }

    def _get_folders(self, library_id=None):
        """Get a list of a user's folders"""
        client = self._get_group(library_id)

        # Note: Pagination is the only way to ensure all of the collections
        #       are retrieved. 100 is the limit per request. This applies
        #       to Mendeley too, though that limit is 500.
        return client.collections(limit=100)

    def _get_group(self, group_id):
        if group_id and group_id != 'personal':
            return zotero.Zotero(str(group_id), 'group', self.account.oauth_key)
        else:
            return self._get_client()

    def _get_client(self):
        return zotero.Zotero(self.account.provider_id, 'user', self.account.oauth_key)

    def _verify_client_validity(self):
        # Check if Zotero can be accessed with current credentials
        try:
            self._client.collections()
        except zotero_errors.PyZoteroError as err:
            self._client = None
            if isinstance(err, zotero_errors.UserNotAuthorised):
                raise HTTPError(403)
            else:
                raise err

    def _fetch_groups(self):
        """ Retrieves the Zotero group data to which the current library_id and api_key has access """
        groups = self.client.groups()
        return groups

    def _folder_metadata(self, folder_id, library_id=None):
        client = self._get_group(library_id)
        collection = client.collection(folder_id)
        return collection

    def _library_metadata(self, library_id):
        for library in self.client.groups():
            if str(library['id']) == library_id:
                return library
        return None

    def _citations_for_folder(self, list_id, library_id=None):
        """Get all the citations in a specified collection

        :param  str list_id: ID for a Zotero collection.
        :return list of csljson objects representing documents.
        """
        client = self._get_group(library_id)

        citations = []
        more = True
        offset = 0
        while more and len(citations) <= MAX_CITATION_LOAD:
            page = client.collection_items(list_id, content='csljson', limit=100, start=offset)
            citations = citations + page
            if len(page) == 0 or len(page) < 100:
                more = False
            else:
                offset = offset + len(page)
        return citations

    def _citations_for_user(self, library_id=None):
        """Get all the citations from the user """
        citations = []
        more = True
        offset = 0
        client = self._get_group(library_id)

        while more and len(citations) <= MAX_CITATION_LOAD:
            page = client.items(content='csljson', limit=100, start=offset)
            citations = citations + page
            if len(page) == 0 or len(page) < 100:
                more = False
            else:
                offset = offset + len(page)
        return citations

    @property
    def auth_url(self):
        url = super(Zotero, self).auth_url
        return url + '&all_groups=read'


class UserSettings(BaseOAuthUserSettings):
    oauth_provider = Zotero
    serializer = ZoteroSerializer


class NodeSettings(BaseCitationsNodeSettings):
    provider_name = 'zotero'
    oauth_provider = Zotero
    serializer = ZoteroSerializer
    user_settings = models.ForeignKey(UserSettings, null=True, blank=True)

    list_id = models.TextField(blank=True, null=True)
    library_id = models.TextField(blank=True, null=True)
    _api = None

    @property
    def fetch_library_name(self):
        """Returns a displayable library name"""
        if self.library_id is None:
            return ''
        else:
            library = self.api._library_metadata(self.library_id)
            return library['data'].get('name') if library else "Personal library"

    @property
    def _fetch_folder_name(self):
        folder = self.api._folder_metadata(self.list_id, self.library_id)
        return folder['data'].get('name')

    @property
    def fetch_groups(self):
        return self.api._fetch_groups()
