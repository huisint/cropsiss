NAME := $(or $(NAME), huisint)
APPNAME := $(or $(APPNAME), $(shell python setup.py --name))
BUILD_DATE := $(shell date "+%Y%m%d")
VERSION := $(or $(VERSION), $(shell python setup.py --version))
TAG_VERSION := $(VERSION)-$(BUILD_DATE)
PLATFORMS := $(or $(PLATFORMS), $(shell echo "linux/amd64,linux/arm64"))
BUILD_ARGS := $(or $(BUILD_ARGS),)
MAJOR := $(word 1,$(subst ., ,$(TAG_VERSION)))
MINOR := $(word 2,$(subst ., ,$(TAG_VERSION)))


buildx:
	docker login
	docker buildx build $(BUILD_ARGS) \
	--platform $(PLATFORMS) \
	--build-arg VERSION=v$(VERSION) \
	--push  \
	-t $(NAME)/$(APPNAME):${TAG_VERSION} \
	-t $(NAME)/$(APPNAME):${VERSION} \
	-t $(NAME)/$(APPNAME):$(MAJOR) \
	-t $(NAME)/$(APPNAME):$(MAJOR).$(MINOR) \
	docker

buildx-preview:
	docker login
	docker buildx build $(BUILD_ARGS) \
	--platform $(PLATFORMS) \
	--build-arg VERSION=v$(VERSION)-preview \
	--push \
	-t $(NAME)/$(APPNAME):v$(VERSION)-preview \
	docker
	

test: flake8 mypy unittest

flake8:
	flake8 .

mypy:
	mypy .

unittest:
	coverage run -m unittest
	coverage html
	coverage report