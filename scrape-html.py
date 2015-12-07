#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; -*-
#
# Copyright © 2013-2014, Jeroen Janssens
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# scrape-html: Extract HTML elements using an XPath query or CSS3 selector.
#
# Example usage:
# $ curl 'http://en.wikipedia.org/wiki/List_of_sovereign_states' -s \
#       | scrape -be 'table.wikitable > tr > td > b > a'
#
# Dependencies: lxml and cssselector
#
# Author:     Jeroen Janssens <datascience@jeroenjanssens.com>
# Maintainer: Remy Goldschmidt <taktoa@gmail.com>

import sys
import argparse
from lxml import etree
from cssselect import GenericTranslator, SelectorError


def argument_parser():
    parser = argparse.ArgumentParser()

    def arg(*args, **kwargs):
        parser.add_argument(*args, **kwargs)

    arg('query_type', nargs='?', default="xpath", choices=["xpath", "css"],
        help="A query type", metavar="QUERY-TYPE")
    arg('query', nargs='?', default="*",
        help="The query itself", metavar="QUERY")
    arg('html', nargs='?', default=sys.stdin, type=argparse.FileType('rb'),
        help="A file containing HTML to query", metavar="FILE")
    arg('-a', default="", dest="argument",
        help="the argument to extract from tag", metavar="ARGUMENT")
    arg('-f', default='utf-8', dest="input_encoding",
        help="encoding with which to read the file", metavar="CODE")
    arg('-t', default='utf-8', dest="output_encoding",
        help="encoding with which to write to stdout", metavar="CODE")
    arg('-b', '--body', default=False, action='store_true',
        help="enclose output with HTML and BODY tags")
    arg('-r', '--raw', default=False, action='store_true',
        help="do not parse HTML before feeding etree")

    return parser


def main():
    parser = argument_parser()

    args = parser.parse_args()

    xpath = args.query

    if args.query_type == "css":
        try:
            xpath = GenericTranslator().css_to_xpath(args.query)
        except SelectorError:
            parser.error('Invalid CSS selector')
    else:
        xpath = args.query

    html_parser = etree.HTMLParser(encoding=args.input_encoding,
                                   recover=True,
                                   strip_cdata=True)
    if args.raw:
        document = etree.fromstring(args.html.read())
    else:
        document = etree.parse(args.html, html_parser)

    if args.body:
        sys.stdout.write("<!DOCTYPE html>\n<html>\n<body>\n")

    for e in document.xpath(xpath):
        try:
            if not args.argument:
                text = etree.tostring(e, encoding="unicode")
            else:
                text = e.get(args.argument)
            if text is not None:
                sys.stdout.write(text)
                sys.stdout.write("\n")
            sys.stdout.flush()
        except IOError:
            pass

    if args.body:
        sys.stdout.write("</body>\n</html>\n")

if __name__ == "__main__":
    exit(main())
