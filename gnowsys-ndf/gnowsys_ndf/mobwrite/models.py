# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# Written 2009 by j@mailb.org
from __future__ import with_statement
import datetime
from django.utils import timezone  #textb
import sys
import os
import urllib
import random

from django.db import models
from django.contrib.auth.models import User
import markdown

from reversion import revision
from reversion.models import Version

import mobwrite_core


def randomString(length):
    s = ''
    letters = "0123456789abcdefghijklmnopqrstuvwxyz"
    while len(s) < length:
        s += letters[random.randint(0, len(letters)-1)]
    return s

def randomName():
    name = randomString(10)
    while TextObj.objects.filter(filename=name).count() > 0:
        name = randomString(10)
    return name

class TextObj(mobwrite_core.TextObj, models.Model):
  # An object which stores a text.

  # Object properties:
  # .lasttime - The last time that this text was modified.

  # Inerhited properties:
  # .name - The unique name for this text, e.g 'proposal'.
  # .text - The text itself.
  # .changed - Has the text changed since the last time it was saved.

  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  filename = models.CharField(max_length=255)
  text = models.TextField(default='share and write')
  lasttime = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return self.filename

  def get_absolute_url(self):
    return "/t/%s/" % self.filename[1:]

  def __init__(self, *args, **kwargs):
    # Setup this object
    mobwrite_core.TextObj.__init__(self, *args, **kwargs)
    models.Model.__init__(self, *args, **kwargs)

  def setText(self, newtext):
    if timezone.now()-self.updated > datetime.timedelta(seconds=10) and self.text != newtext:       #textb
        r = revision        #textb
        self.save()         #textb

    mobwrite_core.TextObj.setText(self, newtext)

    if (not self.changed and
        self.lasttime + mobwrite_core.TIMEOUT_TEXT <
        timezone.now() + mobwrite_core.TIMEOUT_VIEW):       #textb
      # Text object will expire before its view.  Bump the database.
      self.changed = True
      mobwrite_core.LOG.info("Keep-alive save for TextObj: '%s'" % self.id)

    if self.changed:
      self.save()
      if newtext is None:
        mobwrite_core.LOG.debug("Nullified TextObj: '%s'" % self.id)
      else:
        mobwrite_core.LOG.debug("Saved %db TextObj: '%s'" %
            (len(newtext), self.id))
      self.changed = False

  def safe_name(unsafe_name):
    # DataStore doesn't like names starting with numbers.
    return "_" + unsafe_name
  safe_name = staticmethod(safe_name)

  def get_or_insert(model, filename):
    try:
        o = model.objects.get(filename=filename)
    except model.DoesNotExist:
        o = model(filename=filename)
        o.save()
    return o
  get_or_insert = classmethod(get_or_insert)

  def html(self):
    return '\n'.join([
      '<!doctype html>',
      '<html><head>',
      ' <meta http-equiv="Content-Type" content="text/html; charset=utf-8" >'
      '</head>',
      '<body>',
      markdown.markdown(self.text),
      '</body></html>'
    ])

def fetchText(name):
  filename = TextObj.safe_name(name)
  textobj = TextObj.get_or_insert(filename)
  if textobj.text is None:
    mobwrite_core.LOG.debug("Loaded null TextObj: '%s'" % filename)
  else:
    mobwrite_core.LOG.debug("Loaded %db TextObj: '%s'" %
        (len(textobj.text), filename))
  return textobj


