all: setup run

build: build-nginx

build-nginx:
	docker build -t proxy_bench/nginx ./images/nginx

setup: build
	pipenv install

run:
	pipenv run python -m proxy_bench

ping:
	docker network create ping --subnet 172.23.0.0/24 --gateway 172.23.0.1
	docker run --rm -dt --name nginx --net ping nginx:1.19	
	docker run --rm -t --net ping busybox ping -c 60 172.23.0.2
	docker kill nginx
	docker network remove ping