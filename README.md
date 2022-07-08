# PyChess

[![Tests](https://github.com/asimos-bot/pychess/workflows/Tests/badge.svg)](https://github.com/asimos-bot/pychess/actions/workflows/main.yml)

## How to Run

The most easy way to run is to download and run a binary for your operating system from the [release page](https://github.com/asimos-bot/pychess/releases/tag/v1.0.0)

#### With Docker

```
docker build . -t pychess
docker run --privileged -e --user="$(id --user):$(id --group)" --rm \
-v /dev/snd:/dev/snd -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY pychess sh -c 'python3 pychess.py'
```

#### With python3

First install the needed python3 dependencies:

```
pip3 install -r requirements.txt
```

Then you just gotta run `pychess.py`:

```
python3 pychess.py
```

#### Build executable (with pyinstaller)

```
python3 -m pyinstaller pychess.spec
```

## Run Tests

#### Host Machine

inside `src/`:

```
python3 -m unittest
```

#### With Docker

```
docker build . -t pychess && docker run pychess sh -c 'python3 -m unittest'
```
