# vim: fileencoding=utf-8 tw=100 expandtab ts=4 sw=4 :
#
# (c) 2015 ActivKonnect

from __future__ import unicode_literals


import hashlib
import os
import sqlite3
import fcntl
import errno
import time
from collections import namedtuple

FileInfoData = namedtuple('FileInfoData', ['size', 'last_access'])


class Pycachu(object):
    def __init__(self, root, max_storage):
        """
        Initializes Pycachu

        :param root: path to the root cache directory
        :param max_storage: size in octets that the cache should take at most on disk
        :return:
        """
        self.root = root
        self.max_storage = max_storage
        self.db = self.init_db(os.path.join(root, 'index.db'))

    def get(self, x, y, zoom):
        """
        Returns a file object for that key, or None if the object isn't in the cache.
        :param key:
        :return:
        """
        try:
            f = open(self.make_path(x, y, zoom), 'rb')
            fcntl.lockf(f, fcntl.LOCK_SH)
            key = '%d.%d.%d' % (x, y, zoom)

            c = self.db.cursor()
            c.execute(
                '''UPDATE "file" SET last_access = ? WHERE key = ?''',
                (int(time.time()), key)
            )
            self.db.commit()

            return f
        except IOError:
            return None

    def put(self, x, y, zoom, content, commit=True):
        h = self.hash(x, y, zoom)
        p = self.make_path(h)
        f = self.safe_create(p)

        if f is None:
            return

        f.write(content.read())
        f.close()

        s = os.stat(p)
        size = s.st_blocks * 512  # This is a magic number from the doc. I hope it's right.

        key = '%d.%d.%d' % (x, y, zoom)

        c = self.db.cursor()
        c.execute('''
          INSERT INTO "file" ("key", "size", "last_access")
          VALUES (?, ?, ?, ?)
        ''', (key, size, int(time.time())))
        self.trim_cache(commit=False)

        if commit:
            self.db.commit()

    def trim_cache(self, commit=True):
        made_changes = False

        while self.cache_size > self.max_storage:
            c = self.db.cursor()
            c.execute('SELECT hash FROM "file" ORDER BY last_access ASC LIMIT 1')
            h = c.fetchone()[0]
            p = self.make_path(h)

            try:
                os.unlink(p)
                c.execute('DELETE FROM "file" WHERE hash = ?', (h,))
            except OSError:
                break

            made_changes = True

        if made_changes and commit:
            self.db.commit()

    @property
    def cache_size(self):
        c = self.db.cursor()
        c.execute('''SELECT "value" FROM stats WHERE "key" = 'cache_size';''')
        return c.fetchone()[0]

    @staticmethod
    def init_db(path):
        db = sqlite3.connect(path, isolation_level='DEFERRED')
        c = db.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS "file" (
              "hash" TEXT PRIMARY KEY,
              "key" TEXT,
              "size" INTEGER,
              "last_access" INTEGER
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS "stats" (
              "key" TEXT PRIMARY KEY,
              "value" INTEGER
            )
        ''')

        c.execute('''
            INSERT OR IGNORE INTO stats ("key", "value") VALUES ('cache_size', 0)
        ''')

        c.execute('''
            CREATE TRIGGER IF NOT EXISTS delete_file AFTER DELETE ON "file" FOR EACH ROW BEGIN
              UPDATE stats SET "value" = "value" - OLD.size WHERE "key" = 'cache_size';
            END
        ''')

        c.execute('''
            CREATE TRIGGER IF NOT EXISTS insert_file BEFORE INSERT ON "file" FOR EACH ROW BEGIN
              UPDATE stats SET "value" = "value" + NEW.size WHERE "key" = 'cache_size';
            END
        ''')

        c.execute('''
            CREATE INDEX IF NOT EXISTS file_last_access ON "file" (last_access ASC)
        ''')

        db.commit()

        return db

    def make_path(self, x, y, zoom):
        return os.path.join(self.root, str(zoom), str(y), str(x))

    #@staticmethod
    #def hash(key):
    #    m = hashlib.md5()
    #    m.update(key)
    #    return m.hexdigest()

    @staticmethod
    def safe_create(path):
        try:
            f = open(path, 'wb')
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except IOError as err:
            if err.errno != errno.ENOENT:
                return None

        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass

        try:
            f = open(path, 'wb')
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except IOError:
            return None

