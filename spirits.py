import os
from optparse import OptionParser
import yaml
import sys


def parser_option():
    parser = OptionParser()
    parser.add_option(
        '-r', '--rebot',
        dest='test_suite_rebot',
        help='select yaml file or robot file', )
    (options, args) = parser.parse_args()
    return options, args


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    options, args = parser_option()
    if options.test_suite_rebot:
        test_suite = yaml.load(open(options.test_suite_rebot))
        map(__import__, [test_suite['test_module']])
        ts_class = getattr(sys.modules[test_suite['test_module']], test_suite['test_class'])
        ts_run = ts_class()
        ts_run.run(test_suite)


if __name__ == '__main__':
    main()