class ViewObj(mobwrite_core.ViewObj, models.Model):
  # An object which contains one user's view of one text.

  # Object properties:
  # .edit_stack - List of unacknowledged edits sent to the client.
  # .lasttime - The last time that a web connection serviced this object.
  # .textobj - The shared text object being worked on.

  # Inerhited properties:
  # .username - The name for the user, e.g 'fraser'
  # .filename - The name for the file, e.g 'proposal'
  # .shadow - The last version of the text sent to client.
  # .backup_shadow - The previous version of the text sent to client.
  # .shadow_client_version - The client's version for the shadow (n).
  # .shadow_server_version - The server's version for the shadow (m).
  # .backup_shadow_server_version - the server's version for the backup
  #     shadow (m).

  username = models.CharField(max_length=255, blank=True)
  filename = models.CharField(max_length=2000, blank=True)
  shadow = models.TextField()
  backup_shadow = models.TextField()
  shadow_client_version = models.IntegerField()
  shadow_server_version = models.IntegerField()
  backup_shadow_server_version = models.IntegerField()
  edit_stack = models.TextField()
  lasttime = models.DateTimeField(auto_now=True)
  textobj = models.ForeignKey(TextObj, related_name='viewobj', null=True)

  def __init__(self, *args, **kwargs):
    # Setup this object
    mobwrite_core.ViewObj.__init__(self, *args, **kwargs)
    # The three version numbers are required when defining a models.Model
    kwargs["shadow_client_version"] = self.shadow_client_version
    kwargs["shadow_server_version"] = self.shadow_server_version
    kwargs["backup_shadow_server_version"] = self.backup_shadow_server_version
    models.Model.__init__(self, *args, **kwargs)

  def nullify(self):
    mobwrite_core.LOG.debug("Nullified ViewObj: '%s'" % self.id)
    self.delete()

def fetchUserViews(username):
  query = ViewObj.objects.filter(username=username)
  # Convert list to a hash.
  views = {}
  for viewobj in query:
    mobwrite_core.LOG.debug("Loaded %db ViewObj: '%s@%s'" %
        (len(viewobj.shadow), viewobj.username, viewobj.filename))
    views[viewobj.filename] = viewobj
  if len(views) == 0:
    mobwrite_core.LOG.debug("Unable to find any ViewObj for: '%s'" % username)
  return views


