# MediaWiki to PDF with Bookmarks #

This was originally written for someone who wanted a complete copy of the Europa Universalis wiki. That wiki uses uses the MediaWiki software. I haven't tried it on other wikis but I suspect it should run with little or no change. I would not point this at a huge wiki and it is not designed for rapidly changing wikis. The first thing I'd do in that case was change the file naming format but that's another issue.


## Example Program Usage ##

**Download a wiki:**
<pre>
mediawiki_to_pdf -url https://eu4.paradoxwikis.com
</pre>

Note, you only need to give the transport://domain_name with no trailing /, or pages. It will pull topics on the main page, pull all names from Special:AllPages page and download those that have content, then merge the files using Ghostscript. See the source code for path/requirements.
