import requests
import logging
import json


class Handler(object):
    def __init__(self):
        """
        This class is used to handle interaction towards coffee interface.
        """
        super(Handler, self).__init__()
        logging.warning('Initializing coffeeHandler....')

        # get an active token and get prepared for sending request
        self.coffee_session = requests.session()

    def get_rsp_from_url(self, url, params=None, method='get', data=None):
        logging.warning('when using method {}, header is:\n {} \n data is: \n{}.\n'.
                        format(method, self.coffee_session.headers, data))
        rsp = None

        if 'get' == method:
            rsp = self.coffee_session.get(url, params=params, timeout=10)
        elif 'put' == method:
            rsp = self.coffee_session.put(url, data=json.dumps(data))
        elif 'post' == method:
            rsp = self.coffee_session.post(url, data=json.dumps(data))
        elif 'delete' == method:
            rsp = self.coffee_session.delete(url, data=json.dumps(data))
        else:
            assert 0, 'We only support get/post/put/delete for now!!!'

        logging.warning('\n\n#####\nget rsp from url: \n{} is :\n##### \n{}\n#####\n\ntext is: \n{}\n#####\n'.
                        format(url, repr(rsp), repr(rsp.text)))
        return rsp

    def check_rsp(self, origin_rsp, expected_rsp, check_format=False, check_partial_rsp=False, check_length=False,
                  check_format_ignore_list_length=False, check_format_null_str=False):

        if check_format:
            logging.warning('Now start to check format for origin_rsp and expected_rsp!')

            self._check_format(origin_rsp, expected_rsp, check_format_ignore_list_length, check_format_null_str)
        if check_partial_rsp:
            self._check_partial_rsp(expected_rsp, origin_rsp)
        if check_length is not False:
            for key, expected_length in check_length.iteritems():
                current_length = len(origin_rsp[key])
                assert expected_length == current_length, \
                    'We expect to see length of \'{}\' in origin_rsp is {}, but now it is {}'.format(
                        key, expected_length, current_length)
        if not any([check_format, check_partial_rsp, check_length]):
            sorted_expected_rsp = self._order_json(expected_rsp)
            sorted_origin_rsp = self._order_json(origin_rsp)
            logging.warning('\nWe expect to see \n\n{}, \n\nand we get \n\n{}.'.format(sorted_expected_rsp,
                                                                                       sorted_origin_rsp))
            assert sorted_expected_rsp == sorted_origin_rsp, \
                'We don\'t get the expected,please check the log'

        logging.warning('\033[0;32m check_rsp done!!! PASS\033[0m')

    def _check_format(self, origin_rsp, expected_rsp, check_format_ignore_list_length, check_format_null_str):

        logging.warning(u'now compare origin rsp: \n{}'.format(origin_rsp))
        logging.warning(u'\nAnd expected_rsp: \n{}'.format(expected_rsp))

        if isinstance(origin_rsp, dict) and isinstance(expected_rsp, dict):
            assert len(origin_rsp) == len(
                expected_rsp), 'Length of dict is not right! Please check the length.\norigin_rsp: ' \
                               '\n{}\nexpected_rsp: \n{}'.format(origin_rsp, expected_rsp)
            for key, value in origin_rsp.iteritems():
                assert expected_rsp.get(
                    key), 'In expected_rsp, there is no key: {} while there is in origin_rsp'.format(str(key))
                logging.warning(u'Check value for the same key: [{}] in origin_rsp and expected_rsp'.format(key))
                self._check_format(value, expected_rsp.get(key),
                                   check_format_ignore_list_length, check_format_null_str)
        elif isinstance(origin_rsp, list) and isinstance(expected_rsp, list):
            if expected_rsp:
                logging.warning('Length of list is not right! Please check the length.\norigin_rsp: \n{}\nexpected_rsp:'
                                ' \n{}'.format(origin_rsp, expected_rsp))
                if check_format_ignore_list_length:
                    for index in xrange(len(expected_rsp)):
                        self._check_format(origin_rsp[index], expected_rsp[index],
                                           check_format_ignore_list_length, check_format_null_str)
                else:
                    assert len(origin_rsp) == len(
                        expected_rsp), 'Length of list is not right! Please check the length.'

                    for index in xrange(len(origin_rsp)):
                        self._check_format(origin_rsp[index], expected_rsp[index],
                                           check_format_ignore_list_length, check_format_null_str)
            else:
                return True
        elif isinstance(origin_rsp, int) and isinstance(expected_rsp, int):
            return True
        elif isinstance(origin_rsp, float) and isinstance(expected_rsp, float):
            return True
        elif (isinstance(origin_rsp, str) or isinstance(origin_rsp, unicode)) and (
                    isinstance(expected_rsp, str) or isinstance(expected_rsp, unicode)):
            return True
        elif check_format_null_str:
            if origin_rsp is None and isinstance(expected_rsp, str):
                return True
            if origin_rsp is None and isinstance(expected_rsp, int):
                return True
        else:
            logging.warning(
                'Check format fail!!!! We get different value here!!\norigin_rsp: \n{}\nbut we expect to see in '
                'expected_rsp: \n{}'.format(origin_rsp, expected_rsp))
            assert 0, 'Check format fail!!!! We get different value here!!'

    def _order_json(self, json_string):
        """
        Return an ordered list for compare.
        :param json_string: string in json format
        :return: an ordered list
        """

        if isinstance(json_string, dict):
            return sorted((k, self._order_json(v)) for k, v in json_string.items())
        if isinstance(json_string, list):
            return sorted(self._order_json(x) for x in json_string)
        else:
            return json_string

    def _check_partial_rsp(self, exp, ori):
        """
        Check partial rsp but not the while rsp.
        :param exp: expected rsp
        :param ori: origin rsp
        :return: None
        """
        logging.warning('Start to check if expected_rsp: {} is part of origin_rsp: {}'.format(exp, ori))
        # so far, leaf node could be string or list which must be exactly the same

        if isinstance(exp, dict):
            for k, v in exp.iteritems():
                if ori.get(k):
                    self._check_partial_rsp(exp[k], ori[k])
                else:
                    assert 0, 'key \'{}\' does not exist in original response.'.format(k)
        elif isinstance(exp, list):
            for index in xrange(len(exp)):
                if isinstance(exp[index], dict):
                    self._assert_dict_contain(exp[index], ori[index])
                elif isinstance(exp[index], list):
                    self._check_partial_rsp(exp[index], ori[index])
                else:
                    assert exp[index] in ori, 'exp: {} does not in ori: {}'.format(exp[index], ori)
        else:
            assert exp == ori, 'exp: {} does not equal to ori: {}'.format(exp, ori)

    @staticmethod
    def _assert_dict_contain(subset_dict, whole_dict):
        logging.warning('subset_dict is {}, whole_dict is {}'.format(subset_dict, whole_dict))
        for key in subset_dict:
            if whole_dict.get(key):
                continue
            else:
                assert 0, '{} should be subset of {}, but now it is not!!'.format(subset_dict, whole_dict)
