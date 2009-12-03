# Copyright (C) 2005, 2006, 2007, 2008 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Exceptions for bzr, and reporting of them.
"""


from warnings import warn

class BzrError(StandardError):
    """
    Base class for errors raised by bzrlib.

    :cvar internal_error: if True this was probably caused by a bzr bug and
    should be displayed with a traceback; if False (or absent) this was
    probably a user or environment error and they don't need the gory details.
    (That can be overridden by -Derror on the command line.)

    :cvar _fmt: Format string to display the error; this is expanded
    by the instance's dict.
    """
    
    internal_error = False

    def __init__(self, msg=None, **kwds):
        """Construct a new BzrError.

        There are two alternative forms for constructing these objects.
        Either a preformatted string may be passed, or a set of named
        arguments can be given.  The first is for generic "user" errors which
        are not intended to be caught and so do not need a specific subclass.
        The second case is for use with subclasses that provide a _fmt format
        string to print the arguments.  

        Keyword arguments are taken as parameters to the error, which can 
        be inserted into the format string template.  It's recommended 
        that subclasses override the __init__ method to require specific 
        parameters.

        :param msg: If given, this is the literal complete text for the error,
        not subject to expansion.
        """
        StandardError.__init__(self)
        if msg is not None:
            # I was going to deprecate this, but it actually turns out to be
            # quite handy - mbp 20061103.
            self._preformatted_string = msg
        else:
            self._preformatted_string = None
            for key, value in kwds.items():
                setattr(self, key, value)

    def __str__(self):
        s = getattr(self, '_preformatted_string', None)
        if s is not None:
            # contains a preformatted message; must be cast to plain str
            return str(s)
        try:
            fmt = self._get_format_string()
            if fmt:
                d = dict(self.__dict__)
                # special case: python2.5 puts the 'message' attribute in a
                # slot, so it isn't seen in __dict__
                d['message'] = getattr(self, 'message', 'no message')
                s = fmt % d
                # __str__() should always return a 'str' object
                # never a 'unicode' object.
                if isinstance(s, unicode):
                    return s.encode('utf8')
                return s
        except (AttributeError, TypeError, NameError, ValueError, KeyError), e:
            return 'Unprintable exception %s: dict=%r, fmt=%r, error=%r' \
                % (self.__class__.__name__,
                   self.__dict__,
                   getattr(self, '_fmt', None),
                   e)

    def _get_format_string(self):
        """Return format string for this exception or None"""
        fmt = getattr(self, '_fmt', None)
        if fmt is not None:
            return fmt
        fmt = getattr(self, '__doc__', None)
        if fmt is not None:
            warn("%s uses its docstring as a format, "
                    "it should use _fmt instead" % self.__class__.__name__,
                    DeprecationWarning)
            return fmt
        return 'Unprintable exception %s: dict=%r, fmt=%r' \
            % (self.__class__.__name__,
               self.__dict__,
               getattr(self, '_fmt', None),
               )


class CantReprocessAndShowBase(BzrError):

    _fmt = ("Can't reprocess and show base, because reprocessing obscures "
           "the relationship of conflicting lines to the base")


class BinaryFile(BzrError):
    
    _fmt = "File is binary but should be text."


