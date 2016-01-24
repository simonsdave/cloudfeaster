# Change Log
All notable changes to this project will be documented in this file.
Format of this file follows [these](http://keepachangelog.com/) guidelines.
This project adheres to [Semantic Versioning](http://semver.org/).

## [0.6.0] - [2016-01-24]

### Changed

- colorama now req'd to be @ least version 0.3.5 instead of only 0.3.5

- command line args to bin/spiderhost.sh have been simplified - now just
  take spider name and spider args just as you'd expect - no more url
  encoding of args and ----- indicating no spider args

- like the changes to bin/spiderhost.sh, bin/spiderhost.py now just accepts
  regular command line arguments of a spider name and spider args - much easier

### Removed

- bin/spiders.sh is no longer needed - callers now access bin/spiders.py
  directly rather that getting at bin/spiders.py through bin/spiders.sh

## [0.5.0] - [2015-05-10]

- not really the initial release but intro'ed CHANGELOG.md late
- initial clf commit to github was 13 Oct '13
