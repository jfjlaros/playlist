import argparse
import os
import sys

import yaml


class PlayDB(object):
    def __init__(self):
        config_path = '{}/.cache/playnext'.format(os.getenv('HOME'))

        self._config = '{}/db.yml'.format(config_path)
        if not os.path.isfile(self._config):
            os.makedirs(config_path)
            yaml.safe_dump({}, open(self._config, 'w'))

        self._db = yaml.safe_load(open(self._config, 'r'))

        self._path = os.path.realpath('.')
        if self._path not in self._db:
            self._db[self._path] = {'files': [], 'offset': 0}

        self._item = self._db[self._path]

    def __del__(self):
        yaml.safe_dump(
            self._db, open(self._config, 'w'), width=76,
            default_flow_style=False)

    def _overflow(self):
        return self._item['offset'] >= len(self._item['files'])

    def add(self, files):
        for file_name in files:
            if not file_name.startswith('.') and os.path.isfile(file_name):
                if file_name not in self._item['files']:
                    self._item['files'].append(file_name)

    def remove(self, files):
        for index, file_name in enumerate(self._item['files']):
            if file_name in files:
                self._item['files'].pop(index)
                if index < self._item['offset']:
                    self._item['offset'] -= 1

    def set(self, filename):
        for index, file_name in enumerate(self._item['files']):
            if file_name == filename:
                self._item['offset'] = index
                return

    def current(self):
        if self._overflow():
            return ''
        return self._item['files'][self._item['offset']]

    def next(self):
        if self._overflow():
            return
        self._item['offset'] += 1

    def show(self):
        for index, file_name in enumerate(self._item['files']):
            spacer = ' '
            if index == self._item['offset']:
                spacer = '*'
            print '{} {}'.format(spacer, file_name)


def add(files):
    PlayDB().add(files)


def remove(files):
    PlayDB().remove(files)


def set(filename):
    PlayDB().set(filename)


def current():
    print PlayDB().current()


def next():
    db = PlayDB()
    print db.current()
    db.next()


def show():
    PlayDB().show()


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='', epilog='')
    #parser.add_argument('-v', action='version', version=version(parser.prog))
    subparsers = parser.add_subparsers(dest='subcommand')

    subparser = subparsers.add_parser('add')
    subparser.add_argument('files', metavar='FILE', type=str, nargs='+')
    subparser.set_defaults(func=add)

    subparser = subparsers.add_parser('remove')
    subparser.add_argument('files', metavar='FILE', type=str, nargs='+')
    subparser.set_defaults(func=remove)

    subparser = subparsers.add_parser('set')
    subparser.add_argument('filename', metavar='FILE', type=str)
    subparser.set_defaults(func=set)

    subparser = subparsers.add_parser('current')
    subparser.set_defaults(func=current)

    subparser = subparsers.add_parser('next')
    subparser.set_defaults(func=next)

    subparser = subparsers.add_parser('show')
    subparser.set_defaults(func=show)

    args = parser.parse_args()

    args.func(**{k: v for k, v in vars(args).items()
        if k not in ('func', 'subcommand')})


if __name__ == '__main__':
    main()
