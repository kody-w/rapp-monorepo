# Script: the WebSocket handshake in 40 seconds

Two voices: **ADA** asks, **MAX** explains. One presenter may read both parts.
Every factual line maps to a verified claim in `claims.json` (keys in
brackets); the reference read runs about 44 seconds before trims.

**ADA** [F01-L01]: How did web pages get live updates before WebSockets?

**MAX** [F01-L02]: By polling, which the WebSocket RFC calls an abuse of HTTP.

**MAX** [F01-L03]: RFC 6455 offers one TCP connection instead, carrying
traffic in both directions.

**ADA** [F02-L01]: So how does a WebSocket connection start?

**MAX** [F02-L02]: As an ordinary HTTP request that asks to upgrade: Upgrade
websocket, Connection Upgrade.

**MAX** [F02-L03]: It adds a random key, and asks for protocol version 13.

**ADA** [F02-L04]: And the server?

**MAX** [F02-L05]: If it accepts, it answers 101, Switching Protocols, with an
accept header.

**MAX** [F02-L06]: Any other status code, and HTTP semantics still apply.

**MAX** [F02-L07]: Then frames flow both ways, whenever either side wants.

## Reading notes

- Land the hook question cleanly; it is the first thing viewers hear.
- Read header names as spoken words ("Upgrade websocket, Connection Upgrade").
  The typing window shows their exact spelling.
- Pause briefly between lines; the editor cuts on those silences.
