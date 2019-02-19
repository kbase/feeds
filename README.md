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
See the Makefile to change the number of `gunicorn` workers. (Default=5).

## Run tests
1. Install Python dependencies (just run `make install` as above).
2. Install MongoDB on your system. 
3. In `test/test.cfg` set the `mongo-exe` key (in the `[test]` section) to the location of your `mongod` executable. On a Linux / MacOS system, you can find this with `which mongod`. You're on your own with Windows.
4. Finally, run tests with:
```
make test
```


## API
(see [the API design doc](design/api.md) for details, also see below.)
### Data Structures

**Entity**
An Entity structure defines, loosely, an entity related to a notification. This will make more sense below in the Notification object, but Entities are all of the actors in the notifications, the objects of each notification, users who receive the notification, and targets of the notification. For example, in the notification defined by the phrase:  
```
User "wjriehl" invited user "some_other_user" to join the group "Bill's Fancy Group".
```
There are 3 entities:  
1. wjriehl is an entity of type user
2. some_other_user is an entity of type user
3. Bill's Fancy Group is an entity of type group
These are used as a vocabulary to strictly control what's meant in the notification structure.

The types currently supported are:
* user - id should be a user id
* group - id should be a group id
* workspace - id should be a workspace id
* narrative - id should be a workspace id (maybe an UPA if needed)
* job - id should be a job id string

**Entity**
```
{
    "id": string - an id for this notification, defined by context,
    "type": string - what type of entity this is. Allowed values below.
    "name": string (optional) - the full name of this entity (not stored, as its possible it could change)
}
```

**Notification**
```
{
    "id": string - a unique id for the notification,
    "actor": Entity - the Entity who triggered the notification (mostly a user),
    "verb": string - the action represented by this notification (see list of verbs below),
    "object": Entity - the object of the notification,
    "target": list(Entity) - the target(s) of the notification,
    "source": string - the source service that created the notification,
    "level": string, one of alert, error, warning, request,
    "seen": boolean, if true, then this has been seen before,
    "created": int - number of milliseconds since the epoch, when the notification was created,
    "expires": int - number of milliseconds since the epoch, when the notification will expire, and will no longer be seen.
    "external_key": string - (optional) a external key that has meaning for the service that created the notification. Meant for use by other services.
    "context": structure - (optional) a (mostly) freely open structure with meaning for the service that created it. The special keys `text` and `link` are intended to be used by the front end viewers. A `link` becomes a hyperlink that would link to some relevant place. `text` gets interpreted as the intended text of the notification, instead of automatically generating it.
    "users": list(Entity) - the user(s) who should see the notification. If that user is a group, then all members of the group will see it.
            Note that when returned from the server for user consumption, this will not be found, for some attempt at privacy.
}
```

### Service info
Returns some basic service info. The current time, the service name and version.
* Path: `/`
* Method: `GET`
* Required headers: none
* Returns:
```
{
    "servertime": <millis since epoch>,
    "service": "Notification Feeds Service",
    "version": "1.0.0" 
}
```

### Permissions
Returns the allowed endpoints based on the passed authentication header. This will vary, depending on the user or service making the call. For example, a user can only GET their notifications, while a Service can POST notifications.
* Path: `/permissions`
* Method: `GET`
* Required headers: either nothing, or `Authorization`
* Returns:
```
{
    "token": {
        "user": <user id>,
        "service": null or the name of the service if it's a token with type = Service,
        "admin": true if the user has the "FEEDS_ADMIN" custom role
    },
    "permissions": {
        "GET": [ list of paths available with the GET method ],
        "POST": [ list of paths available with the POST method ]
    }
}
```

### List of API functions
Returns the visible endpoints for the feeds API.
* Path: `/api/V1`
* Method: `GET`
* Required headers: none
* Returns a key-value pair object where the keys give some semantic meaning to the paths, and the values are the paths themselves (without the required `/api/V1` part). E.g.:
```
{
    "add_notification": "POST /notification",
    "get_notifications": "GET /notifications",
    ... etc.
}
```

### Get a notification feed
Returns the feed for a single user. This feed is an ordered list of Notifications (see the structure above). It's separated into two parts that are returned at once - the global feed (global notifications set by admins that are intended for all users), and the user's feed with targeted notifications.

Options are included to filter by level, source, whether a notification has been seen or not, and the order in which it was created.
* Path: `/api/V1/notifications`
* Method: `GET`
* Required header: `Authorization`
* URL parameters:
    * `n` - the maximum number of notifications to return. Should be a number > 0. `default 10`
    * `rev` - reverse the chronological sort order if `1`, if `0`, returns with most recent first
    * `l` - filter by the level. Allowed values are `alert`, `warning`, `error`, and `request`
    * `v` - filter by the verb used. Allowed values are listed below under "Create a new notification", and include `invite`, `request`, `shared`, etc.
    * `seen` - return all notifications that have also been seen by the user if this is set to `1`.

