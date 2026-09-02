# OpenSERP + FastAPI

Self-hosted [OpenSERP](https://github.com/karust/openserp) (official Docker image) wrapped by a Python FastAPI app that uses the official [`openserp`](https://pypi.org/project/openserp/) SDK and serves a small search UI.

Netlify and Vercel cannot run OpenSERP: it is a long-lived Go process that launches Chromium. This project runs locally with Docker Compose and deploys to **Railway as one service** (OpenSERP + API in the same container).

```
Browser  -->  FastAPI UI + /api/*  -->  OpenSERP (Chromium)  -->  search engines
```

## Local

Requirements: Docker Desktop with Compose v2.

```bash
docker compose up --build
```

- UI: http://localhost:8000
- FastAPI docs: http://localhost:8000/docs
- OpenSERP (direct, local only): http://localhost:7000/docs

```bash
curl "http://localhost:8000/health"
curl "http://localhost:8000/api/search?engine=duckduckgo&text=openserp&limit=5"
```

DuckDuckGo and Ecosia are the most reliable engines without residential proxies. Google and Bing often serve CAPTCHAs to datacenter IPs.

To require a bearer token on `/api/*`, copy `.env.example` to `.env` and set `API_KEY`, then pass it into Compose (`API_KEY` is already wired in `docker-compose.yml`).

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API + OpenSERP health |
| `GET` | `/api/engines` | Supported engines and mega modes |
| `GET` | `/api/search` | Single-engine search |
| `GET` | `/api/mega` | Multi-engine search (`mode=balanced\|fast\|any`) |
| `GET` | `/api/images` | Image search (single engine or mega) |
| `POST` | `/api/extract` | Extract one URL |
| `POST` | `/api/extract/batch` | Extract up to 20 URLs |

Search query params (common): `text`, `engine`, `limit`, `region`, `lang`, `site`, `date`, `file`, `start`, `extract` (0–5), `extract_mode` (`auto\|fast\|rendered`).

If `API_KEY` is set, send `Authorization: Bearer <key>` on `/api/*`.

## Railway

Use **one GitHub service**. Do not use `.railway.internal`: that DNS is IPv6-only, and OpenSERP listens on IPv4, so connections fail.

1. Keep a single service connected to this repository (root `Dockerfile`).
2. **Delete** any second `openserp` / Docker-image service.
3. **Clear the custom start command** so the image runs `start.sh` (OpenSERP on `127.0.0.1:7000`, then the API on `$PORT`).
4. Settings → Resources: at least **2 GB RAM**.
5. Variables:

   ```
   RAILWAY_SHM_SIZE_BYTES=2147483648
   OPENSERP_TIMEOUT=120
   API_KEY=<optional-secret>
   ```

   You can leave `OPENSERP_BASE_URL` unset. The combined image always uses `http://127.0.0.1:7000`.
6. Generate a **public domain** on this service.

`/health` should show `"openserp_ready": true` and `"openserp_base_url": "http://127.0.0.1:7000"`.

## Operational notes

- **CAPTCHAs:** Railway (and most cloud) IPs are datacenter ranges. Google/Bing may block them. Add proxy pools in `config.yaml` if you need those engines in production.
- **Chrome OOM:** `/dev/shm` must be enlarged. Locally that is `shm_size: 2gb`. On Railway set `RAILWAY_SHM_SIZE_BYTES=2147483648`.
- **Do not expose OpenSERP** on a public domain. Only the FastAPI service should be on the internet.
- First search after idle can be slow while Chromium starts (`idle_ttl` in `config.yaml` is 5 minutes).