class DjangoMobWrite(mobwrite_core.MobWrite):

  def feedBuffer(self, name, size, index, datum):
    """Add one block of text to the buffer and return the whole text if the
      buffer is complete.

    Args:
      name: Unique name of buffer object.
      size: Total number of slots in the buffer.
      index: Which slot to insert this text (note that index is 1-based)
      datum: The text to insert.

    Returns:
      String with all the text blocks merged in the correct order.  Or if the
      buffer is not yet complete returns the empty string.
    """
    text = ""
    if not 0 < index <= size:
      mobwrite_core.LOG.error("Invalid buffer: '%s %d %d'" % (name, size, index))
    elif size == 1 and index == 1:
      # A buffer with one slot?  Pointless.
      text = datum
      mobwrite_core.LOG.debug("Buffer with only one slot: '%s'" % name)
    else:
      timeout = mobwrite_core.TIMEOUT_BUFFER.seconds
      mc = memcache.Client()
      namespace = "%s_%d" % (name, size)
      # Save this buffer to memcache.
      if mc.add(str(index), datum, time=timeout, namespace=namespace):
        # Add a counter or increment it if it already exists.
        counter = 1
        if not mc.add("counter", counter, time=timeout, namespace=namespace):
          counter = mc.incr("counter", namespace=namespace)
        if counter == size:
          # The buffer is complete.  Extract the data.
          keys = []
          for index in xrange(1, size + 1):
            keys.append(str(index))
          data_map = mc.get_multi(keys, namespace=namespace)
          data_array = []
          for index in xrange(1, size + 1):
            datum = data_map.get(str(index))
            if datum is None:
              mobwrite_core.LOG.critical("Memcache buffer '%s' does not contain element %d."
                  % (namespace, index))
              return ""
            data_array.append(datum)
          text = str("".join(data_array))
          # Abandon the data, memcache will clean it up.
      else:
        mobwrite_core.LOG.warning("Duplicate packet for buffer '%s'." % namespace)
    return urllib.unquote(text)

  def cleanup(self):
    def cleanTable(model, limit):
      query = model.objects.filter(lasttime__lt=limit).delete()

    mobwrite_core.LOG.info("Cleaning database")
    # Delete any view which hasn't been written to in a while.
    limit = timezone.now() - mobwrite_core.TIMEOUT_VIEW     #textb
    cleanTable(ViewObj, limit)

    # Delete any text which hasn't been written to in a while.
    #limit = datetime.datetime.now() - mobwrite_core.TIMEOUT_TEXT
    #cleanTable(TextObj, limit)

    mobwrite_core.LOG.info("Database clean")

  def handleRequest(self, text):
    actions = self.parseRequest(text)
    return self.doActions(actions)

  def doActions(self, actions):
    output = []
    viewobj = None
    last_username = None
    last_filename = None
    user_views = None

    for action_index in xrange(len(actions)):
      # Use an indexed loop in order to peek ahead on step to detect
      # username/filename boundaries.
      action = actions[action_index]
      username = action["username"]
      filename = action["filename"]
      # Fetch the requested view object.
      if not user_views:
        user_views = fetchUserViews(username)
        viewobj = None
      if not viewobj:
        if user_views.has_key(filename):
          viewobj = user_views[filename]
        else:
          viewobj = ViewObj(username=username, filename=filename)
          mobwrite_core.LOG.debug("Created new ViewObj: '%s@%s'" %
              (viewobj.username, viewobj.filename))
          viewobj.shadow = u""
          viewobj.backup_shadow = u""
          viewobj.edit_stack = ""
          viewobj.textobj = fetchText(filename)
          viewobj.save()
          user_views[filename] = viewobj
        delta_ok = True

      if action["mode"] == "null":
        # Nullify the text.
        mobwrite_core.LOG.debug("Nullifying: '%s@%s'" %
            (viewobj.username, viewobj.filename))
        # Textobj transaction not needed; just a set.
        textobj = viewobj.textobj
        textobj.setText(None)
        viewobj.nullify();
        del user_views[filename]
        viewobj = None
        continue

      if (action["server_version"] != viewobj.shadow_server_version and
          action["server_version"] == viewobj.backup_shadow_server_version):
        # Client did not receive the last response.  Roll back the shadow.
        mobwrite_core.LOG.warning("Rollback from shadow %d to backup shadow %d" %
            (viewobj.shadow_server_version, viewobj.backup_shadow_server_version))
        viewobj.shadow = viewobj.backup_shadow
        viewobj.shadow_server_version = viewobj.backup_shadow_server_version
        viewobj.edit_stack = ""

      # Remove any elements from the edit stack with low version numbers which
      # have been acked by the client.
      stack = self.stringToStack(viewobj.edit_stack)
      x = 0
      while x < len(stack):
        if stack[x][0] <= action["server_version"]:
          del stack[x]
        else:
          x += 1
      viewobj.edit_stack = self.stackToString(stack)

      if action["mode"] == "raw":
        # It's a raw text dump.
        data = urllib.unquote(action["data"]).decode("utf-8")
        mobwrite_core.LOG.info("Got %db raw text: '%s@%s'" %
            (len(data), viewobj.username, viewobj.filename))
        delta_ok = True
        # First, update the client's shadow.
        viewobj.shadow = data
        viewobj.shadow_client_version = action["client_version"]
        viewobj.shadow_server_version = action["server_version"]
        viewobj.backup_shadow = viewobj.shadow
        viewobj.backup_shadow_server_version = viewobj.shadow_server_version
        viewobj.edit_stack = ""
        # Textobj transaction not needed; in a collision here data-loss is
        # inevitable anyway.
        textobj = viewobj.textobj
        if action["force"] or textobj.text is None:
          # Clobber the server's text.
          if textobj.text != data:
            textobj.setText(data)
            mobwrite_core.LOG.debug("Overwrote content: '%s@%s'" %
                (viewobj.username, viewobj.filename))
      elif action["mode"] == "delta":
        # It's a delta.
        mobwrite_core.LOG.info("Got '%s' delta: '%s@%s'" %
            (action["data"], viewobj.username, viewobj.filename))
        if action["server_version"] != viewobj.shadow_server_version:
          # Can't apply a delta on a mismatched shadow version.
          delta_ok = False
          mobwrite_core.LOG.warning("Shadow version mismatch: %d != %d" %
              (action["server_version"], viewobj.shadow_server_version))
        elif action["client_version"] > viewobj.shadow_client_version:
          # Client has a version in the future?
          delta_ok = False
          mobwrite_core.LOG.warning("Future delta: %d > %d" %
              (action["client_version"], viewobj.shadow_client_version))
        elif action["client_version"] < viewobj.shadow_client_version:
          # We've already seen this diff.
          pass
          mobwrite_core.LOG.warning("Repeated delta: %d < %d" %
              (action["client_version"], viewobj.shadow_client_version))
        else:
          # Expand the delta into a diff using the client shadow.
          try:
            diffs = mobwrite_core.DMP.diff_fromDelta(viewobj.shadow, action["data"])
          except ValueError:
            diffs = None
            delta_ok = False
            mobwrite_core.LOG.warning("Delta failure, expected %d length: '%s@%s'" %
                (len(viewobj.shadow), viewobj.username, viewobj.filename))
          viewobj.shadow_client_version += 1
          if diffs != None:
            # Textobj transaction required for read/patch/write cycle.
            #FIXME: this should be a transaction idealy
            self.applyPatches(viewobj, diffs, action)

      # Generate output if this is the last action or the username/filename
      # will change in the next iteration.
      if ((action_index + 1 == len(actions)) or
          actions[action_index + 1]["username"] != viewobj.username or
          actions[action_index + 1]["filename"] != viewobj.filename):
        output.append(self.generateDiffs(viewobj,
                                    last_username, last_filename,
                                    action["echo_username"], action["force"],
                                    delta_ok))
        last_username = viewobj.username
        last_filename = viewobj.filename
        # Dereference the cache of user views if the user is changing.
        if ((action_index + 1 == len(actions)) or
            actions[action_index + 1]["username"] != viewobj.username):
          user_views = None
        # Dereference the view object so that a new one can be created.
        viewobj.save()
        viewobj = None

    return "".join(output)


  def generateDiffs(self, viewobj, last_username, last_filename,
                    echo_username, force, delta_ok):
    output = []
    if (echo_username and last_username != viewobj.username):
      output.append("u:%s\n" %  viewobj.username)
    if (last_filename != viewobj.filename or last_username != viewobj.username):
      output.append("F:%d:%s\n" % (viewobj.shadow_client_version, viewobj.filename))

    # Textobj transaction not needed; just a get, stale info is ok.
    textobj = viewobj.textobj
    mastertext = textobj.text

    stack = self.stringToStack(viewobj.edit_stack)

    if delta_ok:
      if mastertext is None:
        mastertext = ""
      # Create the diff between the view's text and the master text.
      diffs = mobwrite_core.DMP.diff_main(viewobj.shadow, mastertext)
      mobwrite_core.DMP.diff_cleanupEfficiency(diffs)
      text = mobwrite_core.DMP.diff_toDelta(diffs)
      if force:
        # Client sending 'D' means number, no error.
        # Client sending 'R' means number, client error.
        # Both cases involve numbers, so send back an overwrite delta.
        stack.append((viewobj.shadow_server_version,
            "D:%d:%s\n" % (viewobj.shadow_server_version, text)))
      else:
        # Client sending 'd' means text, no error.
        # Client sending 'r' means text, client error.
        # Both cases involve text, so send back a merge delta.
        stack.append((viewobj.shadow_server_version,
            "d:%d:%s\n" % (viewobj.shadow_server_version, text)))
      viewobj.shadow_server_version += 1
      mobwrite_core.LOG.info("Sent '%s' delta: '%s@%s'" %
          (text, viewobj.username, viewobj.filename))
    else:
      # Error; server could not parse client's delta.
      # Send a raw dump of the text.
      viewobj.shadow_client_version += 1
      if mastertext is None:
        mastertext = ""
        stack.append((viewobj.shadow_server_version,
            "r:%d:\n" % viewobj.shadow_server_version))
        mobwrite_core.LOG.info("Sent empty raw text: '%s@%s'" %
            (viewobj.username, viewobj.filename))
      else:
        # Force overwrite of client.
        text = mastertext
        text = text.encode("utf-8")
        text = urllib.quote(text, "!~*'();/?:@&=+$,# ")
        stack.append((viewobj.shadow_server_version,
            "R:%d:%s\n" % (viewobj.shadow_server_version, text)))
        mobwrite_core.LOG.info("Sent %db raw text: '%s@%s'" %
            (len(text), viewobj.username, viewobj.filename))

    viewobj.shadow = mastertext

    for edit in stack:
      output.append(edit[1])

    mobwrite_core.LOG.debug("Saving %db ViewObj: '%s@%s'" %
        (len(viewobj.shadow), viewobj.username, viewobj.filename))
    viewobj.edit_stack = self.stackToString(stack)
    viewobj.save()

    return "".join(output)

  def stringToStack(self, string):
    stack = []
    for line in string.split("\n"):
      if line:
        (version, command) = line.split("\t", 1)
        stack.append((int(version), command))
    return stack

  def stackToString(self, stack):
    strings = []
    for (version, command) in stack:
      strings.append(str(version) + "\t" + command)
    return "\n".join(strings)