* Returns structure with 2 feeds:
```
{
    "global": {
        "name": <full name of feed>,
        "unseen": <number unseen>,
        "feed": [ array of global notifications ]
    },
    "user": {
        "name": <full name of user>,
        "unseen": <number unseen>,
        "feed": [ array of user's notifications ]
    }
}
```
#### Examples
**Get 10 most recent notifications**
```sh
curl -X GET
     -H "Authorization: <auth token>"
     https://<service_url>/api/V1/notifications
```
returns
```
{
    "global": {
        "name": <name>,
        "unseen": <number unseen>,
        "feed": [{note 1}, {note 2}, ...]
    },
    "user": { structure as above }
}
```
(they all return a structure like that, so the return is omitted for the remaining examples)

**Get unseen notifications**
```sh
curl -X GET
     -H "Authorization: <auth token>"
     https://<service_url>/api/V1/notifications?seen=1
```

**Get up to 50 unseen notifications with verb "share" and level "warning"**
```sh
curl -X GET
     -H "Authorization: <auth token>"
     https://<service_url>/api/V1/notifications?seen=0&n=50&v=share&l=warning
```

### Get count of unseen notifications
Doesn't return the notifications at all, just how many unseen ones there are for the given user. Should be pretty performant, and certainly light on data transfer.
* Path: `/api/V1/notifications/unseen_count`
* Method: `GET`
* Required header: `Authorization`
* Returns: a JSON object with an "unseen" key. This key is a small structure with "user" and "global" keys, where the values of those are the number of unseen notifications in each. For the user feed, this is summed across all feeds the user is subscribed to.
* Possible errors:
    * 401 Not Authenticated - If an auth token is not provided.
    * 403 Forbidden -If an invalid auth token is provided.

### Get a single notification
If you have the id of a notification and want to get its structure, just add it to the path. This will search the user's feed for that notification. If present on the user's feed, it will be returned. If not present, or if this notification cannot be seen by the user, this will raise a "404 Not Found" error.
* Path: `/api/V1/notification/<note_id>`
* Method: `GET`
* Required header: `Authorization`
* Returns: a JSON object with a "notification" key where the value is the requested Notification.
* Possible errors:
    * 404 Not Found
        * If the notification does not exist.
        * If the notification is real but does not exist in the user's feed.
    * 401 Not Authenticated - If an auth token is not provided.
    * 403 Forbidden - If an invalid auth token is provided.

### Get global notifications
To just return the list of global notifications, use the global path. It returns only a list of notifications in descending chronological order (newest first).
* Path: `/api/V1/notifications/global`
* Method: `GET`
* Required header: none
* Returns: a list of Notifications

