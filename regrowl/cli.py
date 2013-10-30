from argparse import ArgumentParser
from ConfigParser import RawConfigParser
import logging
import os

from regrowl.server import GNTPServer


CONFIG_PATH = [
    os.path.expanduser('~/.regrowl'),
    '.regrowl'
    ]

DEFAULTS = {
    'regrowl.server':
    {
        'host': '0.0.0.0',
        'port': 12345,
        'password': None,
    }
}

class DefaultConfig(RawConfigParser):
    def __init__(self, *args, **kwargs):
        RawConfigParser.__init__(self, *args, **kwargs)
        
        for section in DEFAULTS:
            self.add_section(section)
            for (option, value) in DEFAULTS[section].items():
                self.set(section, option, value)

        self.get = self._wrap_default(self.get)
        self.getint = self._wrap_default(self.getint)
        self.getboolean = self._wrap_default(self.getboolean)

    def _wrap_default(self, function):
        def _wrapper(section, option, default=None):
            try:
                return function(section, option)
            except:
                return default
        return _wrapper


class ParserWithConfig(ArgumentParser):
    def __init__(self, *args, **kwargs):
        if 'config' in kwargs:
            config = kwargs['config']
            del kwargs['config']
        else:
            config = []
        ArgumentParser.__init__(self, *args, **kwargs)
        self.config = DefaultConfig()
        self.config.read(config)

    def add_default_option(self, *args, **kwargs):
        # Map the correct config.get* to the type of option being added
        fun = {
            int: self.config.getint,
            None: self.config.get,
        }.get(kwargs.get('type'))

        if 'section' in kwargs:
            kwargs['default'] = fun(kwargs.get('section'), kwargs.get('dest'))
            del kwargs['section']

        self.add_argument(*args, **kwargs)


def main():
    conf_parser = ParserWithConfig(config=CONFIG_PATH, add_help=False)
    conf_parser.add_argument(
        '-c', '--config',
        help='path to a regrowl configuration file',
        dest='config_path'
        )
    
    (options, remaining_args) = conf_parser.parse_known_args()
    if options.config_path is not None:
        conf_parser.config.read(options.config_path)

    parser = ParserWithConfig(
        config=options.config_path, 
        parents=[conf_parser]
        )

    parser.add_default_option(
        '-a', '--address',
        help='address to listen on',
        dest='host',
        section='regrowl.server'
        )
    parser.add_default_option(
        '-p', '--port',
        help='port to listen on',
        dest='port',
        type=int,
        section='regrowl.server'
        )
    parser.add_default_option(
        '-P', '--password',
        help='Network password',
        dest='password',
        section='regrowl.server'
        )

    # Debug Options
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        default=0,
        action='count',
        )
    parser.add_argument(
        '-d', '--debug',
        help='Print raw growl packets',
        dest='debug',
        action='store_true',
        default=False
        )
    parser.add_argument(
        '-q', '--quiet',
        help='Quiet mode',
        dest='debug',
        action='store_false'
        )

    (options, args) = parser.parse_known_args(remaining_args)
    options.verbose = logging.WARNING - options.verbose * 10

    try:
        import setproctitle
        setproctitle.setproctitle('regrowl-server')
    except ImportError:
        pass

    logging.basicConfig(level=options.verbose,
        format="%(name)-25s %(levelname)s:%(message)s")

    server = GNTPServer(options, parser.config)
    server.run()

if __name__ == '__main__':
    main()
