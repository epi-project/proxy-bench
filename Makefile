all: setup run

build: build-nginx build-ping

build-nginx:
	docker build -t proxy_bench/nginx ./images/nginx

build-ping:
	docker build -t proxy_bench/ping ./images/ping
	
setup: build
	pipenv install

run:
	pipenv run python -m proxy_bench