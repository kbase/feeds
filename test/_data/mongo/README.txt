Test data for testing notification feeds.

notifications.json has a list of notifications. The "users" who can see those
are all named "test_user" (test_user, test_user2, test_user3, etc.). There
should be enough notifications there to do some fairly broad testing with
various filters and such, as follows:

test_user
* 10 total notifications
* default chronological order = order of ids (1-10)
* 8-10 have been seen by test_user
* verb usage:
    * 1,2 = verb 1
    * 3,4,5 = verb 2
    * 6,7,8 = verb 3
    * 9,10 = verb 4
* level usage:
    * 1,2,3 = level 1
    * 4,5,6 = level 2
    * 7,8,9 = level 3
    * 10 = level 4
* all actors are kbasetest
* source usage:
    * 1,2,3,4,5 = ws
    * 6,7,8,9,10 = groups
* all targets are test_user
* users usage:
    * 1-10 all have test_user
    * 6-10 have test_user2
    * 8,9,10 have test_user3
* external key:
    * 1,2,3 have external keys