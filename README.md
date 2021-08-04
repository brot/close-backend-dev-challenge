# Close Backend Developer Challenge

## Request statistics exercise

This Flask app counts every request by URL path and store this metric in Redis.

It handles the following three sets of endpoints:
* `GET /api/*` - Simulated API endpoints
* `GET /stats/` - Returns JSON report of URL request statistics
* `POST /test/{number of requests}/` - Starts a test run to generate fake requests

The complete task and spec description can be found [here](https://gist.githubusercontent.com/jkemp101/0a7212e19fa9c5dbc547c608f9018dfe/raw/35e376f8b294933e493eb371ccf6f2b4f1ad8b9f/backend_challenge.md)


## Basic usage

1. Start with docker-compose
   ```sh
   docker-compose up
   ```
1. Open http://localhost:5000/stats/ in your local browser to get the initial JSON report
1. Start a test run to generate fake requests with the desired number of requests in the URL path. e.g: to fake 20 requests you can call
   ```sh
   curl -X POST localhost:5000/test/20/
   ```
1. Reload http://localhost:5000/stats/ in your local browser to get the updated JSON report

## Overview of my solution

The Flask app is packaged into a Docker Compose environment. Beside the Flask container we also start a Redis container.

### Redis

Redis is used to store the request count statistic.
The Redis data structure used to store the statistic data is a Sorted Set. A Sorted Set does not allow duplicate members and the members are already ordered, which helps us in the statistics endpoint, because here we should return the data sorted.
The other option would be to sort the URL request count values in the Python layer, but as the specification mentioned that there would be millions of unique URLs, I decided that a Redis Sorted Set is the better solution.

### WSGI HTTP Server

Because the Flask’s built-in server is not suitable for production, I decided to start the Flask application with the WSGI HTTP Server "gunicorn".

Even though I know that this does not make much difference with my solution, because the test run function requests the API endpoint `/api/*` synchronously and directly in the API endpoint function.

### Development

For development the best option to run the API is the Flask built-in server which reloads on code changes.
To use the Flask development server instead of gunicorn you can make use of the [docker-compose.override.yml](https://docs.docker.com/compose/extends/#understanding-multiple-compose-files) feature

Therefore you need to run
```sh
cp docker-compose.override.yml.example docker-compose.override.yml
```
before starting the containers.

## Possible improvements

I really enjoyed working on this backend developer challange, but time is limited. Also you need my solution to evaluate it and to be able to decide if you want to move forward in the hiring process.

### Error handling

A big problem for a real world solution would be the missing error handling in all the API functions.

Adding error handling code would be crucial when putting such an API in production.
Espacially the error responses need to be consistent with all other APIs.

Open questions/topics:
* Which resonse status codes should we use for which error scenario
* Is there a general JSON error structure how we return error messages
* Make sure to not put too much information in the error messages and not leak customer information

### Tests (unit/integration)

Because I didn't use TDD (Test driven Development) for implementing this solution, I decided to skip writing test afterwards.

Of course, if we would deploy such an API to production, a test-suite with unit-tests and also integration tests is necessary.

Every developer should be able to run the tests locally. But the tests must also run in a CI/CD pipeline after every `git push`

### Linting/Formatting

Beside tests, also linting and formatting tools should run in the CI/CD pipeline. The pipeline must fail if the code does not meet the defined code quality criteria.

Possible tools to use:
* black
* flake8
* isort
* mypy
* bandit

For my solution I used all the above mentioned (except bandit) tool with the standard configuration locally to check and format my code.


### Logging / Tracing / Monitoring

Writing logging messages and/or use tools like [OpenTracing](https://opentracing.io/) or [Zipkin](https://zipkin.io/) is also missing in my solution, but is necessary to get an inside in the running production code.

Also I would add some healthcheck endpoints and some monitoring solutions (e.g: Prometheus, Grafana).
The healthcheck endpoint would be also necessary for Kubernetes to know if the API is already ready to receive requests.

### Async / TaskQueues

My current solution has a major weakness if you start a test run with a high number of requests.

As already mentioned in the solution overview, I just use `requests.get` in a loop and do not parallelize these URL requests.

To solve this problem we could use a task queue like Celery. Maybe your TaskTiger library could also be used, but I'm not familiar with this library yet.
Another option would be to use some async code and increase the API workers to parallelize the requests.

### Authentication / Security

API authentication would be also necessary for the API.

I'm not sure which Identity and Access Management solution you are using, but adding a solution like [Keyclaok](https://www.keycloak.org/), [authentik](https://goauthentik.io/), [ory](https://www.ory.sh/), [Okta](https://www.okta.com/) could be a good idea too.
But of course, there should be one single solution for all applications and APIs.

In my solution I use redis without authentication. This could also be a next step to increase the security of the API.

### General

Checking my solution again against the [Twelve-Factor App](https://12factor.net/) could also be an option.  
Espacially to look into the configuration options and not hard-code values like "port" (for Flask and Redis) in the Dockerfile or in the code itself.

Also I tried to keep the solution as simple as possible, which means that it would need some refactorings if the solution become larger in the future.  
Curently there is only one `app.py` module, but this could be split up in the future with more features. And with more Python modules the project structure would also need some changes to keep it clean.