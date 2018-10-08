This is part of the Feeds work, but focused on the backend Feeds service. A more global design doc can be found here:
https://docs.google.com/document/d/1dR4xAPpXdc5rDYmeiUX-HOqs8dCuyNKrE8CEW6Jv0wE/edit#


# Feeds Design
This document describes the high level design for the Feeds service and what it should do. The goal is to provide a way to notify our users about events, including, but not limited to, the following:
* Jobs that have recently changed state (queued->running, running->completed).
* Narratives that have been shared.
* Data that has been shared.
* Data that has been uploaded or changed.
* Requests for Narrative sharing - critical for first implementation of Groups/Projects.
* Requests for Group membership (see also the Groups / Orgs document).
* Requests for data sharing through Groups.
* Global KBase notifications
* App version updates
* Data object version updates

# Components
Along with this service, other KBase components will need to be updated to handle feeds. These include:
* Workspace service
    - Update to push events into Feeds
* Dashboard
    - Add a feeds viewer
* Narrative
    - Update to push events
    - Add a small viewer for notifications
* Job service
    - Update to push job state changes into Feeds

# Work
The absolute barest minimum MVP should be a feeds interface that tells when a Narrative has been shared with you, or when a shared Narrative has been updated. If we take the time to design this interface and the feeds service well, it will be possible to add other feed events without much trouble.

## Service Design Properties
* A "Feed" sends "Notifications" to users, which are visible in ways defined by the UI.

## Notification Properties
* It can have a state of read, unread, or marked for deletion.
* Once deleted, a Notification cannot be recovered.
* Has a list of users that can see it.
* Each user gets their own unique copy of the Notification; deleting one has no effect on the others.
* A notification can have one or more links to other pages.
* A notification has a "level" that defines how it should be received. These levels should be:
  * Alert - something happened, but nothing to respond to.
    * A job changing state.
    * An app that you have favorited has been updated.
    * A Narrative has been shared with you.
    * A Narrative that you had access to is no longer shared with you.
    * A Narrative you own but have shared with others has been shared with a new user.
    * A user has joined a group you are in.
    * A user has left a group you are in.
  * Error - something unrecoverably bad happened.
    * An app entered an error state.
  * Warning - something significant happened you really should be aware of.
    * A Narrative you own has been shared by someone else.
    * Upcoming KBase maintenance or downtime.
  * Request - something happened, requiring user intervention. These should be accompanied by a way to resolve that request, whether it's an inline form, or a link to a Narrative or Group management page.
    * A request to be added to a group.
    * An invitation to join a group.
    * A request to add/remove a workspace to/from a group.
    * A request to share a Narrative.
    * A request to accept ownership of a group.
* A notification has an icon that is set based on its type.
* A notification can have an optional "category", linked to the source that created it.
  * narrative or workspace for data
  * job
  * app -> app updates, releases, etc.
  * social -> groups, sharing, etc.
  * catalog -> for admin requests and responses ("Your request to release X module has been approved")
* A notification response can be decided by the service that creates the notification. Responses include:
  * Approve/Deny a sharing request
  * Approve/Deny a group invite
  * Approve/Deny a group request to add/remove a Narrative

## Feed Properties
* As of this design, users will have a single feed that gets populated with all notifications.
* Feeds are sortable and filterable by:
  * Most recent and unread
  * Type (alert, error, warning, request)
  * Most "urgent" - should move requests to the top, then errors, warnings, and alerts.

## Stretch Properties
* Users can configure certain notifications to be sent via email.
  * This will require a TON of extra work, including an email service, email verification through auth, additional account configuration options, and testing of everything. It should be put off for a good long time. Who uses email anymore anyway?

