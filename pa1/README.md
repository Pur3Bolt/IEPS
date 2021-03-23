# IEPS 1. naloga

## Namestitev PostgreSQL

Podatkovno bazo PostgreSQL namestimo lokalno z uporabo Dockerja. V repozitoriju se v mapi `docker/init-scripts` nahaja SQL skripta, ki ustvari podatkovno bazo ter vnese začetne URL povezave (tj. semena), na računalniku pa je potrebno ustvariti še mapo `docker/pgdata` v kateri se bodo hranili podatki iz baze. Docker instanco ustvarimo z naslednjim ukazom v terminalu:
```sh
docker run --name postgresql-wier \
    -e POSTGRES_PASSWORD=SecretPassword \
    -e POSTGRES_USER=user \
    -v $PWD/pgdata:/var/lib/postgresql/data \
    -v $PWD/init-scripts:/docker-entrypoint-initdb.d \
    -p 5432:5432 \
    -d postgres:12.2
```

V primeru, da izberemo druge prijavne podatke, moramo le-te vnesti v datoteko `database/connector.py`.

## Poganjanje skripte

Skripto poženemo z ukazom `python process.py --threads n`, kjer si parameter `n` poljubno izberemo. Skripa bo, glede na zmogljivosti računalnika, ustvarila do `n` niti pajkov.
