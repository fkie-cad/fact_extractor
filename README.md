# FACT extractor

Utilizes FACT unpack plugins into standalone utility.
Should be able to extract most of the common container formats.

Build with

```sh
docker build --build-arg USER=root -t fact_extractor .
```

Run with

```sh
docker run -v <path_to_shared_folder>:/tmp/extractor --rm fact_extractor
```

### Copyright Fraunhofer FKIE 2019
