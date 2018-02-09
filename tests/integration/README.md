# Integration Tests

The primary purpose of integration tests is to verify the functional correctness
of Cloudfeaster assets (read docker image file and samples) that are generated
as part of the CI process.

Running integration tests - note setting of ```CLF_DOCKER_IMAGE``` environment variable
so ```docker_image_integration_tests.py``` knows which docker image you want to validate.

```bash
(env) ~/cloudfeaster/tests/integration> docker images
REPOSITORY                TAG                 IMAGE ID            CREATED             SIZE
simonsdave/cloudfeaster   latest              d6e07bb87c2c        2 days ago          795MB
ubuntu                    14.04               dc4491992653        2 weeks ago         222MB
koalaman/shellcheck       latest              41f67b8f2cbf        2 weeks ago         19MB
(env) ~/cloudfeaster/tests/integration> CLF_DOCKER_IMAGE=simonsdave/cloudfeaster:latest nosetests -v .
test_spider_host_dot_py_on_boc_fx_rate (docker_image_integration_tests.SamplesIntegrationTestCase) ... ok
test_spiders_dot_py_with_samples (docker_image_integration_tests.SpidersDotPyIntegrationTestCase) ... ok
test_spiders_dot_py_without_samples (docker_image_integration_tests.SpidersDotPyIntegrationTestCase) ... ok

----------------------------------------------------------------------
Ran 3 tests in 13.393s

OK
(env) ~/cloudfeaster/tests/integration>
```
