# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from __future__ import print_function

import argparse
import json
import re

from engine.fuzzing_parameters.fuzzing_utils import *

class ResponseTracker():
    """ Response tracker for error code and error message """

    def __init__(self, ignore, verbose=False, LOG=print):
        """ Initialize the tracker

        @param LOG: Customized log
        @type  LOG: Function

        @return: None
        @rtype:  None

        """
        self._log = LOG
        self._codes = {}
        self._valid_cnt = 0
        self._invalid_cnt = 0
        self._ignore = ignore
        self._verbose = verbose

    @property
    def num_requests(self):
        """ Return the total number of responses received

        @return: Total number of responses
        @rtype:  Int

        """
        return self._valid_cnt + self._invalid_cnt

    @property
    def num_error_codes(self):
        """ Return the number of different error code/message

        @return: Number of different error code/message
        @rtype:  Int

        """
        return sum(len(self._codes[c]) for c in self._codes)

    @property
    def num_valid(self):
        """ Return the number of valid responses

        @return: Number of valid responses
        @rtype:  Int

        """
        return self._valid_cnt

    def process_response(self, response, test_round=None):
        """ Process a response

        @param response: Server's response
        @type  response: HttpResponse

        @return: None
        @rtype:  None

        """
        # valid response are not handled for now
        if response.has_valid_code():
            self._valid_cnt += 1
            return None

        self._invalid_cnt += 1

        # try to get response body (JSON)
        body = get_response_body(response.to_str)

        if test_round:
            status_code = f'{test_round}_{status_code}'
        else:
            status_code = response.status_code

        if body:
            self._process_json_error_response(body, response)
        else:
            self._process_other_error_response(response.to_str, status_code)

    def _process_json_error_response(self, body, response):
        """ Process the body of an invalid response

        @param body: Response body
        @type  body: String
        @param response: Server's response
        @type  response: HttpResponse

        @return: None
        @rtype:  None

        """
        # get the error code and error message
        error = body['error'] if 'error' in body else body
        if ('code' not in error) or ('message' not in error):
            self._update_record('misc', error)
            return None

        if response.has_bug_code():
            message = error['message'].split('timestamp')[0]
        else:
            message = error['message']

        # update tracker
        code = '{0}_{1}'.format(response.status_code, error['code'])
        self._update_record(code, message)

    def _process_other_error_response(self, response, status_code):
        """ Try to process unexpected response

        @param response: Response
        @type  response: String
        @param status_code: Status code
        @type  status_code: String

        @return: None
        @rtype:  None

        """
        # try if is XML
        xml_body_start = response.find('<body>')
        xml_body_end = response.find('</body>')
        if (
            xml_body_start != -1
            and xml_body_end != -1
            and xml_body_end > xml_body_start
        ):
            xml_body = response[xml_body_start:xml_body_end]
            self._update_record(f'{status_code}_XML', xml_body)
            return

        # don't know
        self._update_record(f'{status_code}_UnknownResponse', response)

    def _update_record(self, code, msg):
        """ Update the tracker record

        @param code: Error code
        @type  code: String
        @param msg: Error message
        @type  msg: String

        @return: None
        @rtype:  None

        """
        msg = self._get_message_hash(msg)

        if code in self._codes:
            if msg in self._codes[code]:
                self._codes[code][msg] += 1
            else:
                self._codes[code][msg] = 1
        else:
            self._codes[code] = {msg: 1}

    def _get_message_hash(self, msg):
        """ Sanitize the message and return the hash

        @param msg: Error message
        @type  msg: String

        @return: Hash
        @rtype:  Int

        """
        # make sure it's string
        msg = str(msg)

        # remove ignores
        if self._ignore:
            for keyword in self._ignore:
                msg = msg.replace(keyword, '?')

        # replace guid with '?'
        guids = re.findall('[0-9a-f]{10}', msg)
        for guid in guids:
            msg = msg.replace(guid, '?')

        # replace numbers
        msg = replace_number_chunks(msg, '?')

        # hash
        return msg if self._verbose else hash(msg)

    def show(self, msg=''):
        """ Print out the tracker statistics

        @param msg: Additional message to print along with the statistics
        @type  msg: String

        @return: None
        @rtype:  None

        """
        self._log(f'Tracker begin ({msg}):')
        self._log(f'    Valid: {self._valid_cnt}')
        self._log(f'    Invalid: {self._invalid_cnt}')
        for c in self._codes:
            detail = ''
            total = 0
            for msg in self._codes[c]:
                cnt = self._codes[c][msg]
                detail += f' {cnt}'
                total += cnt
            desp = f'{total}:{detail}'
            self._log(f'    {c}: {len(self._codes[c])} ({desp})')
        self._log('Tracker end')

    def show_detail(self, msg=''):
        """ Print out the tracker statistics in detail

        @param msg: Additional message to print along with the statistics
        @type  msg: String

        @return: None
        @rtype:  None

        """
        self._log(f'Tracker begin ({msg}):')
        self._log(f'    Valid: {self._valid_cnt}')
        self._log(f'    Invalid: {self._invalid_cnt}')
        for c in self._codes:
            total = 0
            self._log(f'    {c}: {len(self._codes[c])}')
            for msg in self._codes[c]:
                cnt = self._codes[c][msg]
                detail = f'      ({cnt}) {msg}'
                self._log(detail)
                total += cnt
            self._log(f'      Total: {total}')

        self._log('Tracker end')
