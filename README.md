# OpenSERP + FastAPI

Self-hosted [OpenSERP](https://github.com/karust/openserp) (official Docker image) wrapped by a Python FastAPI app that uses the official [`openserp`](https://pypi.org/project/openserp/) SDK and serves a small search UI.

Netlify and Vercel cannot run OpenSERP: it is a long-lived Go process that launches Chromium. This project runs locally with Docker Compose and deploys to **Railway** as two services.

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

Railway does not run Compose as one unit. Create **one project** with **two services**.

### 1. `openserp` — Docker Image

1. New service → **Docker Image** → `karust/openserp:latest`
2. Name the service **`openserp`** (private DNS becomes `openserp.railway.internal`)
3. Custom start command: `serve -a 0.0.0.0 -p 7000`
4. Variables:

   ```
   OPENSERP_SERVER_HOST=0.0.0.0
   OPENSERP_SERVER_PORT=7000
   RAILWAY_SHM_SIZE_BYTES=2147483648
   ```

5. Resources: at least **2 GB RAM**
6. Do **not** generate a public domain. Keep this service private.

### 2. `api` — this GitHub repo

1. New service → **GitHub Repo** → this repository (root Dockerfile is auto-detected; do not set a custom start script)
2. Leave **Root Directory** empty (repo root). Railway uses `Dockerfile` + `railway.toml`.
3. Variables:

   ```
   OPENSERP_BASE_URL=http://openserp.railway.internal:7000
   OPENSERP_TIMEOUT=120
   API_KEY=<optional-secret>
   ```

   Railway also injects `PORT`. Uvicorn binds `0.0.0.0:$PORT`.
4. Generate a **public domain** for the UI.

If search returns 500/503, open `/health` on the public domain. `openserp_ready: false` means the API cannot see OpenSERP. Confirm the `openserp` image service exists, is named exactly `openserp`, is running (`serve -a 0.0.0.0 -p 7000`), and the API has `OPENSERP_BASE_URL=http://openserp.railway.internal:7000`.

Private networking uses `http://<service-name>.railway.internal:<port>` with no port mapping layer.

## Operational notes

- **CAPTCHAs:** Railway (and most cloud) IPs are datacenter ranges. Google/Bing may block them. Add proxy pools in `config.yaml` if you need those engines in production.
- **Chrome OOM:** `/dev/shm` must be enlarged. Locally that is `shm_size: 2gb`. On Railway set `RAILWAY_SHM_SIZE_BYTES=2147483648`.
- **Do not expose OpenSERP** on a public domain. Only the FastAPI service should be on the internet.
- First search after idle can be slow while Chromium starts (`idle_ttl` in `config.yaml` is 5 minutes).
