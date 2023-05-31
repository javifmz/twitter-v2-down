# SocialDown

A tool to download tweets using the Twitter API V2.

## Configuration

All the configuration goes into the `config.yml` file.

## Normal execution

### Search

```bash
python -m search # config.yml and output in the execution path
python -m search --config /path/to/config.yml --output /path/to/output # Different path
```

### Check search status

```bash
python -m status # File config.yml in the execution path
python -m status --config /path/to/config.yml --output /path/to/output # Different path
```

## Docker execution

### Build (mandatory step)

```bash
docker build . -t socialdown
```

### Search

```bash
docker run --rm -it -v "$PWD:/app" socialdown python -m search # config.yml and output in the execution path
```

### Status

```bash
docker run --rm -it -v "$PWD:/app" socialdown python -m status # config.yml and output in the execution path
```