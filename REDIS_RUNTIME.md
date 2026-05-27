# Redis Runtime

Redis is transient operational memory, not durable truth.

Responsibilities:

- websocket fanout.
- replay pacing coordination.
- bounded realtime buffering.
- subscriber isolation for scaled API workers.

Runtime classes:

- `RedisRuntime`
- `RedisEventBroadcaster`
- `RedisWebsocketSubscriber`

Security rule:

All runtime channels must use the `hermes:` namespace and must not contain whitespace.

