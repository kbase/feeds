# Feeds
A service to manage event feeds that will get served to KBase users.

## Install
This is a Flask-based service, so you'll need to build the environment and start the server.
```
make install
```
Under the hood, this uses pip to install the requirements in `requirements.txt` and `dev-requirements.txt`.

## Start the server
Easy enough.
```
make start
```
This starts a server on port 5000.
See the Makefile to change the number of `gunicorn` workers. (Default=17).

## Run tests
After installing dependencies in your environment, run
```
make test
```


## API
(see [the API design doc](design/api.md) for details)
### Data Structures

**Notification**
```
{
    "id": string - a unique id for the notification
    "actor": string - the actor who triggered the notification
    "verb": string - the action represented by this notification (see list of verbs)
    "object": string - the object of the notification
    "target": list - the target(s) of the notification

* `id` - a unique id for the notification
* `actor`
* `type`
* `object`
* `target` - (optional)
* `source` - source service
* `level` - alert, error, warning, request
* `seen`
* `content` - (optional) free text content string
* `published` - ISO 8601 datestamp when the notification was originally published.
* `expires` - ISO 8601 datestamp when the notification will expire and should be removed.
```
`GET /api/V1/notifications`
