# -*- coding: utf-8 -*-
## $Id$
## CDSware Search Engine unit tests.

## This file is part of the CERN Document Server Software (CDSware).
## Copyright (C) 2002, 2003, 2004, 2005 CERN.
##
## The CDSware is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## The CDSware is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.  
##
## You should have received a copy of the GNU General Public License
## along with CDSware; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for the search engine."""

__version__ = "$Id$"

import search_engine
import unittest

class TestWashQueryParameters(unittest.TestCase):
    """Test for washing of search query parameters."""

    def test_wash_url_argument(self):
        """search engine - washing of URL arguments"""
        self.assertEqual(1, search_engine.wash_url_argument(['1'],'int'))
        self.assertEqual("1", search_engine.wash_url_argument(['1'],'str'))
        self.assertEqual(['1'], search_engine.wash_url_argument(['1'],'list'))
        self.assertEqual(0, search_engine.wash_url_argument('ellis','int'))
        self.assertEqual("ellis", search_engine.wash_url_argument('ellis','str'))
        self.assertEqual(["ellis"], search_engine.wash_url_argument('ellis','list'))
        self.assertEqual(0, search_engine.wash_url_argument(['ellis'],'int'))
        self.assertEqual("ellis", search_engine.wash_url_argument(['ellis'],'str'))
        self.assertEqual(["ellis"], search_engine.wash_url_argument(['ellis'],'list'))

    def test_wash_pattern(self):
        """search engine - washing of query patterns"""
        self.assertEqual("Ellis, J", search_engine.wash_pattern('Ellis, J'))
        self.assertEqual("ell", search_engine.wash_pattern('ell*'))


class TestStripAccents(unittest.TestCase):
    """Test for handling of UTF-8 accents."""

    def test_strip_accents(self):
        """search engine - stripping of accented letters"""
        self.assertEqual("memememe", search_engine.strip_accents('mémêmëmè'))
        self.assertEqual("MEMEMEME", search_engine.strip_accents('MÉMÊMËMÈ'))


