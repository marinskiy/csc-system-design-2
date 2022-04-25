.DEFAULT_GOAL     := help # when you run make, it defaults to printing available commands

CONDA_ENV_SPEC = ${PWD}/environment.yml

VENV=${PWD}/venv
VENV_PIP=${VENV}/bin/pip
VENV_PYTHON=${VENV}/bin/python

TEST_VENV_NAME=${PWD}/testing_venv
TEST_PIP=${TEST_VENV_NAME}/bin/pip
TEST_PYTHON=${TEST_VENV_NAME}/bin/python

TEST_PYTEST=${TEST_VENV_NAME}/bin/pytest
TEST_FLAKE=${TEST_VENV_NAME}/bin/flake8
TEST_MYPY=${TEST_VENV_NAME}/bin/mypy
TEST_PYLINT=${TEST_VENV_NAME}/bin/pylint

SOURCES := src/roguelike
TESTS := src/tests


# discover the absolute path to the project repo on the host machine
ifeq ($(OS),Windows_NT)
	# * docker driver does not support path-based volume mounts with special characters in the source or target mount path
	# * 'space' character is considered a special character and is quite common as a user name on firm laptops
	#   for example: C:\Users\Tom Smith\Documents\optimus
	# * here we are using powershell to discover the MS DOS 'short-path'
	#   which is an equivalant path expression but without any spaces.
	#   for example, the user path above would look something like this: C:\Users\TOM~1\DOCUME~1\optimus
	OPTIMUS_DIR := $(shell powershell "(New-Object -ComObject Scripting.FileSystemObject).GetFolder('.').ShortPath")
else
	OPTIMUS_DIR := "$$(pwd)"
endif

.PHONY: help
help:  ## Show all make commands
ifeq ($(OS),Windows_NT)
	powershell "((type Makefile) -match '##') -notmatch 'grep'"
else
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@test -f ./utilities/Makefile && grep -E '^[a-zA-Z_-]+:.*?## .*$$' ./utilities/Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' || true
endif

.PHONY: .testing-venv
.testing-venv:
ifneq '$(wildcard $(TEST_VENV_NAME))' '' # check if testing directory with env exists
	@echo ">>> Found $(TEST_VENV_NAME) environment. Skipping installation..."
	conda env update --prefix $(TEST_VENV_NAME) -f ${CONDA_ENV_SPEC} --prune -q
else
ifneq '$(GITHUB_ENV)' ''
		@echo ">>> Detected CI/CD environment. Cloning preinstalled env to working directory..."
		# conda create --prefix $(TEST_VENV_NAME) --clone testing_venv -q
		conda env update --prefix $(TEST_VENV_NAME) -f ${CONDA_ENV_SPEC} --prune -q
else
		@echo ">>> Detected conda, but $(TEST_VENV_NAME) is missing in working directory. Installing ..."
		conda env create --prefix $(TEST_VENV_NAME) -f ${CONDA_ENV_SPEC} -q
endif
endif
	$(TEST_PIP) install --no-deps types-requests -q
	$(TEST_PIP) install --no-deps types-pytz -q
	$(TEST_PIP) install --no-deps types-setuptools -q
	$(MAKE) PIP=$(TEST_PIP) .install
	@echo "\033[92m [testing-venv OK] \033[0m"


.PHONY: .pylint
.pylint:
	@echo "Running pylint checks..."
	@${TEST_PYLINT} ${SOURCES} ${TESTS}
	@echo "\033[92m [pylint OK] \033[0m"

.PHONY: .mypy
.mypy:
	@echo "Running mypy checks..."
	@${TEST_MYPY} ${SOURCES} ${TESTS}
	@echo "\033[92m [mypy OK] \033[0m"

.PHONY: .flake8
.flake8:
	@printf "Running flake8 checks...\t"
	@${TEST_FLAKE} ${SOURCES} ${TESTS}
	@echo "\033[92m [flake8 OK] \033[0m"

.PHONY: .pytest
.pytest:
	@echo "Running pytest checks...\t"
	@${TEST_PYTEST} ${TESTS}

.PHONY: lint
lint: .pylint .flake8 .mypy  ## Create testing env from env file and run linters
	@echo "\033[92m [lint OK] \033[0m"

.PHONY: pytest
pytest: .testing-venv .pytest
	@echo "\033[92m [pytest OK] \033[0m"

.PHONY: test
test: pytest  ## Create testing env from env file and run tests
	@echo "\033[92m [test OK] \033[0m"

.PHONY: clean  ## Clean working directory
clean:
	conda env remove --prefix $(TEST_VENV_NAME)
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type d -name '*egg-info*' -exec rm -rf {} +
	@rm -rf build

.PHONY: .install
.install:
	$(PIP) install -q --no-deps -e ./

.PHONY: install
install: PIP=${VENV_PIP}
install: .install  ## Installs lib from sources to pip

.PHONY: .uninstall
.uninstall:
	$(PIP) uninstall roguelike

.PHONY: uninstall
uninstall: PIP=${VENV_PIP}
uninstall: .uninstall  ## Uninstalls lib from sources from pip

.PHONY: .local-conda-env-create
.local-conda-env-create:
	conda env create --prefix ${VENV} -f ${CONDA_ENV_SPEC}

.PHONY: local-env-create
local-env-create: PIP=${VENV_PIP}
local-env-create: .local-conda-env-create .install  ## Create local conda env with proper dependencies

.PHONY: .local-conda-env-update
.local-conda-env-update:
	conda env update --prefix ${VENV} -f ${CONDA_ENV_SPEC} --prune


.PHONY: local-env-update
local-env-update: PIP=${VENV_PIP}
local-env-update: .local-conda-env-update .install  ## Update local conda env


.PHONY: launch
launch: ## Launch roguelike
	sudo ${VENV_PYTHON} -m roguelike
