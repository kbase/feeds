### Notification
* handle plain string or structured note context
    * service-dependent
* subclass, or otherwise mark context for each service
    * avoid subclassing, so we don't need to modify feeds whenever a new service is added

### TimelineStorage
* abstract caching

### ActivityStorage
* caching to avoid lookups
* expire activities after configured time

### Build & Deployment
* Sphinx docs
* make service token and encrypt

### Server
* TESTS TESTS TESTS
* Mark seen / unseen
* options for admin usage
* Change from using configured admins -> auth roles
* Option to translate from document -> understandable text
* Option for free text when creating notification

### Test Interface
* make one.
* maybe jump straight into KBase-UI module.

### Actor
* validate actor properly
* include groups as an actor

### Object
* validate object of notification where appropriate
* context dependent

### Docs
* Do so, in general
* annotate deploy.cfg.example

### Context
* Make some reserved keys for the context
* "link" and "text" to start with

### UI
* bind submit new global note event
* add refresh to feeds (auto refresh on new global event)
* add optional service-spoof event
* better styles for notification rows
* add link out where appropriate