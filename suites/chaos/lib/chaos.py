# coding:utf-8

from utils.handler import Handler
import yaml
import os


class Chaos(object):
    def __init__(self):
        self.url = None
        self.method = None
        self.params = None
        self.data = None
        self.rsp = None
        self.handler = Handler()

    def run(self, test_suite):
        if test_suite.get('test_case') and test_suite.get('test_path'):
            for test_file in test_suite['test_case']:
                path_for_yaml = os.path.join(test_suite['test_path'], test_file)
                test_info = yaml.load(open(path_for_yaml))
                for key in test_info:
                    test_step = test_info[key]
                    if test_step.get('url'):
                        self.url = test_step['url']

                        if test_step.get('method'):
                            self.method = test_step['method']

                        if test_step.get('params'):
                            self.params = test_step['params']

                        if test_step.get('data'):
                            self.data = test_step['data']

                        self.rsp = self.handler.get_rsp_from_url(url=self.url,
                                                                 params=self.params,
                                                                 method=self.method,
                                                                 data=self.data)

                    if test_step.get('check_rsp_code'):
                        assert test_step.get('check_rsp_code') == self.rsp.status_code, 'code error'

                    if test_step.get('check_rsp'):
                        self.handler.check_rsp(self.rsp.json(), test_step.get('check_rsp'),
                                               check_format=test_step.get('check_format', False),
                                               check_format_ignore_list_length=test_step.get(
                                                   'check_format_ignore_list_length', False),
                                               check_partial_rsp=test_step.get('check_partial_rsp', False),
                                               check_length=test_step.get('check_length', False), )
        else:
            print 'have no file'
