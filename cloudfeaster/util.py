import base64
import mimetypes
import os


def file_to_data_uri_scheme(filename):
    # https://en.wikipedia.org/wiki/Data_URI_scheme
    # data:[<media type>][;base64],<data>

    if not filename:
        return None

    if not os.path.isfile(filename):
        return None

    with open(filename, 'rb') as f:
        file_contents = f.read()
        if not file_contents:
            return None

        return 'data:{mime_type};base64,{data}'.format(
            mime_type=mimetypes.guess_type(filename)[0],
            data=base64.b64encode(file_contents).decode('utf-8'))
