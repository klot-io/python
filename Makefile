ACCOUNT=klotio
IMAGE=python
INSTALL=arm32v7/python:3.8.5-alpine3.12
VERSION?=0.2
DEBUG_PORT=5678
TTY=$(shell if tty -s; then echo "-it"; fi)
VOLUMES=-v ${PWD}/lib:/opt/service/lib \
		-v ${PWD}/test:/opt/service/test \
		-v ${PWD}/setup.py:/opt/service/setup.py
ENVIRONMENT=-e PYTHONDONTWRITEBYTECODE=1 \
			-e PYTHONUNBUFFERED=1
.PHONY: cross build shell debug test push setup tag untag

cross:
	docker run --rm --privileged multiarch/qemu-user-static:register --reset

build:
	docker build . -t $(ACCOUNT)/$(IMAGE):$(VERSION)

shell:
	docker run $(TTY) $(VOLUMES) $(ENVIRONMENT) $(ACCOUNT)/$(IMAGE):$(VERSION) sh

debug:
	docker run $(TTY) $(VOLUMES) $(ENVIRONMENT) -p 127.0.0.1:$(DEBUG_PORT):5678 $(ACCOUNT)/$(IMAGE):$(VERSION) sh -c "python -m ptvsd --host 0.0.0.0 --port 5678 --wait -m unittest discover -v test"

test:
	docker run $(TTY) $(VOLUMES) $(ENVIRONMENT) $(ACCOUNT)/$(IMAGE):$(VERSION) sh -c "coverage run -m unittest discover -v test && coverage report -m --include 'lib/*.py'"

push:
	docker push $(ACCOUNT)/$(IMAGE):$(VERSION)

setup:
	docker run $(TTY) $(VOLUMES) $(INSTALL) sh -c "cp -r /opt/service /opt/install && cd /opt/install/ && python setup.py install && python -m klotio && python -m klotio_unittest"

tag:
	-git tag -a "v$(VERSION)" -m "Version $(VERSION)"
	git push origin --tags

untag:
	-git tag -d "v$(VERSION)"
	git push origin ":refs/tags/v$(VERSION)"
