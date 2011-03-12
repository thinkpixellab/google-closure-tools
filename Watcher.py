import Shared
import os
import subprocess
import time

class Watcher:
  def __init__(self, rootdir, file_filter = '*'):
    self._rootdir = rootdir
    self._file_filter = file_filter
    self._hash = {}
    self._working = False

  def watch(self, callback):
    while(True):
      diff = self.loop()
      if len(diff):
        print diff
        callback(diff)
      time.sleep(0.5)

  def loop(self):
    newHash = Watcher.getFileHash(self._rootdir, self._file_filter)
    diff = Watcher.compare(self._hash, newHash)
    self._hash = newHash
    return diff

  @staticmethod
  def compare(oldHash, newHash):
    added = []
    changed = []
    for k,v in newHash.iteritems():
      if oldHash.has_key(k):
        if oldHash[k] != v:
          changed.append(k)
        del oldHash[k]
      else:
        added.append(k)

    removed = oldHash.keys()

    vals = {}
    if added:
      vals['added'] = added
    if removed:
      vals['removed'] = removed
    if changed:
      vals['changed'] = changed
    return vals

  @staticmethod
  def getFileHash(rootdir, file_filter = '*'):
    return dict(Watcher.enumerate_hashes(rootdir, file_filter))

  @staticmethod
  def enumerate_hashes(rootdir, file_filter):
    rootdir = os.path.abspath(rootdir)
    command = ['git', 'hash-object']
    for file in Shared.find_files(rootdir, file_filter):
      args = list(command) + [file]
      yield file, subprocess.check_output(args).strip()
