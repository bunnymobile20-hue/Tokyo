# TokyoOS ZimaOS App Model

## Overview

TokyoOS is prepared to run as a ZimaOS application (CasaOS App Store compatible).

## Docker Configuration

### Port: 8788
### Volume: /DATA/AppData/tokyoos:/data/tokyo

## ZimaOS Labels (docker-compose.yml)

```yaml
x-casaos:
  title: TokyoOS
  developer: GrupsBunny
  author: GrupsBunny
  category: Utilities
  port_map: "8788"
  scheme: http
  index: /ui
  store_app_id: tokyoos
```

## Healthcheck

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8788/tokyo/system/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Volume Structure

```
/DATA/AppData/tokyoos/
├── memory/
│   ├── local/
│   └── obsidian/
├── intelligence/
├── logs/
└── data/
```

## ZimaOS Requirements Met

- [x] Port mapping (8788)
- [x] Volume mounting (/DATA/AppData/tokyoos)
- [x] x-casaos labels in docker-compose
- [x] Healthcheck endpoint
- [x] HTTP scheme
- [x] Index page (/ui)
- [x] Store app ID (tokyoos)
- [x] Restart policy (unless-stopped)
- [x] No network_mode: host
- [x] App listens on 0.0.0.0

## Deployment

```bash
# Build
docker build -t tokyoos:latest .

# Run with docker-compose
docker-compose up -d

# Or via ZimaOS App Store
# Install "TokyoOS" from Utilities category
```
