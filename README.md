# PiClock
[![Hadolint](https://github.com/Mephphisto/PiClock/actions/workflows/hadolint.yml/badge.svg)](https://github.com/Mephphisto/PiClock/actions/workflows/hadolint.yml)
[![Pylint](https://github.com/Mephphisto/PiClock/actions/workflows/pylint.yml/badge.svg)](https://github.com/Mephphisto/PiClock/actions/workflows/pylint.yml)
[![Docker Image CI](https://github.com/Mephphisto/PiClock/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Mephphisto/PiClock/actions/workflows/docker-image.yml)

An e-ink clock for the Raspberry Pi that displays animated clock faces and album art from a WiiM streamer, with live weather data from Home Assistant.

## Hardware

| Component | Details |
|---|---|
| Display | Pimoroni Inky e-ink 7.3" (inky_e673) |
| SOC | Raspberry Pi Zero W |
| Streamer | WiiM device (HTTP API over LAN) |
| Smart home | Home Assistant (REST API) |

## Features

- **6 animated clock faces** — randomly rotated each hour (or fixed with `-c <index>`)
- **Album art mode** — switches to cover art + track/artist/album when the WiiM is playing
- **Weather overlay** — temperature, humidity, barometric pressure, and pressure trend in the corners of every clock face
- **Docker-first** — runs entirely in a container; no host Python environment needed

## Clock faces

| Index | Name |
|---|---|
| 0 | Drop shadow |
| 1 | Rotating triangles |
| 2 | Dark CMY blobs |
| 3 | Colourful blobs |
| 4 | Stripy black |
| 5 | Stripy white |

## Setup

### 1. Configuration

Copy the default config and fill in your values:

```bash
cp config.json.default config.json
```

```json
{
  "WiM_IP": "192.168.1.x",
  "HA_Addr": "http://192.168.1.x:8123",
  "HA_API_Key": "your_long_lived_access_token",
  "HA_entities": {
    "baro":       "sensor.your_baro_sensor",
    "temp":       "sensor.your_temperature_sensor",
    "humid":      "sensor.your_humidity_sensor",
    "baro_change":"sensor.your_baro_change_sensor"
  }
}
```

### 2. Font

Place `Futura.ttc` in the project root. It is git-ignored and must be supplied separately. Or replace with a differtent Font of your choice.

### 3. Build and run

```bash
docker compose up -d
```

The container mounts all required SPI, GPIO, I2C, and `/sys` devices automatically. It restarts unless stopped.

### 4. Pin a clock face (optional)

To lock a specific clock face instead of randomising:

```bash
# edit CMD in Dockerfile
CMD ["python", "src/main.py", "-c", "1"]
```

or pass it via `docker compose run`:

```bash
docker compose run piclock python src/main.py -c 1
```

## Running without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install spidev
git clone https://github.com/pimoroni/inky inky && pip install -r inky/requirements.txt && pip install --upgrade inky
pip install -r requirements.txt
cd src
python main.py
```

The working directory must be `src/` so that `Futura.ttc` and `config.json` resolve correctly (both are expected one level up at the project root — adjust `FUTURA_DICT` in `MusicCover.py` if needed).

## Project structure

```
PiClock/
├── src/
│   ├── main.py           # Entry point, main loop, state machine
│   ├── Clock.py          # Clock face renderers + HA weather overlay
│   ├── Display.py        # E-ink output (gamma, saturation, contrast)
│   ├── Home_Assistant.py # HA REST client wrapper
│   ├── MusicCover.py     # Album art renderer + font layout helpers
│   └── WiiM.py           # WiiM HTTP API client
├── config.json.default   # Config template (no secrets)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Docker compose devices

The compose file passes through:

| Device | Purpose |
|---|---|
| `/dev/spidev0.0` | SPI bus for the display |
| `/dev/gpiochip0`, `/dev/gpiochip4` | GPIO (display control lines) |
| `/dev/gpiomem` | Direct GPIO memory access |
| `/dev/i2c-1`, `/dev/i2c-2` | I2C (display initialisation) |

`/sys` and `/proc/device-tree` are bind-mounted for hardware detection. `SYS_RAWIO` and `SYS_ADMIN` capabilities are required for low-level peripheral access.

## Notes

- WiiM devices use a self-signed TLS certificate; SSL verification is intentionally disabled in `WiiM.py`.
- The canvas is drawn in landscape and rotated 90° on output to match the display orientation.
- The clock face index randomises on every new hour; `-c` overrides this for the session.
