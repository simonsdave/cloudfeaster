Chrome proxy extension? What's this all about?
Wanted to support routing spider traffic through a proxy
(spiders talk to a Chrome Browser via webdriver and
the browser talks to the proxy).
All seems pretty straight forward until you want to start
supporting proxies which require authentication and that's
when some combination of webdriver and/or chrome seem to
stop playing nicely. To solve this problem some clever
folks came up with the idea of defining a Chrome extension
to setup the proxy -
[here's](https://vimmaniac.com/blog/bangal/selenium-chrome-driver-proxy-with-authentication/)
the example on which this code was based.
With variables replaced and the files in this directory
zipped up into a single archive, the archive becomes the
extention.
