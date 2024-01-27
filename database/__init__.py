"""database

Provide convenience wrappers around the sqlite3 module.
"""

import contextlib
import sqlite3

@contextlib.contextmanager
def connect(*args, **kwargs):
  connection = None
  try:
    with sqlite3.connect(*args, **kwargs) as connection:
      yield connection
  finally:
    if connection is not None:
      connection.close()
  