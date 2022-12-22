.DEFAULT_GOAL := help
.PHONY: docs
SRC_DIRS = ./lekt ./tests ./bin ./docs
BLACK_OPTS = --exclude templates ${SRC_DIRS}


build-pythonpackage: build-pythonpackage-lekt ## Build Python packages ready to upload to pypi

build-pythonpackage-lekt: ## Build the "lekt" python package for upload to pypi
	python setup.py sdist

push-pythonpackage: ## Push python package to pypi
	twine upload --skip-existing dist/lekt-mfe-$(shell make version).tar.gz
 ## Run all tests by decreasing order of priority

test-static: test-lint test-types test-format  ## Run only static tests

test-format: ## Run code formatting tests
	black --check --diff $(BLACK_OPTS)

test-lint: ## Run code linting tests
	pylint --errors-only --enable=unused-import,unused-argument --ignore=templates --ignore=docs/_ext ${SRC_DIRS}

test-types: ## Check type definitions
	mypy --exclude=templates --ignore-missing-imports --strict ${SRC_DIRS}

format: ## Format code automatically
	black $(BLACK_OPTS)

###### Deployment

bundle: ## Bundle the lekt package in a single "dist/lekt" executable
	pyinstaller lekt.spec

release: release-unsafe ## Create a release tag and push it to origin
release-unsafe:
	$(MAKE) release-tag release-push release-publish TAG=v$(shell make version)
release-tag:
	@echo "=== Creating tag $(TAG)"
	git tag -d $(TAG) || true
	git tag $(TAG)
release-push:
	@echo "=== Pushing tag $(TAG) to origin"
	git push origin
	git push origin :$(TAG) || true
	git push origin $(TAG)

release-publish:
	@echo "=== Publishing release $(TAG)"
	twine upload --skip-existing dist/*.tar.gz

version: ## Print the current lekt version
	@python -c 'import io, os; about = {}; exec(io.open(os.path.join("lektmfe", "__about__.py"), "rt", encoding="utf-8").read(), about); print(about["__version__"])'
