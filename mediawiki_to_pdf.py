#!/usr/bin/env python

"""
Take a MediaWiki wiki and save the entire site to a single fully bookmarked PDF

Requires:
    Python modules: pdfkit, requests
    Windows Binaries: wkhtmltopdf and Ghostscript

Copyright 2017 by Stephen Genusa
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import argparse
import HTMLParser
import os
import re
import subprocess
import urllib3

import pdfkit
import requests

#Dropped PyPDF2 due to lack of bookmark support on merge
#from PyPDF2 import PdfFileMerger, PdfFileReader


class WikiPDFBuilder(object):
    """
    """
    def __init__(self, args):
        """
        initialize internal properties
        """
        self.wiki_url = args.wiki_url
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


    def make_uniq_list(self, a_list): 
       new_list = []
       [new_list.append(i) for i in a_list if not new_list.count(i)]
       return new_list
   
   
    def get_html_for_page(self, url):
        print "getting page", url
        req = requests.get(url, verify=False)
        return req.content


    def get_unique_urls(self):
        url_list = []
        base_link_regex = '<a href\="(/[a-zA-Z_0-9%]{2,40})"'
        base_next_page_regex = '<a href="(/index\.php\?title=Special:AllPages&amp;from=.*?)" title="Special:AllPages">Next page'
        # 1. Get main page links
        match = re.findall(base_link_regex, self.get_html_for_page(self.wiki_url))
        if match:
            url_list.extend (self.make_uniq_list(match))
        # 2. Get first page of all links
        html_content = self.get_html_for_page(self.wiki_url + '/Special:AllPages')
        match = re.findall('<li>' + base_link_regex, html_content)
        if match:
            url_list.extend (self.make_uniq_list(match))
        match = re.findall(base_next_page_regex, html_content, re.MULTILINE)
        # 3. Get the rest of the page links
        while match:
            next_page_url = HTMLParser.HTMLParser().unescape(match[0])
            html_content = self.get_html_for_page(self.wiki_url + next_page_url)
            match = re.findall('<li>' + base_link_regex, html_content)
            if match:
                url_list.extend (self.make_uniq_list(match))
            match = re.findall('\ ' + base_next_page_regex, html_content, re.MULTILINE)
            
        url_list = self.make_uniq_list(url_list)
        return url_list

    def generate_wiki_pdf(self):
        wiki_uniq_urls = self.get_unique_urls()
        wiki_pdf_files = []
        
        url_page_count = len(wiki_uniq_urls)
        print "wiki pages found", 
        
        for index, url in enumerate(wiki_uniq_urls):
            pdf_filename = str(index+1).zfill(4) + ".pdf"
            # Only create PDF files that do not exist
            if not os.path.isfile(pdf_filename):
                url = url[1:]
                next_url = self.wiki_url + '/index.php?title=' + url + '&printable=yes'
                print "url is", next_url, "(" + str(index + 1) + "/" + str(url_page_count) + ")"
                pdfkit.from_url(next_url, pdf_filename , configuration=pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'))
            wiki_pdf_files.append(pdf_filename)
            
        #PyPDF2 does not support bookmarks in the merge so dump this code
        #merger = PdfFileMerger()
        #for pdf in wiki_pdf_files:
        #    merger.append(PdfFileReader(file(pdf, 'rb')))
        #merger.write("wiki.pdf")
        
        #Ghostscript supports bookmarks in the merge
        # Write out the list of files (exceeds commandline limits, so save to file)
        with open("pdffiles.txt", "w") as outf: 
            for pdf_filename in wiki_pdf_files:
                outf.write("{0}\n".format(pdf_filename))
        # Write out a batch file that calls Ghostscript to do the merge - allows for customization
        with open("merge_wiki.bat", "w") as outf: 
            outf.write("\"C:\\Program Files\\gs\\gs9.22\\bin\\gswin64.exe\" -dBATCH -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=wiki.pdf @pdffiles.txt")
        # Execute the batch file
        subprocess.call(["merge_wiki.bat"])
             
  
if __name__ == "__main__":
    # pylint: disable-msg=C0103
    print("\nStephen Genusa's MediaWiki PDF Builder 1.0\n")
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", "--wiki_url", help="The top url for the Wiki excluding the trailing /")
    parser_args = parser.parse_args()
    if not parser_args.wiki_url:
        parser.print_help()
        exit()
    documenter = WikiPDFBuilder(parser_args)
    documenter.generate_wiki_pdf()