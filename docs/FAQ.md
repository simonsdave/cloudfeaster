#FAQ

### What skills do I need to author spiders?
1. basic Python
1. grok how HTML websites are built
1. good understanding of [XPath](http://en.wikipedia.org/wiki/XPath)

### How can I generate a coverage report?
From CloudFeaster's root directory run the following:
~~~~~
coverage erase
rm -rf ./coverage_report/
nosetests --with-coverage
coverage html
~~~~~
An HTML version of the coverage report can now be found in coverage_report/index.html

### How can I make my spiders run faster?

CloudFeaster's approach of using [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) makes it super easy to create spiders that are very resilient to web site changes. Ease of implementation and maintenance comes at the expense of performance. How can I improve the performance of my CloudFeaster spiders?
All [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) based
spiders inherit their performance characteristics from the cost of spinning up and driving a real browser. To make significant progress on performance you've got to avoid spinning up browsers.

Some practical details on how to avoid using real browsers ... the [Selenium+WebDriver (aka Selenium 2.0)](http://www.seleniumhq.org/projects/webdriver/) spiders all derive from [webdriver_spider.Spider](https://github.com/simonsdave/clf/blob/master/clf/webdriver_spider.py#L29).
One approach to making your spiders really fast would be to create a new abstract base class which derives from [spider.Spider](https://github.com/simonsdave/clf/blob/master/clf/spider.py#L22) and integrates with one of the [existing libraries](https://github.com/simonsdave/clf/wiki/Other-Web-Scraping-Utilities-&-Approaches#utilities) which makes it easier to create a network traffic based spider. This approach will avoid the overhead of spinning up real browsers and yet still allow you to take advantage of CloudFeaster's other features.
