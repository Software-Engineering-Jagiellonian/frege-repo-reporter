# Frege Repo Reporter

Backend module for the repositories analytics system. 

## Endpoints

### Repository information

Service sends requests directly to the provider's API (currently only GitHub, 
but in the future potentially also from Gitlab, Bitbucket etc.) and extracts/modifies the data 
it returns. Then, returns the repository information as a JSON in the following format:
```
{
    "languages": {
        "<language_name>": <percentage_value>
    }, 
    "repositoryStatistics": {
        "<statistic>": <value>
    },
    "branches": [
        {
            "name": "<name>",
            "commits": [<commits>]
        }
    ]
}
```

### Files metrics

Metrics format returned by the endpoint:
```
{
    "<commit_hash>": {
        "<language_name>": {
            "<file_path>": {
                "<metric_name>": <value>
            }
        }
    }
}
```
By default, service gets currently available metrics from the database and returns 
them to the user in the above format. In case the `get_currently_available` 
parameter is set to `false`, service first checks if ALL metrics are available 
for specified commits and repository. Then:
- If yes, it returns the metrics for all files within specified commits and repository 
as a JSON in the above format.
- If no, it sends the message to the `download` queue in the following format:
```
{
    "repo_id": string,
    "languages": [int],
    "commits": [string]
}
```
that starts the chain of downloading, extracting and analyzing the files in 
the specified commits and repository.

## Building application into a docker image

To build the application into a docker image, run the following command 
in a directory where the Dockerfile is located:
```
docker build -t <name_of_the_image> .
```

## Environment variables

To run this application you need the following environment variables set:

- `RMQ_HOST` - RabbitMQ host
- `RMQ_PORT` - RabbitMQ port
- `RMQ_REJECTED_PUBLISH_DELAY` - number of seconds to wait between retrying sending output message
- `DB_HOST` - Postgres server host
- `DB_PORT` - Postgres server port
- `DB_DATABASE` - database name
- `DB_USERNAME` - database user name
- `DB_PASSWORD` - database user password

All of the above values are available in the `.env` file in a `frege-docker-compose` repository.

## Running the application in a docker container

Run this application in a docker container with the following command:

`docker run -it <name_of_the_image> <environmental variables>`

## Running as a Flask application directly

Run this as a Flask application with one of the following commands:

`python3 main.py`
or
`flask --app main --debug run`

## Authors

- Aleksander Profic https://github.com/aleksanderprofic
- Anna Profic https://github.com/annaprofic