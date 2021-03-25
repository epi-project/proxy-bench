all: setup run

setup: pull build
	mkdir /tmp/docker-tc
	pipenv install

build: build-nginx-proxy build-socks-proxy build-httping-client

build-nginx-proxy:
	docker build -t proxy_bench/nginx-proxy ./images/nginx

build-socks-proxy:
	docker build -t proxy_bench/socks-proxy ./images/socks -f ./images/socks/Dockerfile.proxy

build-httping-client:
	docker build -t proxy_bench/httping-client ./images/socks -f ./images/socks/Dockerfile.httping

build-wrk-client:
	docker build -t proxy_bench/wrk-client ./images/socks -f ./images/socks/Dockerfile.wrk

pull:
	git submodule update --init 
	docker pull nginx:1.19

run:
	pipenv run python -m proxy_bench

ping:
	docker network create ping --subnet 172.23.0.0/24 --gateway 172.23.0.1
	docker run --rm -dt --name nginx --net ping nginx:1.19	
	docker run --rm -t --net ping busybox ping -c 60 172.23.0.2
	docker kill nginx
	docker network remove ping

ping-delayed:
	docker network create ping --subnet 172.23.0.0/24 --gateway 172.23.0.1
	
	docker run --rm -dt --name ping-tc \
		--network host \
		--cap-add NET_ADMIN	\
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v /tmp/docker-tc:/var/docker-tc \
		lukaszlach/docker-tc
	
	docker run --rm -dt --name nginx \
		--net ping \
		--label "com.docker-tc.enabled=1" \
		--label "com.docker-tc.delay=0.4ms" \
		nginx:1.19	
	
	docker run --rm -it --name ping \
		--net ping \
		--label "com.docker-tc.enabled=1" \
		--label "com.docker-tc.delay=0.4ms" \
		busybox \
		ping -c 60 172.23.0.2
	
	docker kill nginx
	docker kill ping-tc

	docker network remove ping
