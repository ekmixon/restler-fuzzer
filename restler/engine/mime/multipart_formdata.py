# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

""" Handling of multipart/form-data MIME type. """
import time


def render(payloads):
    """ Render multipart/form-data MIME type.

    @param payloads: The payload to render according to the MIME type.
    @type payloads: Str

    @return: The properly rendered payload.
    @rtype : String

    Note: To understand why we iterate over multipart/formdata like this one
    should first take a look at this example:
        https://stackoverflow.com/questions/4526273/what-does-enctype-multipart-form-data-mean
    and then read the correspinding RFC:
        https://www.ietf.org/rfc/rfc2388.txt

    Overall, there is nothing exotic here but one needs to be careful
    positioning the delimiters and the proper structure and headers.

    payloads may contain an arbitrary number of content-disposition and
    datasteam path dictionaries, as follows:

    payloads = [
      {
          'content-disposition': 'name="file"; filename="bla1.gz"',
          'datastream': 'bla.gz'
      },
      {
          'content-disposition': 'name="file"; filename="bla2.gz"',
          'datastream': 'bla2.gz'
      },
      ...
    ]

    """
    boundary = f"_CUSTOM_BOUNDARY_{int(time.time())}"

    req = f"Content-Type: multipart/form-data; boundary={boundary}\r\n\r\n"
    req += f'--{boundary}\r\n'

    for i, payload in enumerate(payloads):
        req += f"Content-Disposition: form-data; {payload['content-disposition']}\r\n"
        req += f'Content-Type: application/octet-stream\r\n\r\n'
        try:
            with open(payload['datastream'], 'r') as f:
                data = f.read()
        except Exception as error:
            print(f"Unhandled exception reading stream. Error:{error}")
            raise
        req += f'{data}\r\n\r\n'
        if i == len(payloads) - 1:
            req += f'--{boundary}--\r\n'
        else:
            req += f'--{boundary}\r\n\r\n'

    return req
