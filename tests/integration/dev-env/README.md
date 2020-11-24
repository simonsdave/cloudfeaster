# Integration Tests

The primary purpose of integration tests is to verify the functional correctness
of Cloudfeaster assets (read docker image file and samples) that are generated
as part of the CI process.

```bash
~> ./docker_image_integration_tests.sh --verbose simonsdave/cloudfeaster-dev-env:bindle ppun pppw
Running 'test_sample_spider_python_wheels'
Running 'test_sample_spider_pypi'
Running 'test_sample_spider_xe_exchange_rates'
Successfully completed 3 integration tests.
~>
```
