# Spider Authors

An overview of the spider development process.
We'll use [this](https://github.com/simonsdave/gaming-spiders)
collection of spiders as an example.
Embedded in this documentation is a health does of best practice
guidance as well as required practice.
Best efforts will be made to note when something is only best practice.

* create a private or public repo on [github](https://github.com)
* setup the repo to produce a Python distribution with a name
end with ```-spiders``` (this naming convention is important because
it's relied upon by the ```spiders.py``` utility during spider discovery
* connect the repo to Travis - each Travis build should:
  * run pep8/flake8 on the spiders
  * create a pip installable Python package containing all spiders
  * create a docker image with all the spiders
  * push the newly created docker image to a dockerhub that's either public
or has the dockerhub user cloudfeater as a collaborator
* ```lots more to fill in here```

## Metadata

* ...

### TTL

* Cloudfeaster Services will cache the results of running a spider
for the number of seconds defined by the ```ttl``` property of a
spider's metadata.
* if the ```ttl``` property is missing 60 is assumed
* ```ttl``` must be at least 60 (screen scraping web sites with info
that often takes a bit to refresh and thus the rational for the 
minimum ```ttl``` value of 60)

```python
class MySpider(spider.Spider):

    @classmethod
    def get_metadata(self):
        return {
            "url": "https://example.com",
            "ttl": 120,
```

### Factor Display Names

* [locale](https://en.wikipedia.org/wiki/Locale)
* ```LANG``` environment variable which will look something like ```en_CA.UTF-8``` - take the first 2 characters
and this will be the [ISO639-2](http://www.loc.gov/standards/iso639-2/php/code_list.php) language code

```python
"factor_display_names": {
    "email": {
        "en": "e-mail",
        "fr": "e-mail",
        "ja": "電子メール",
    },
    "password": {
        "en": "Password",
        "fr": "mot de passe",
        "ja": "パスワード",
    },
},
```

* per above, with factor display names & encoding ...

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
```

* to try different factor display names try something like ...

```bash
>LANG=ja ./spider.py
```

## Resources
* [inDifferent Languages](http://www.indifferentlanguages.com/words/e-mail) - How Do You Say Different English Words and Expressions in Different Languages - examples
  * [e-mail](http://www.indifferentlanguages.com/words/e-mail)
  * [password](http://www.indifferentlanguages.com/words/password)
