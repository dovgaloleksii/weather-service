# Back End Tech Test

The purpose of this test is to assess your ability to create a simple service which consumes data from some backing services and returns a result by composing that data together.

Our chosen back end language is Go but it is OK to submit the solution to this test in another language if you are more familiar with it.
We have skills in house to make sense of Go, Python, Node.js, Ruby, Java, PHP or Elixir. If you want to use something not on that list please ask first.

The test will require you to write a very simple service (described below), a set of tests for said service and Docker containers for that service and its tests, which will be run using Docker compose.

## Startup command

For running service use:
```bash
docker-compose up
```

For running only test use:
```bash
docker-compose up test
```