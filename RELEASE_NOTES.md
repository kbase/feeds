KBase Feeds Service

### Version 1.0.2
- Add a cache for bad tokens so they aren't looked up over and over. Maxes out at 10000, then throws out the oldest bad token.

### Version 1.0.1
- Fix issue where groups notifications were being seen by users in the target field as well as the users list.

### Version 1.0.0
- First public release!
- Supports adding notifications from other KBase services.
- Notifications are sent directly to users, no subscription model yet.
- Notifications can also be binned into groups.
- See README.md for API details.