class TestQueryParser(unittest.TestCase):
    """Test of search pattern (or query) parser."""

    def _check(self, p, f, m, result_wanted):
        "Internal checking function calling create_basic_search_units."
        result_obtained = search_engine.create_basic_search_units(None, p, f, m)
        assert result_obtained == result_wanted, \
               'obtained %s instead of %s' % (repr(result_obtained), repr(result_wanted))
        return

    def test_parsing_single_word_query(self):
        "search engine - parsing single word queries"
        self._check('word', '', None, [['|', 'word', '', 'w']])

    def test_parsing_single_word_in_field(self):
        "search engine - parsing single word queries in a logical field"
        self._check('word', 'title', None, [['|', 'word', 'title', 'w']])

    def test_parsing_single_word_in_tag(self):
        "search engine - parsing single word queries in a physical tag"
        self._check('word', '500', None, [['|', 'word', '500', 'a']])

    def test_parsing_query_with_commas(self):
        "search engine - parsing queries with commas"
        self._check('word,word', 'title', None, [['|', 'word,word', 'title', 'a']])

    def test_parsing_exact_phrase_query(self):
        "search engine - parsing exact phrase"
        self._check('"the word"', 'title', None, [['|', 'the word', 'title', 'a']])
        
    def test_parsing_exact_phrase_query_unbalanced(self):
        "search engine - parsing unbalanced exact phrase"
        self._check('"the word', 'title', None, [['|', '"the', 'title', 'w'],
                                                 ['+', 'word', 'title', 'w']])
        
    def test_parsing_exact_phrase_query_in_any_field(self):
        "search engine - parsing exact phrase in any field"
        self._check('"the word"', '', None, [['|', 'the word', 'anyfield', 'a']])
        
    def test_parsing_partial_phrase_query(self):
        "search engine - parsing partial phrase"
        self._check("'the word'", 'title', None, [['|', '%the word%', 'title', 'a']])

    def test_parsing_partial_phrase_query_unbalanced(self):
        "search engine - parsing unbalanced partial phrase"
        self._check("'the word", 'title', None, [['|', "'the", 'title', 'w'],
                                                 ['+', "word", 'title', 'w']])
    def test_parsing_partial_phrase_query_in_any_field(self):
        "search engine - parsing partial phrase in any field"
        self._check("'the word'", '', None, [['|', "'the", '', 'w'],
                                             ['|', "word'", '', 'w']])
            
    def test_parsing_regexp_query(self):
        "search engine - parsing regex matches"
        self._check("/the word/", 'title', None, [['|', 'the word', 'title', 'r']])
        
    def test_parsing_regexp_query_unbalanced(self):
        "search engine - parsing unbalanced regexp"
        self._check("/the word", 'title', None, [['|', '/the', 'title', 'w'],
                                                 ['+', 'word', 'title', 'w']])
    def test_parsing_regexp_query_in_any_field(self):
        "search engine - parsing regexp searches in any field"
        self._check("/the word/", '', None, [['|', "/the", '', 'w'],
                                             ['|', "word/", '', 'w']])
        
    def test_parsing_boolean_query(self):
        "search engine - parsing boolean query with several words"
        self._check("muon kaon ellis cern", '', None, [['|', 'muon', '', 'w'],
                                                       ['+', 'kaon', '', 'w'],
                                                       ['+', 'ellis', '', 'w'],
                                                       ['+', 'cern', '', 'w']])
        
    def test_parsing_boolean_query_with_word_operators(self):
        "search engine - parsing boolean query with word operators"
        self._check("muon and kaon or ellis not cern", '', None, [['|', 'muon', '', 'w'],
                                                                  ['+', 'kaon', '', 'w'],
                                                                  ['|', 'ellis', '', 'w'],
                                                                  ['-', 'cern', '', 'w']])
        
    def test_parsing_boolean_query_with_symbol_operators(self):
        "search engine - parsing boolean query with symbol operators"
        self._check("muon +kaon |ellis -cern", '', None, [['|', 'muon', '', 'w'],
                                                          ['+', 'kaon', '', 'w'],
                                                          ['|', 'ellis', '', 'w'],
                                                          ['-', 'cern', '', 'w']])
        
    def test_parsing_boolean_query_with_symbol_operators_and_spaces(self):
        "search engine - parsing boolean query with symbol operators and spaces"
        self._check("muon + kaon | ellis - cern", '', None, [['|', 'muon', '', 'w'],
                                                             ['+', 'kaon', '', 'w'],
                                                             ['|', 'ellis', '', 'w'],
                                                             ['-', 'cern', '', 'w']])
        
    def test_parsing_boolean_query_with_symbol_operators_and_no_spaces(self):
        "search engine - parsing boolean query with symbol operators and no spaces"
        self._check("muon+kaon|ellis-cern", '', None, [['|', 'muon+kaon|ellis-cern', '', 'w']])
        
    def test_parsing_combined_structured_query(self):
        "search engine - parsing combined structured query"
        self._check("title:muon author:ellis", '', None, [['|', 'muon', 'title', 'w'],
                                                          ['+', 'ellis', 'author', 'w']])
        
    def test_parsing_structured_regexp_query(self):
        "search engine - parsing structured regexp query"
        self._check("title:/(one|two)/", '', None, [['|', '(one|two)', 'title', 'r']]),
        
    def test_parsing_combined_structured_query_in_a_field(self):
        "search engine - parsing structured query in a field"
        self._check("title:muon author:ellis", 'abstract', None, [['|', 'muon', 'title', 'w'],
                                                                  ['+', 'ellis', 'author', 'w']])
        
        
def create_test_suite():
    """Return test suite for the search engine."""
    return unittest.TestSuite((unittest.makeSuite(TestWashQueryParameters,'test'),
                               unittest.makeSuite(TestStripAccents,'test'),
                               unittest.makeSuite(TestQueryParser,'test')))

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(create_test_suite())