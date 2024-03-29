# Copyright (C) 2006 Canonical Ltd
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

"""Utilities for distinguishing binary files from text files"""

from itertools import chain

from merge3.bzrlib.errors import BinaryFile
from merge3.bzrlib.iterablefile import IterableFile
#from bzrlib.osutils import file_iterator


# def text_file(input):
#     """Produce a file iterator that is guaranteed to be text, without seeking.
#     BinaryFile is raised if the file contains a NUL in the first 1024 bytes.
#     """
#     first_chunk = input.read(1024)
#     if '\x00' in first_chunk:
#         raise BinaryFile()
#     return IterableFile(chain((first_chunk,), file_iterator(input)))


def check_text_lines(lines):
    """Raise BinaryFile if the supplied lines contain NULs.
    Only the first 1024 characters are checked.
    """
    f = IterableFile(lines)
    if '\x00' in f.read(1024):
        raise BinaryFile()


# def check_text_path(path):
#     """Check whether the supplied path is a text, not binary file.
#     Raise BinaryFile if a NUL occurs in the first 1024 bytes.
#     """
#     f = open(path, 'rb')
#     try:
#         text_file(f)
#     finally:
#         f.close()

