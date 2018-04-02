import requests
import cgi


def get_dropbox_file(url):
    response = requests.get(url)
    value, params = cgi.parse_header(response.headers['content-disposition'])

    return {
        'blob': response.content,
        'name': params['filename'],
        'mime': response.headers['content-type'],
    }


def get_drive_file(file_id, token):
    headers = {'Authorization': 'Bearer %s' % token}
    metadata_url = "https://www.googleapis.com/drive/v2/files/%s" % file_id
    metadata = requests.get(metadata_url, headers=headers).json()

    file_url = metadata['downloadUrl']

    return {
        'blob': requests.get(file_url, headers=headers).content,
        'name': metadata['originalFilename'],
        'mime': metadata['mimeType'],
    }
