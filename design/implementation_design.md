# Implementation Design
The Feeds service will be composed of a few components.
1. A database to store notifications.
2. An engine to handle notifications.
3. A queue to manage sending notifications through the engine to the database.
4. An API layer to:
  * Provide access for users to see their notifications.
  * Provide access for external services to create new notifications.

## Interactions
* Notifications are only created by services, NOT other users (at least, not yet).
* To create a notification, a service token is required. This will be validated against the auth service on each request.

From the Atom Activity Streams protocol, [here](https://www.w3.org/TR/activitystreams-core/) (see also [this article](https://hackernoon.com/getting-started-with-activity-stream-d7d5a528394c) for a brief summary), an activity has 4 main components: Actor Verb Object Target. For example, "User wjriehl shared Narrative 'My Fancy Metagenomics Work' with you." Here, we get:
* Actor - User wjriehl
* Type - shared
* Object - "My Fancy Metagenomics Work" (i.e. the narrative itself)
* Target - you, the user being notified.

As far as I can tell, the systems used by industry all do something similar, and each of the notifications described in the [product design](product_design.md) doc can be broken down in the same way.

These are intended to be mostly read-only, though they can have a pointer to a way to respond. For sharing narratives, it would be a link to a sharing interface. For maintaining groups, a link to the group management interface.

For our use, these should also be marked as "read" or "seen" or, for the requests, "finished".

## Structures
### `Notification`
* `id` - UUID or something similar
* `actor`
    * "who" is doing a thing (a user, org, or service)
    * must be a KBase user id
* `type` - what is the type of notification (share, invite, remove, job ...)
    * List of types TBD (but likely similar to the list [here](https://www.w3.org/TR/activitystreams-vocabulary/#activity-types) ). Following is a partial list that seems relevant
    * Invite
    * Accept
    * Reject
    * Share
    * Unshare
    * Join
    * Leave
    * Request
* `object` - what thing is the actor working with (a narrative, or job)
    * List of objects TBD, but the following should be included
    * Org/Group
* `target` - who is the actor doing this for (user or org) (optional - e.g. a job changing state isn't doing it to a user, or a maintenance notice isn't targeted)
* `source` - what service spawned the notification
* `level`
    * one of alert, error, warning, request
    * used for sorting / filtering
* `seen`
    * boolean
    * starts as false, toggled to true when returned in a search
    * can be toggled back to false on request

## API Interactions (not the official API, just actions that it should expose)


### Create notification
* One at a time.
* Requires actor, type, object, level.
* Requires a valid service token.
* Source can be inferred from the service token.
* Optional target.
* Returns 200 for ok, other codes as appropriate

### Get notifications
* Requires user token
* Requires number of notifications to get, default 10
* Optional time order, default is most recent
* Optional filters based on level, default is all
* Returns list of notifications
* All notifications returned are now marked as "seen"

### Unsee notifications
* Marks seen notifications as unseen
* Requires user token
* Requires list of notification ids
* Those in this list are marked as unseen

### Delete notification
* Removes notification from user's feed

### Respond to request
* Marks a request as responded to, along with the response
* Requires notification id
* Requires response - should be one of accepted or denied
