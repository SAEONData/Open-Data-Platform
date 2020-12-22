import json
import requests
import xmltodict

from odp.lib.exceptions import MediaRepositoryError


class MediaRepoClient:

    def __init__(
            self,
            media_repo_url: str,
            username: str,
            password: str,
    ):
        self.media_repo_url = media_repo_url
        self.username = username
        self.password = password

    def flatten_dict_to_list(self, input_dict):
        curr_keys = input_dict.keys()
        values = []
        for k in curr_keys:
            if type(input_dict[k]) == dict:
                next_vals = self.flatten_dict_to_list(input_dict[k])
                modfied_next_vals = []

                for item in next_vals:
                    new_dict = {}
                    for next_k in item.keys():
                        new_dict["{}, {}".format(k, next_k)] = item[next_k]
                    modfied_next_vals.append(new_dict)
                values = values + modfied_next_vals
            else:
                values.append({k: input_dict[k]})
        return values

    def get_download_link(self, file_path: str) -> str:
        """
        Fetch a file download link from the media repository.
        """
        # print("trying to retrieve {}".format(file_path))
        data_str = {"OCS-APIRequest": "true"}
        auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        api_path = 'ocs/v2.php/apps/files_sharing/api/v1/shares?path='
        url = self.media_repo_url + api_path + file_path
        response = requests.get(url, headers=data_str, auth=auth)

        if response.status_code != 200:
            error_str = "Media repository error {}".format(response.status_code)
            if response.status_code == 404:
                error_str = "Requested file {} does not exist".format(file_path)
            raise MediaRepositoryError(status_code=response.status_code, error_detail=error_str)
        else:
            # print(response)
            response_json = json.loads(json.dumps(xmltodict.parse(response.text)))
            values = self.flatten_dict_to_list(response_json)

            url_key = 'ocs, data, element, url'
            download_link = None
            # print(response.text)
            for val in values:
                if url_key in val:
                    download_link = val[url_key] + '/download'
                    break
            if download_link:
                # print("returning {}".format(download_link))
                return download_link
            else:
                raise MediaRepositoryError(status_code=404,
                                           error_detail="Requested file {} not available for download.".format(
                                               file_path))
