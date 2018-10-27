### Notification
* handle plain string or structured note context
    * service-dependent
* subclass, or otherwise mark context for each service
    * avoid subclassing, so we don't need to modify feeds whenever a new service is added

### NotificationFeed
* combine with global feed for maintenance, etc.

### NotificatonManager
* handle fanouts in a more consistent way

### TimelineStorage
* abstract caching
* filters on
    * seen
    * service
    * level
* add remove notification

### ActivityStorage
* caching to avoid lookups
* expire activities after configured time

### Build & Deployment
* build Dockerfile
* build DockerCompose file
* Dockerize
* Sphinx docs
* make service token and encrypt

### Server
* add params to GET notifications endpoint

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

