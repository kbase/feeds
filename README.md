# Feeds
A service to manage event feeds that will get served to KBase users.

docker run --name feeds-redis -v feeds_data:/data -p 6379:6379 -d redis redis-server --appendonly yes