### Get a single notification from an external key
**(debug method)**  
This is meant for services to debug their use of external keys. A service that created a notification with an external key can fetch that notification using that key and the auth token that created it (i.e. the proof it came from that service). As in getting a notification above, this returns a JSON object with a "notification" key and a single notification attached to it. Also, in contrast to the method above, this returns the entire Notification document as stored in the database (including the list of users it is intended for and whether they've marked it as seen).
* Path: `/api/V1/notification/external_key/<key>`
* Method: `GET`
* Required header: `Authorization`
* Returns: a JSON object with a "notification" key where the value is the requested Notification. This includes extra data that's stored in the database as well, but not usually available to users.
* Possible errors:
    * 404 Not Found - If the notification does not exist with that combination of external key and source.
    * 401 Not Authenticated - if no auth token is provided.
    * 403 Forbidden - If the token is invalid, or not a Service token.

### Create a new notification
Only services (i.e. those Authorization tokens with type=Service, as told by the Auth service) can use this endpoint to create a new notification. This requires the body to be a JSON structure with the following available keys (pretty similar to the Notification structure above):
* `source` - required, this is the source service of the request.
* `actor` - required, should be a valid Entity
* `object` - required, the object of the notice (the workspace being shared, the group being invited to, etc.)
* `verb` - required, the action implied by this notice. Currently allowed verbs are:
    * invite / invited
    * accept / accepted
    * reject / rejected
    * share / shared
    * unshare / unshared
    * join / joined
    * leave / left
    * request / requested
    * update / updated
* `level` - optional (default `alert`), the level of the request. Affects filtering and visual styling. Currently allowed values are:
    * alert
    * warning
    * error
    * request
* `target` - optional, but if present should be a list of Entities - the targets of the notification
* `expires` - optional, an expiration date for the notification in number of milliseconds since the epoch. Default is 30 days after creation.
* `external_key` - optional, a string that can be used to look up notifications from a service.
* `context` - optional, a key-value pair structure that can have some semantic meaning for the notification. "Special" keys are `text` - which is used to generate the viewed text in the browser (omitting this will autogenerate the text from the other attributes), and `link` - a URL used to craft a hyperlink in the browser.
* `users` - optional, a list of Entities that should receive the notification (limited to users and groups). This list will be automatically augmented by the service if necessary. E.g. if a workspace is the object of the notification, then the workspace admins will be notified.

**Usage:**
* Path: `/api/V1/notification`
* Method: `POST`
* Required header: `Authorization`
* Returns:
```
{"id": <the new notification id>}
```
**Example**
```python
import requests
note = {
    "actor": {
        "id": "wjriehl",
        "type": "user"
    },
    "source": "workspace",
    "verb": "shared",
    "object": {
        "id": "30000",
        "type": "workspace"
    },
    "target": [{
        "id": "gaprice",
        "type": "user"
    }],
    "context": {
        "text": "User wjriehl shared workspace 30000 with user gaprice."  # this can also be auto-generated by the UI.
    }
}
r = requests.post("https://<service_url>/api/V1/notification", json=note, headers={"Authorization": auth_token})
```
would return:
```python
{"id": "some-unique-id-for-the-notification"}
```

### Mark notifications as seen
Takes a list of notifications and marks them as seen for the user who submitted the request (does not currently affect global notifications). If the user doesn't have access to a notification in the list, it is marked as unauthorized in the return structure, and nothing is done to it.
* Path: `/api/V1/notifications/see`
* Method: `POST`
* Required header: `Authorization`
* Expected body:
```
{
    "note_ids": [ list of notification ids ]
}
```
* Returns:
```
{
    "seen_notes": [ list of seen notification ids ],
    "unauthorized_notes": [ list of notification ids that the user doesn't have access to ]
}
```

### Mark notifications as unseen
Takes a list of notifications and marks them as unseen for the user who submitted the request (does not currently affect global notifications). If the user doesn't have access to a notification in the list, it is marked as unauthorized in the return structure, and nothing is done to it.
* Path: `/api/V1/notifications/unsee`
* Method: `POST`
* Required header: `Authorization`
* Expected body:
```
{
    "note_ids": [ list of notification ids ]
}
```
* Returns:
```
{
    "unseen_notes": [ list of seen notification ids ],
    "unauthorized_notes": [ list of notification ids that the user doesn't have access to ]
}
```

### Expire a notification right away
This effectively deletes notifications by pushing their expiration time up to the time this request is made.
* Path: `/api/V1/notifications/expire`
* Method: `POST`
* Required header: `Authorization` - requires a service token.
* Expected body:
```
{
    "note_ids": [ list of notification ids ],
    "external_keys": [ list of external keys ],
    "source": source string for the notification
}
```
At least one of the "note_ids" or "external_keys" keys must be present. Source must always be present.
* Returns:
```
{
    "expired": {
        "note_ids": [ list of expired notification ids ],
        "external_keys": [ list of expired notifications by external key ]
    },
    "unauthorized": {
        "note_ids": [ list of not-expired note ids ],
        "external_keys": [ list of not-expired external keys ]
    }
}
```
This will include all of the ids passed to the endpoint, put into one category or the other. Any that were "unauthorized" either don't exist, or came from a different service than the given auth token.


## Admin API
These methods are intended for Administrator use only. Any auth token that posts this must come from a user with the "FEEDS_ADMIN" custom auth role (see the [auth docs](https://github.com/kbase/auth2) for details)

### Post a global notification
Functions just as a service would create a new notification, but specialized. This is intended for admins to create a notice that all users should see, whether it's for maintenance, or an upcoming webinar, or something else. As such, there's no target user group, as everyone should be targeted. As in the notification posting method above, it requires a JSON document as the body of the request, with the following fields:
* verb - required
* object - required
* level - required (default alert)
* context - optional, but `text` is STRONGLY recommended.

**Usage:**
* Path: `/admin/api/V1/notification/global`
* Method: `POST`
* Required header: `Authorization` - must have the `FEEDS_ADMIN` role
* Returns: 
```
{"id": <the new notification id>}
```

### Expire any notification
This effectively deletes notifications by pushing their expiration time up to the time this request is made.
* Path: `/admin/api/V1/notifications/expire`
* Method: `POST`
* Required header: `Authorization` - must have the `FEEDS_ADMIN` role
* Expected body:
```
{
    "note_ids": [ list of notification ids ],
    "external_keys": [ list of external keys ],
    "source": source string for the notification
}
```
At least one of the "note_ids" or "external_keys" keys must be present. If external_keys is present here, then
source must be present - both the external key and the source of that key are used to find the notification to expire.
* Returns:
```
{
    "expired": {
        "note_ids": [ list of expired notification ids ],
        "external_keys": [ list of expired notifications by external key ]
    },
    "unauthorized": {
        "note_ids": [ list of not-expired note ids ],
        "external_keys": [ list of not-expired external keys ]
    }
}
```
This will include all of the ids passed to the endpoint, put into one category or the other. Any that were "unauthorized" either don't exist, or came from a different service than the given auth token.
