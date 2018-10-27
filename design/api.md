# Feeds API doc

The KBase feeds service is HTTP-based, and uses the usual verbs. It's not strictly RESTful, but pretty close. Most of them require a valid auth token in the `Authorization` header, except where noted. These will be used to fetch notifications from the user's feed.

The focus here is on notifications - things that a user should know about fairly globally, but not necessarily have to react to. This is different from seeing a colleague's actions. That may come as a later project. Most of these require a valid KBase auth token in the header.

# Data Structures

## Notification structure
(see also the implementation_design doc)
```json
{
    "id" - a unique id for the notification
    "actor" - string
    "verb" - string
    "object" - string
    "target" - (optional) string
    "source" - string
    "level" - string, one of "alert", "error", "warning", "request"
    "seen" - boolean
    "context" - (optional) free text content object
    "created" - ISO 8601 datestamp when the notification was originally published.
    "expires" - ISO 8601 datestamp when the notification will expire and should be removed.
}
```

### Example:
A user might see a notification like:

`User "William Riehl" invited you to join group "Wild KBase Cowboys". Click here to accept.`  
This would be packaged up as the following structure:  
```json
{
    "id": <a UUID>,
    "actor": "wjriehl",
    "verb": "invite",
    "target": [<your user id>],
    "object": "Wild KBase Cowboys",
    "source": "groups",
    "level": "request"
}
```

Or, for an alert:  
`KBase maintenance is scheduled for January 25 at 11:00 am.`  
```json
{
    "id": <a UUID>,
    "actor": "kbase",
    "verb": "announce",
    "target": null,   # wouldn't be present
    "object": "maintenance",
    "source": "kbase",
    "level": "alert",
    "seen": true
}
```

# API

## Get global notifications
```
GET /notifications/global
```
Returns a list notifications visible to everyone, in order of when they were created. These are meant for major announcements, like KBase downtime. No authentication required.

This represents a "global" read-only feed. It's recommended for an admin to clear these occasionally.

## Get user notifications
```
GET /notifications
Authorization required
```
Returns notifications. By default, returns the most recent 10 unread notifications for that user of any type. This includes parameters for number, filtering, and sorting.

Parameters:
* `n`: integer > 0, max number of notifications to return
* `f`: string, filter notifications to return based on level. comma-delimited
* `rev`: reverse sort order for returned notifications if =1
* `seen`: include read notifications if =1

Examples:
* `GET /notifications/?n=100`  
Return the most recent 100 notifications

* `GET /notifications/?f=alert,request`  
Return notifications that are only at alert or request level.

* `GET /notifications/?rev=1`  
Return notifications in oldest first order.

* `GET /notifications/?seen=1`  
Include notifications that have already been seen.

## Get notification by id.
```
GET /notification/<notification id>
Authorization required for a user notification.
Authorization NOT required for a global notification.
```
Retrieves the notification with that id. If it's a global notification, then auth isn't required.

## Mark a notification seen
```
POST /notifications/see/<notification id>
Authorization required
```
Marks a single user notification seen. Has no effect on globals. The user is defined by the auth token used. If that notification is not on that user's feed it's ignored.

## Mark a list of notifications seen
```
POST /notifications/see
Authorization required
JSON Form data: array of notification ids.
```
Marks a list of notification ids as seen. Has no effect on globals. The user is defined by the auth token used. Any notifications not on that user's feed are ignored. 

## Mark a notification unseen
```
POST /notifications/unsee/<notification id>
Authorization required
```
Marks a single user notification unseen. Has no effect on globals. The user is defined by the auth token used. If that notification is not on that user's feed it's ignored.


## Mark a list of notifications unseen
```
POST /notifications/unsee
Authorization required
JSON Form data: array of notification ids.
```
Marks a list of notification ids as unseen. Has no effect on globals. The user is defined by the auth token used. Any notifications not on that user's feed are ignored. 



**`PUT /notification`**  
Adds a notification for a user. Requires a service token in the `Authorization` header (see the [auth2 documentation](https://github.com/kbase/auth2) for details). Requires adding info as JSON-encoded data with the following fields:
* `actor` - a user or org id.
* `type` - one of the type keywords (see below, TBD (as of 10/8))
* `target` - optional, a user or org id.
* `object` - object of the notice. For invitations, the group to be invited to. For narratives, the narrative UPA.
* `level` - alert, error, warning, or request.
* `content` - optional, content of the notification, otherwise it'll be autogenerated from the info above.
* `global` - true or false. If true, gets added to the global notification feed and everyone gets a copy.
