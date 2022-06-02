# PyChess

[![Tests](https://github.com/asimos-bot/pychess/workflows/Tests/badge.svg)](https://github.com/asimos-bot/pychess/actions/workflows/main.yml)

## How to Run

#### With Docker

```
docker build . -t pychess
docker run --privileged -e --user="$(id --user):$(id --group)" --rm \
-v /dev/snd:/dev/snd -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY pychess sh -c 'python3 pychess.py'
```

#### Host Machine

First install the needed python3 dependencies:

```
pip3 install -r requirements.txt
```

Then you just gotta run `pychess.py`:

```
python3 pychess.py
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
