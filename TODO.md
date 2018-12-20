### Service
* Option to translate from feed document -> understandable text on server side
* include groups as an actor, target, object
* annotate config examples
* Make some reserved keys for the context
    * "link" and "text" to start with
* Connect service to Kafka to get notifications into the DB
* Add lookup of total unexpired notes / total unread notes
* Add categorization of lookups for each feed
    * groups
* Add "pagination" - rather, a form of skip.
    * first, and total to return

### UI
* Create tabs for each group a user belongs to
* Keep ability to toggle seen/unseen
    * Other sites just always show things in order, with some decoration if they're unseen. That decoration fades.
    * Gonna try having a solid border, with pale fill. After some time fill should fade to white.
    * Modeled on LinkedIn, Facebook, Twitter
* Date/time input area instead of timestamp for global notes


Kafka input data structure
~/kafka/2.1.0/kafka_2.11-2.1.0$ bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic feeds --from-beginning
{
    "operation":"cancel",
    "source":"groupsservice",
    "external_ids":["5a78c8d7-b960-45ed-ac43-30536b2b6102"]
}
{
    "actor":"junkypants",
    "external_key":"016da4f5-68db-41a8-b68d-5693e6ee634f",
    "expires":1545948030466,
    "level":"request",
    "verb":"request",
    "context":{"resourcetype":"user"},
    "source":"groupsservice",
    "operation":"notify",
    "users":["gaprice"],
    "target":["junkypants"],
    "object":"i"
}
