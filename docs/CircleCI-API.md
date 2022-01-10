# CircleCI API

* [CircleCI API Developer's Guide](https://circleci.com/docs/2.0/api-developers-guide/)
* [CircleCI API (v2)](https://circleci.com/docs/api/v2/)

## Authentication

* generate [Personal API Token](https://app.circleci.com/settings/user/tokens) which is associated with a user
  and assign it to the environment variable ```PERSONAL_API_TOKEN```

* test the token works

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    https://circleci.com/api/v2/me
~>
```

## Accept Header

* use an accept header to return compressed json

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    --header 'Accept: application/json' \
    https://circleci.com/api/v2/me
~>
```

## URLs

* project slug = ```gh/simonsdave/cloudfeaster```
* example URL ```https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/pipeline```

## Rate Limiting

* API implements rate limiting
* HTTP status code of 429 when rate limiting tripped and [Retry-After](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Retry-After)
  header may be returned with the response and in the absense of such a header
  clients should use an exponential backoff approach to retry

## Get Project Details

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    --header 'Accept: application/json'    \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster
~>
```

## Get All Pipelines For A Repo

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    --header 'Accept: application/json'    \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/pipeline
~>
```

## Trigger a Pipeline

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    -X POST \
    --header 'Content-Type: application/json' \
    --data '{"branch": "master"}' \
    --header 'Accept: application/json'    \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/pipeline
~>
```

## Scheduled Pipelines

* [Scheduled Pipelines](https://circleci.com/docs/2.0/scheduled-pipelines)
* [7 Jan '22 - Getting started with scheduled pipelines](https://circleci.com/blog/using-scheduled-pipelines/)
* can configure schedules under ```project settings / triggers``` (ex [https://app.circleci.com/settings/project/github/simonsdave/cloudfeaster/triggers](https://app.circleci.com/settings/project/github/simonsdave/cloudfeaster/triggers))
* [Schedule CircleCI API (v2)](https://circleci.com/docs/api/v2/#tag/Schedule)

### Get All Schedules

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    --header 'Accept: application/json' \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/schedule
~>
```

### Create Schedule

* [https://circleci.com/docs/api/v2/#operation/createSchedule](https://circleci.com/docs/api/v2/#operation/createSchedule)
* note = "hour of day" is in UTC; API docs don't make this clear but you can see from the UI

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    -X POST \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "name": "Integration Tests",
        "description": "Run Intergration Tests",
        "attribution-actor": "system",
        "parameters": {
            "branch": "master"
        },
        "timetable": {
            "per-hour": 1,
            "hours-of-day": [21],
            "days-of-week": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        }
    }' \
    --header 'Accept: application/json' \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/schedule | jq .
{
  "description": "Run Intergration Tests",
  "updated-at": "2022-01-09T20:13:18.855Z",
  "name": "Integration Tests",
  "id": "00000000-1111-2222-3333-444444444444",
  "project-slug": "gh/simonsdave/cloudfeaster",
  "created-at": "2022-01-09T20:13:18.855Z",
  "parameters": {
    "branch": "master"
  },
  "actor": {
    "login": "system-actor",
    "name": "Scheduled",
    "id": "55555555-1111-2222-3333-444444444444",
  },
  "timetable": {
    "per-hour": 1,
    "hours-of-day": [
      21
    ],
    "days-of-week": [
      "MON",
      "TUE",
      "WED",
      "THU",
      "FRI",
      "SAT",
      "SUN"
    ]
  }
}
~>
```

### Get A Schedule

* get a schedule after it's been created

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    --header 'Accept: application/json' \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/schedule/00000000-1111-2222-3333-444444444444
~>
```

## Delete Schedule

* delete a schedule after it's been created

```bash
~> curl \
    -s \
    --header "Circle-Token: ${PERSONAL_API_TOKEN}" \
    -X DELETE \
    --header 'Accept: application/json' \
    https://circleci.com/api/v2/project/gh/simonsdave/cloudfeaster/schedule/00000000-1111-2222-3333-444444444444
~>
```
