import argparse
import os
import sys

import yaml


def _get_files(path):
    files = []

    for file_name in os.listdir(path):
        if not file_name.startswith('.'):
            if os.path.isfile(os.path.join(path, file_name)):
                files.append(file_name)

    return files


class PlayDB(object):
    def __init__(self):
        config_path = '{}/.cache/playnext'.format(os.getenv('HOME'))

        self._config = '{}/db.yml'.format(config_path)
        if not os.path.isfile(self._config):
            os.makedirs(config_path)
            yaml.safe_dump({}, open(self._config, 'w'))

        self._db = yaml.safe_load(open(self._config, 'r'))

    def __del__(self):
        yaml.safe_dump(
            self._db, open(self._config, 'w'), width=76,
            default_flow_style=False)

    def __contains__(self, key):
        return os.path.realpath(key) in self._db

    def __getitem__(self, key):
        return self._db[os.path.realpath(key)] if key in self else -1

    def __setitem__(self, key, value):
        self._db[os.path.realpath(key)] = value

    def __delitem__(self, key):
        if key in self:
            del self._db[os.path.realpath(key)]

    def add(self, path):
        self[path] = len(_get_files(path)) - 1

    def remove(self, path):
        del self[path]

    def set(self, path, value):
        self[path] = value

    def current(self, path):
        if self[path] < 0:
            return ''
        return sorted(_get_files(path), reverse=True)[self[path]]

    def next(self, path):
        self[path] = max(self[path] - 1, -1)


def add():
    PlayDB().add('.')


def remove():
    PlayDB().remove('.')


def set(value):
    PlayDB().set('.', value)


def current():
    print PlayDB().current('.')


def next():
    db = PlayDB()
    print db.current('.')
    db.next('.')


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='', epilog='')
    #parser.add_argument('-v', action='version', version=version(parser.prog))
    subparsers = parser.add_subparsers(dest='subcommand')

    subparsers.add_parser('add').set_defaults(func=add)
    subparsers.add_parser('remove').set_defaults(func=remove)
    subparsers.add_parser('set').set_defaults(func=set)
    subparsers.add_parser('current').set_defaults(func=current)
    subparsers.add_parser('next').set_defaults(func=next)

    args = parser.parse_args()

    args.func(**{k: v for k, v in vars(args).items()
        if k not in ('func', 'subcommand')})


if __name__ == '__main__':
    main()
