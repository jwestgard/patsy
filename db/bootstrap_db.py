#!/usr/bin/env python3

import csv
from io import StringIO
import os
import re
import sqlite3
import sys
import tarfile
import yaml

configfile = os.path.abspath(sys.argv[1])
rootdir = os.path.split(configfile)[0]

class Batch(list):
    def __init__(self, info, content):
        self.filepath = info.name
        self.filename = self.filepath.split('/')[-1]
        self.date = info.mtime
        delimiter = '\t' if '\t' in content.readline() else ','
        content.seek(0)
        self.extend(
            [row for row in csv.DictReader(content, delimiter=delimiter)]
            )

    def create_db_entry(self, cursor):
        query =  '''INSERT INTO batches (filename, date) 
                    VALUES ("{filename}", "{date}")'''.format(**self.__dict__)
        cursor.execute(query)
        self.id = cursor.lastrowid


class Asset:
    def __init__(self, **kwargs):
        kwargs = {key.upper(): value for key, value in kwargs.items()}
        self.bytes  = kwargs.get('BYTES', None)
        self.md5    = kwargs.get('MD5', None)
        if self.md5 is None:
            self.md5 = kwargs.get('OTHER', None)
        self.sha1   = kwargs.get('SHA1', None)
        self.sha256 = kwargs.get('SHA256', None)

    def create(self, cursor):
        selectq = '''SELECT id FROM assets WHERE md5 = "{md5}" 
                     and bytes = "{bytes}"'''.format(**self.__dict__)
        insertq = '''INSERT INTO assets (bytes, md5, sha1, sha256)
                     VALUES ("{bytes}", "{md5}", "{sha1}", "{sha256}"
                     )'''.format(**self.__dict__)
        results = cursor.execute(selectq).fetchall()
        if len(results) == 1:
            self.id = results[0]
        elif not results:
            cursor.execute(insertq)
            self.id = cursor.lastrowid


class File:
    def __init__(self, **kwargs):
        pass

    def create(self, cursor):
        insertq =  '''INSERT INTO instances (filename, batch_id, asset_id)
                      VALUES ("{0}", {1}, {2})'''.format(self.filename, batch_id, asset_id)


def main():
    print('Reading configuration from {0}...'.format(configfile))
    with open(configfile) as handle:
        config = yaml.safe_load(handle)

    datapath = os.path.abspath(os.path.join(rootdir, config['SOURCE_DATA']))
    patterns = [re.compile(pattern) for pattern in config['PATTERNS']]
    conn = sqlite3.connect(
        os.path.abspath(os.path.join(rootdir, config['DB_FILE']))
        )
    cursor = conn.cursor()

    archive = tarfile.open(datapath, 'r:gz')
    for f in [obj for obj in archive if obj.isfile()]:
        filename = os.path.basename(f.name)
        if not filename.startswith('.'):
            for pattern in patterns:
                match = pattern.match(filename)
                if match:
                    print('Processing {0}...'.format(filename))
                    content = StringIO(archive.extractfile(f).read().decode())
                    b = Batch(f, content)
                    b.create_db_entry(cursor)
                    for row in b:
                        a = Asset(**row)
                        a.create(cursor)
                        print(a.id)
                        f = File(**row)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()

