# Copyright (C) 2008 Patrick Lewis
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

import unittest
from os.path import join, dirname
from merge3 import Merge3

class Merge3Test(unittest.TestCase):
    
    def read_datafile(self, filename):
        f = open(join(self.datapath, filename), 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def setUp(self):
        self.datapath = join(dirname(__file__), 'datafiles')
        self.base = self.read_datafile('ancestor.txt')
        
    def tearDown(self):
        pass
        
    def test_simple_merge(self):
        a = self.read_datafile('insert1.txt')
        b = self.read_datafile('insert2.txt')
        expected = self.read_datafile('result1.txt')
        m = Merge3(self.base, a, b)
        self.assertEqual([l for l in m.merge_lines()], expected)
        
    def test_conflict(self):
        a = self.read_datafile('insert1.txt')
        b = self.read_datafile('conflict1.txt')
        expected = self.read_datafile('resultconflict.txt')
        m = Merge3(self.base, a, b)
        self.assertEqual([l for l in m.merge_lines()], expected)
        
    def test_delete(self):
        a = self.read_datafile('insert1.txt')
        b = self.read_datafile('delete1.txt')
        expected = self.read_datafile('resultdelete.txt')
        m = Merge3(self.base, a, b)
        self.assertEqual([l for l in m.merge_lines()], expected)
        