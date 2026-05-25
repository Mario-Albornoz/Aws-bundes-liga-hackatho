# Bundesliga Live Match Experience

A full-stack, real-time football match viewer with social watch-party chat, DVR replay, and in-play betting. The backend replays anonymised DFL (German Football League) XML feeds at configurable speed, processes match events through a handler pipeline, and serves multiple WebSocket streams. The frontend renders player and ball positions on a live 3D pitch and lets users place bets, chat with friends, and scrub back through the match.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Variables](#environment-variables)
3. [Architecture Overview (L2)](#architecture-overview-l2)
4. [Feed Simulator](#feed-simulator)
5. [Feed Handler & Event Pipeline](#feed-handler--event-pipeline)
6. [WebSocket Streams](#websocket-streams)
7. [Caching Strategy — Redis & In-Memory](#caching-strategy--redis--in-memory)
8. [REST API Reference](#rest-api-reference)
9. [Frontend Architecture](#frontend-architecture)
10. [Running Tests](#running-tests)
11. [Debug & Testing Tools](#debug--testing-tools)

---

## Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| Redis | 7+ (running locally or remote) |
| Expo CLI | latest (`npm i -g expo-cli`) |

> **Match data** — The XML files (`Events_Anonym.xml`, `Positions_Bayern_Hamburg.xml`) are large and gitignored. Place them under `backend/data/` before starting the backend.

---

### 1. Start Redis

```bash
# macOS (Homebrew)
brew services start redis

# or run directly
redis-server

# Verify
redis-cli ping   # → PONG

# Stop when done
brew services stop redis
```

---

### 2. Backend

```bash
cd backend

# Create and activate virtualenv
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env — at minimum set REDIS_URL and JWT_SECRET_KEY (see Environment Variables below)

# Start the server
uvicorn main:app --reload --reload-dir . --host 0.0.0.0 --port 8000
```

> **Tip:** `--reload-dir .` constrains the file watcher to your app source and prevents spurious reloads caused by changes inside `venv/`.

---

### 3. Frontend

```bash
cd frontend

npm install

# Configure environment
cp .env.template .env
# Set EXPO_PUBLIC_API_BASE_URL and EXPO_PUBLIC_WS_URL
# When testing on a physical device over Wi-Fi, replace `localhost`
# with your machine's LAN IP (e.g. http://192.168.1.42:8000)

npm start          # interactive menu
# or
npm run ios        # iOS simulator
npm run android    # Android emulator
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | *(required)* | Redis connection string, e.g. `redis://localhost:6379` |
| `JWT_SECRET_KEY` | *(required)* | Random hex string. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `MATCH_ID` | `DFL-MAT-111111` | Match identifier embedded in all WS messages |
| `EVENT_BUFFER` | `200` | Ring-buffer depth for the event broadcaster |
| `EVENT_QUEUE_SIZE` | `50` | Per-client async queue depth (events) |
| `POSITIONAL_BUFFER` | `2500` | Ring-buffer depth for the positional broadcaster |
| `POSITIONAL_QUEUE_SIZE` | `250` | Per-client async queue depth (positional frames) |
| `CHUNK_SIZE` | `500` | XML rows loaded per batch |
| `REPLAY_CHUNK_SIZE` | `25` | Positional frames stored as one Redis chunk **(must match frontend)** |
| `REPLAY_FRAME_INTERVAL` | `0.04` | Seconds between frames at 1× speed **(must match frontend)** |
| `REPLAY_STREAM_TTL` | `10800` | Seconds before replay data expires in Redis (3 h) |
| `REPLAY_IDLE_POLL_INTERVAL` | `0.1` | Poll interval when replay catches up to live edge |
| `REPLAY_IDLE_LIMIT` | `50` | Consecutive idle polls before replay stream ends |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_API_BASE_URL` | `http://localhost:8000` | HTTP base URL |
| `EXPO_PUBLIC_WS_URL` | `ws://localhost:8000` | WebSocket base URL |
| `EXPO_PUBLIC_REPLAY_CHUNK_SIZE` | `25` | Must equal backend `REPLAY_CHUNK_SIZE` |
| `EXPO_PUBLIC_REPLAY_FRAME_INTERVAL_SEC` | `0.04` | Must equal backend `REPLAY_FRAME_INTERVAL` |
| `EXPO_PUBLIC_REPLAY_SKIP_SECONDS` | `10` | How far the skip buttons jump |

---

## Architecture Overview (L2)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            EXPO (React Native)                              │
│                                                                             │
│  ┌─────────────┐  ┌──────────────────┐  ┌───────────────────────────────┐  │
│  │  PitchCanvas │  │   ChatOverlay    │  │       BetStatusDashboard      │  │
│  │  (Three.js) │  │ (rooms · chat)   │  │  (my bets · settlement feed)  │  │
│  └──────┬──────┘  └────────┬─────────┘  └──────────────┬────────────────┘  │
│         │                  │                            │                   │
│  ┌──────┴──────┐  ┌────────┴─────────┐  ┌──────────────┴────────────────┐  │
│  │ usePositional│  │  useChatStream   │  │  ApiContext · BetSettlement   │  │
│  │    Stream   │  │  /chat-room/stream│  │        Socket /bets/stream    │  │
│  └──────┬──────┘  └────────┬─────────┘  └──────────────┬────────────────┘  │
│  ┌──────┴──────────────────┴────────────────────────────┴────────────────┐  │
│  │                       useReplayStream · MatchTimeline (DVR)           │  │
│  └─────────────────────────────────────────────────────────────────────-─┘  │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │  HTTP + WebSocket
┌────────────────────────────────────▼────────────────────────────────────────┐
│                          FastAPI  (main.py)                                 │
│                                                                             │
│  /auth   /bets   /bets/debug   /chat-room   /replay   /events   /positional │
│                                                                             │
│  ┌──────────────────────────┐   ┌──────────────────────────────────────────┐│
│  │     Feed Simulator       │   │           Feed Handler                   ││
│  │                          │   │                                          ││
│  │  EventSimulator ─────────┼──►│  FeedConsumer                           ││
│  │    Events_Anonym.xml     │   │    ├─ BetPublishingHandler               ││
│  │                          │   │    │    └─ BetRuleEngine                 ││
│  │  PositionalSimulator ────┼──►│    │         └─ BetNotifier              ││
│  │    Positions_*.xml       │   │    ├─ BetProcessingHandler               ││
│  │                          │   │    └─ MatchResultBetHandler              ││
│  │  BaseBroadcaster         │   │                                          ││
│  │  (ring buffer + queues)  │   │  PositionalFeedConsumer                  ││
│  │    EventBroadcaster      │   │    └─ ReplayHandler → Redis Stream       ││
│  │    PositionalBroadcaster │   │                                          ││
│  └──────────────────────────┘   └──────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────┐   ┌───────────────────────────────────────────┐│
│  │    BetOpportunityStore  │   │         ConnectionManager (in-memory)     ││
│  │    (in-memory, per type)│   │         room_id → [WebSocket, ...]        ││
│  └─────────────────────────┘   └───────────────────────────────────────────┘│
│                                                                             │
│  ┌──────────────────────────────┐   ┌─────────────────────────────────────┐ │
│  │  BetSettlementNotifier       │   │     DatabaseManager (SQLite)        │ │
│  │  user_id → [WebSocket, ...]  │   │     users · balances                │ │
│  └──────────────────────────────┘   └─────────────────────────────────────┘ │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │
              ┌─────────────────────────▼──────────────────────────┐
              │                     Redis                          │
              │                                                    │
              │  bet:{id}                 Bet document (JSON)      │
              │  user_id:{uid}            Set of bet IDs           │
              │  chat:room:{id}           Room metadata            │
              │  chat:room:{id}:messages  Message history (List)   │
              │  chat:ws_token:{tok}      One-time WS token (30 s) │
              │  auth:refresh:{hash}      Refresh token (7 d)      │
              │  replay:{match}:frames    Positional chunks (Stream)│
              └────────────────────────────────────────────────────┘
```

---

## Feed Simulator

The feed simulator replays anonymised DFL XML files as live WebSocket streams, making it possible to develop and demo the app without a live feed subscription.

### How it works

1. **Data loading** — `EventSimulator` parses `Events_Anonym.xml` sequentially. `PositionalSimulator` loads `Positions_Bayern_Hamburg.xml` into an in-memory SQLite table for fast sequential reads.

2. **Timing** — Each event or frame has a real-world timestamp. The simulator calculates the gap to the next item, divides by `speed`, and sleeps accordingly. A `speed` of `60` plays back a 90-minute match in 90 seconds.

3. **Broadcasting** — Both simulators push items into a `BaseBroadcaster`:
   - An **in-memory ring buffer** stores the last N items so late-connecting clients can catch up.
   - A **per-client async queue** decouples the producer from each consumer so slow clients don't block fast ones.
   - The `BroadcastRegistry` ensures a single broadcaster per `match_id` regardless of how many clients connect.

4. **Message envelope** — Every message is wrapped as `WSServerMessage`:
   ```json
   { "type": "event|positional|match_start|match_end|heartbeat", "seq": 42, "match_id": "...", "payload": { ... } }
   ```

5. **Internal consumers** — When the first client connects to `/events/stream`, `EventBroadcastRegistry` creates a `FeedConsumer` that subscribes to the broadcaster's internal queue (no WebSocket) and runs the bet handler pipeline on every event. `PositionalBroadcastRegistry` similarly creates a `PositionalFeedConsumer` that feeds the DVR replay cache.

### Supported event types

`KickOff`, `FinalWhistle`, `Substitution`, `ShotAtGoal`, `SuccessfulShot`, `Tackle`, `Foul`, `YellowCard`, `RedCard`, `GoalKick`, `ThrowIn`, `CornerKick`, `FreekickSituation`, `SavedShot`, `Offside`, and more — all sourced from the DFL schema.

---

## Feed Handler & Event Pipeline

The feed handler decouples bet logic from broadcasting. It runs as a background consumer on the same internal broadcaster queue, so bet processing is completely invisible to WebSocket clients.

### Handler base class

Every handler implements `AbstractHandler`:

```python
class AbstractHandler:
    async def handle(self, event: MatchEvent) -> None: ...
    async def complete(self) -> None: ...   # called at end of stream
```

### Pipeline (in order)

```
FeedConsumer
 │
 ├─► BetPublishingHandler
 │     BetRuleEngine evaluates each event:
 │       Substitution   → SubstitutionBetOpportunity (30 s window)
 │       KickOff (1st)  → MatchResultBetOpportunity  (90 min window)
 │     BetNotifier saves to BetOpportunityStore + broadcasts to
 │       all chat-room sockets and all /bets/stream sockets
 │
 ├─► BetProcessingHandler  [bet_type = substitution]
 │     Substitution event → PENDING → ACTIVE  (sub-in player matches bet)
 │     SuccessfulShot     → ACTIVE  → SUCCESS (scorer matches player)
 │     FinalWhistle (2nd) → ACTIVE  → FAILED  (never scored)
 │     Updates Redis, adjusts SQLite balance, notifies user via WS
 │
 └─► MatchResultBetHandler  [bet_type = match_result]
       KickOff (2nd half) → all PENDING → ACTIVE
       FinalWhistle (2nd) → parse score, settle each ACTIVE bet
                            winner team → SUCCESS (+balance)
                            loser team  → FAILED  (no change)
```

### Why a pipeline?

Adding a new bet type only requires writing a new `AbstractHandler` and registering it in `EventBroadcastRegistry`. The broadcaster, WebSocket routing, and Redis plumbing are unchanged.

---

## WebSocket Streams

The backend exposes five WebSocket endpoints. Each serves a different purpose and targets a different part of the frontend.

---

### `WS /positional/stream?speed=&seq=`

**Purpose:** Live match view — player and ball positions in real time.

**Client receives:**
```json
{ "type": "positional", "seq": 1042, "match_id": "...",
  "payload": { "frame_n": 1042, "match_id": "...", "players": [...], "ball": {...} } }
```
Each frame contains x/y/z coordinates for every tracked player and the ball.

**Client sends:** `{ "type": "pause" }` / `{ "type": "resume" }` to throttle playback.

**Used by:** `usePositionalStream` → `PitchCanvas`.

---

### `WS /events/stream?speed=&seq=`

**Purpose:** Raw match event feed — commentary, betting triggers.

**Client receives:** Wrapped `MatchEvent` objects (substitutions, goals, cards, whistles, …).

**Side effect (invisible to client):** Triggers the bet handler pipeline on the server side.

**Used by:** Available for client consumption; currently used internally for bet processing.

---

### `WS /chat-room/stream?room_id=&ws_token=`

**Purpose:** Social watch-party — real-time chat within a room, plus bet opportunity delivery for users who entered via a chat room.

**On connect the server pushes:**
1. Full Redis message history for the room
2. All currently active `BetOpportunity` objects from `BetOpportunityStore`
3. A `user_joined` broadcast to all room members

**Client receives:**
```json
{ "type": "chat_message", "sender_id": "1", "content": "What a save!", "timestamp": "..." }
{ "type": "user_joined", "user_id": "1" }
{ "type": "bet_opportunity", "opportunity": { "bet_type": "match_result", ... } }
```

**Client sends:**
```json
{ "sender_id": "1", "content": "let's go!", "timestamp": "..." }
```

**Authentication:** `ws_token` is a one-time 30-second Redis token minted by `POST /chat-room/join`. It is deleted on first use.

**Used by:** `useChatStream` → `ChatOverlay`.

---

### `WS /bets/stream?user_id=`

**Purpose:** Per-user bet lifecycle — the primary channel for bet opportunity delivery and settlement notifications.

**On connect the server pushes:**
1. `bet_snapshot` — complete list of the user's current bets
2. One `bet_opportunity` message per active unexpired opportunity in `BetOpportunityStore`

**Server pushes at runtime:**
| Message type | Trigger |
|---|---|
| `bet_opportunity` | New opportunity published (via `BetNotifier`) |
| `bet_updated` | Bet transitions PENDING → ACTIVE |
| `bet_settled` | Bet transitions ACTIVE → SUCCESS / FAILED |
| `bet_snapshot` | User places a new bet (updated snapshot) |

**Used by:** `ApiContext` (auto-connects on match screen mount) → `BetOpportunityBanner`, `BetStatusDashboard`.

---

### `WS /replay/stream?from_chunk=&speed=`

**Purpose:** DVR scrub — replay positional frames from any historical point.

**How it works:** The `ReplayHandler` continuously writes live positional frames into a Redis Stream as fixed-size chunks (default 25 frames). The replay endpoint reads these chunks and emits them at `REPLAY_FRAME_INTERVAL / speed` seconds per frame, so the pitch stays in sync with the scrub bar.

**Client receives:** Same `positional` envelope as the live stream.

**Client sends:** `{ "type": "resume", "from_chunk": 42 }` to seek.

**Used by:** `useReplayStream` → `MatchTimeline` (DVR mode).

---

## Caching Strategy — Redis & In-Memory

### Why Redis for bets?

Bets are **live, ephemeral state** that must be accessible across multiple concurrent WebSocket connections without hitting the database on every message. Redis provides:

- **O(1) reads/writes** via `bet:{id}` string keys (serialised JSON).
- **Per-user index** as a Redis Set (`user_id:{uid}`) so `GET /bets?user_id=` is a single `SMEMBERS` + `MGET` — no table scan.
- **TTL semantics** available if bets should expire (not used today but trivially addable).
- **Atomic updates** via single `SET` calls, avoiding race conditions when multiple handlers settle the same bet.

SQLite is kept as the **source of truth for user balances** only, because balance changes must be durable and are infrequent (one write per settled bet).

### Why Redis for chat?

Chat rooms must survive server restarts and be readable by any connection. Redis gives us:

- **Message history** as a Redis List (`RPUSH` / `LRANGE`) — naturally ordered, bounded by `LLEN`.
- **Room metadata & join codes** as JSON strings with no schema migration overhead.
- **One-time WS tokens** with automatic 30-second `EX` expiry — no background cleanup job needed.
- **Member sets** for presence tracking.

### Why in-memory for `BetOpportunityStore`?

Bet opportunities are short-lived and can be regenerated. There is at most one active opportunity per bet type at a time. Storing them in-process avoids a Redis round-trip on every new connection and keeps the opportunity lifecycle co-located with the `BetNotifier`. If the server restarts, the chat-room `_ensure_match_result_opportunity()` guard re-seeds the store on the next connection.

### Why in-memory for `ConnectionManager` and `BetSettlementNotifier`?

WebSocket handles are OS file descriptors — they live in the process that accepted the connection. They cannot be serialised to Redis. Both managers use `asyncio.Lock`-protected dicts and are inherently single-process. If the app were scaled horizontally, a Redis Pub/Sub fan-out layer would replace these in-memory maps.

---

## REST API Reference

### Auth — `/auth`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | — | Register user, returns access + refresh JWT |
| POST | `/auth/login` | — | Validate credentials, returns tokens |
| POST | `/auth/refresh` | Refresh token | Issue new access token |
| POST | `/auth/logout` | Bearer | Revoke refresh token |
| GET | `/auth/me` | Bearer | Current user profile |

### Bets — `/bets`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/bets/create` | Optional Bearer | Place or update a bet; pushes snapshot to user WS |
| WS | `/bets/stream?user_id=` | — | Per-user settlement and opportunity stream |

### Chat — `/chat-room`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/chat-room/create` | — | Create a room, returns metadata + join code |
| POST | `/chat-room/join` | — | Join by code, returns `room_id` + `ws_token` |
| WS | `/chat-room/stream` | ws_token | Bi-directional chat + bet opportunity delivery |

### Replay — `/replay`

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/replay/status` | — | Chunk count, live edge seq, first frame number |
| WS | `/replay/stream?from_chunk=&speed=` | — | DVR positional stream from a given chunk |

### Debug — `/bets/debug` *(development only)*

| Method | Path | Description |
|--------|------|-------------|
| POST | `/bets/debug/trigger?window_seconds=` | Broadcast a fake substitution opportunity |
| POST | `/bets/debug/trigger/match_result?window_seconds=` | Broadcast a fake match-result opportunity |
| POST | `/bets/debug/loop/start?interval=` | Auto-fire substitution opportunities on a timer |
| POST | `/bets/debug/loop/stop` | Stop the loop |
| GET | `/bets/debug/loop/status` | Loop state |
| POST | `/bets/debug/bet/create` | Create a fake PENDING bet in Redis |
| POST | `/bets/debug/bet/activate` | Advance bet to ACTIVE |
| POST | `/bets/debug/bet/settle?result=` | Settle bet as SUCCESS or FAILED |
| POST | `/bets/debug/bet/settle_match_result?final_result=` | Simulate full-time whistle (e.g. `1:0`) |
| GET | `/bets/debug/bets?user_id=` | List all Redis bets for a user |

---

## Frontend Architecture

### Screen tree

```
app/
 ├─ _layout.tsx          AuthProvider + ApiProvider + auth redirect guard
 ├─ login.tsx            Credential form → POST /auth/login
 ├─ register.tsx         Registration form → POST /auth/register
 └─ (tabs)/
     ├─ _layout.tsx      Slim dark header; single-tab app (no bottom bar)
     └─ match.tsx        Main experience
         ├─ PitchCanvas          3D pitch (Expo GL + Three.js)
         ├─ MatchTimeline        Scrub bar + skip ± 10 s + Go Live
         ├─ ChatOverlay          Watch-party panel (left side)
         ├─ BetStatusDashboard   My bets panel (right side)
         └─ BetOpportunityBanner Pop-up banner on new opportunity
```

### Key hooks

| Hook | WebSocket | Surfaces |
|------|-----------|----------|
| `usePositionalStream` | `/positional/stream` | `lastMessage`, `matchId`, `status` |
| `useChatStream` | `/chat-room/stream` | `messages[]`, `latestBetOpportunity`, `sendMessage` |
| `useReplayStream` | `/replay/stream` + HTTP `/replay/status` | `lastMessage`, `replayStatus`, chunk helpers |
| `ApiContext` | `/bets/stream` | `myBets`, `latestBetOpportunity`, `createBet`, `settlementSocketStatus` |

### State flow for betting

```
BetSettlementSocket (/bets/stream)
      │  bet_opportunity message
      ▼
ApiContext.latestBetOpportunity
      │
      ▼
BetOpportunityBanner (slide-in from top)
      │  user taps team / YES / NO + enters amount
      ▼
ApiContext.createBet → POST /bets/create
      │
      ▼
BetSettlementSocket receives bet_snapshot
      │
      ▼
ApiContext.myBets → BetStatusDashboard (right panel)
```

---

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

Test files live under `backend/api/` and are discovered automatically via `pyproject.toml`.

---

## Debug & Testing Tools

The fastest way to exercise the betting flow without waiting for a live feed event:

```bash
# 1. Broadcast a match-result opportunity (90-minute window)
curl -X POST "http://localhost:8000/bets/debug/trigger/match_result?window_seconds=5400"

# 2. Broadcast a substitution opportunity (30-second window)
curl -X POST "http://localhost:8000/bets/debug/trigger?window_seconds=30"

# 3. Simulate half-time kick-off (activates pending bets)
#    Currently handled automatically by MatchResultBetHandler on second-half KickOff

# 4. Simulate full-time whistle — settle all match-result bets
curl -X POST "http://localhost:8000/bets/debug/bet/settle_match_result?final_result=1:0"

# 5. Inspect a user's bets in Redis
curl "http://localhost:8000/bets/debug/bets?user_id=1"
```
