# =============================================================================
# Sangho SDK Python — Makefile
# =============================================================================
# Usage : make <target>
# Prérequis : python3.13+, pip, git
# =============================================================================

.DEFAULT_GOAL := help
.PHONY: help install test test-file test-coverage test-integration test-ci \
        lint lint-fix format typecheck check build clean \
        version-patch version-minor version-major changelog \
        publish-test publish release-patch release-minor release-major \
        _bump _git-tag-and-push info

# Détection automatique Windows vs Unix
ifeq ($(OS),Windows_NT)
    PYTHON   := python
    PIP      := pip
    RM       := rmdir /s /q
    RMFILE   := del /f /q
else
    PYTHON   := python3
    PIP      := pip3
    RM       := rm -rf
    RMFILE   := rm -f
endif

# -----------------------------------------------------------------------------
# Couleurs terminal
# -----------------------------------------------------------------------------
RESET  := \033[0m
BOLD   := \033[1m
GREEN  := \033[32m
YELLOW := \033[33m
CYAN   := \033[36m
RED    := \033[31m

VERSION  := $(shell $(PYTHON) -c "import sangho; print(sangho.__version__)" 2>/dev/null || echo "0.0.0")
PKG_NAME := sangho

# -----------------------------------------------------------------------------
# AIDE
# -----------------------------------------------------------------------------
help: ## Affiche cette aide
	@echo ""
	@echo "$(BOLD)$(CYAN)Sangho SDK Python v$(VERSION)$(RESET)"
	@echo "$(CYAN)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# -----------------------------------------------------------------------------
# INSTALLATION
# -----------------------------------------------------------------------------
install: ## Installe les dépendances (dev)
	@echo "$(CYAN)→ Installation des dépendances...$(RESET)"
	$(PIP) install -e ".[dev]"

# -----------------------------------------------------------------------------
# TESTS
# -----------------------------------------------------------------------------
test: ## Lance les tests (une fois)
	@echo "$(CYAN)→ Tests...$(RESET)"
	pytest tests/ -v --tb=short

test-file: ## Lance un fichier de test précis (make test-file FILE=tests/test_x.py)
	pytest $(FILE) -v --tb=short

test-coverage: ## Lance les tests avec rapport de couverture
	@echo "$(CYAN)→ Tests + couverture...$(RESET)"
	pytest tests/ --cov=sangho --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Rapport généré dans ./htmlcov$(RESET)"

test-ci: ## Tests + couverture pour CI (exit code si seuil non atteint)
	@echo "$(CYAN)→ Tests CI...$(RESET)"
	pytest tests/ --cov=sangho --cov-report=xml --cov-fail-under=80
	@echo "$(GREEN)✓ Tests CI OK$(RESET)"

test-integration: ## Tests intégration sandbox (nécessite SANGHO_API_KEY)
	@echo "$(CYAN)→ Tests intégration sandbox...$(RESET)"
	pytest tests/integration/ -v --tb=short
	@echo "$(GREEN)✓ Tests intégration OK$(RESET)"

# -----------------------------------------------------------------------------
# QUALITÉ DU CODE
# -----------------------------------------------------------------------------
lint: ## Lint du code source
	@echo "$(CYAN)→ Lint...$(RESET)"
	ruff check sangho/ tests/
	ruff format --check sangho/ tests/

lint-fix: ## Lint + correction automatique
	@echo "$(CYAN)→ Lint + fix...$(RESET)"
	ruff format sangho/ tests/
	ruff check --fix sangho/ tests/
	@echo "$(GREEN)✓ Lint corrigé$(RESET)"

format: lint-fix ## Alias de lint-fix

typecheck: ## Vérifie les types avec mypy
	@echo "$(CYAN)→ Vérification des types...$(RESET)"
	mypy sangho/
	@echo "$(GREEN)✓ Types OK$(RESET)"

check: lint typecheck ## Lint + typecheck (pipeline qualité)
	@echo "$(GREEN)✓ Qualité OK$(RESET)"

# -----------------------------------------------------------------------------
# BUILD
# -----------------------------------------------------------------------------
build: clean ## Build de production (sdist + wheel)
	@echo "$(CYAN)→ Build en cours...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Build terminé$(RESET)"
	@ls -lh dist/ 2>/dev/null || true

# -----------------------------------------------------------------------------
# NETTOYAGE
# -----------------------------------------------------------------------------
clean: ## Supprime les artefacts de build/test
ifeq ($(OS),Windows_NT)
	if exist dist      rmdir /s /q dist
	if exist build     rmdir /s /q build
	if exist htmlcov   rmdir /s /q htmlcov
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache   rmdir /s /q .mypy_cache
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
else
	rm -rf dist/ build/ *.egg-info htmlcov .coverage .pytest_cache .mypy_cache __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
endif

# -----------------------------------------------------------------------------
# VERSIONING (Semantic Versioning)
# -----------------------------------------------------------------------------
version-patch: check test ## Bump patch version (1.1.0 → 1.1.1)
	@$(MAKE) _bump PART=patch

version-minor: check test ## Bump minor version (1.1.0 → 1.2.0)
	@$(MAKE) _bump PART=minor

version-major: check test ## Bump major version (1.1.0 → 2.0.0)
	@$(MAKE) _bump PART=major

_bump: ## (Interne) Bump __version__ dans sangho/__init__.py
	@echo "$(CYAN)→ Bump $(PART)...$(RESET)"
	@$(PYTHON) -c "\
import re; \
path = 'sangho/__init__.py'; \
content = open(path).read(); \
current = re.search(r'__version__ = \"(\d+)\.(\d+)\.(\d+)\"', content).groups(); \
major, minor, patch = map(int, current); \
new = {'major': (major+1,0,0), 'minor': (major,minor+1,0), 'patch': (major,minor,patch+1)}['$(PART)']; \
new_version = '.'.join(map(str, new)); \
open(path, 'w').write(re.sub(r'__version__ = \"[^\"]+\"', f'__version__ = \"{new_version}\"', content)); \
print(new_version)"
	@echo "$(GREEN)✓ Nouvelle version : $(shell $(PYTHON) -c "import sangho; print(sangho.__version__)")$(RESET)"

changelog: ## Rappelle de documenter la release dans CHANGELOG.md
	@echo "$(YELLOW)⚠ Ajoutez une entrée dans CHANGELOG.md avant de release.$(RESET)"

# -----------------------------------------------------------------------------
# PUBLICATION PyPI
# -----------------------------------------------------------------------------
publish-test: build ## Publie sur TestPyPI
	@echo "$(CYAN)→ Publication sur TestPyPI...$(RESET)"
	twine upload --repository testpypi dist/*

publish: build test ## Publie sur PyPI (nécessite les identifiants twine)
	@echo "$(CYAN)→ Publication v$(VERSION) sur PyPI...$(RESET)"
	twine upload dist/*
	@echo "$(GREEN)✓ $(PKG_NAME)@$(VERSION) publié sur PyPI$(RESET)"

# -----------------------------------------------------------------------------
# RELEASE COMPLÈTE (versioning + git tag + publish)
# -----------------------------------------------------------------------------
release-patch: ## Release patch complète (bump + tag + publish)
	$(MAKE) version-patch
	$(MAKE) _git-tag-and-push
	$(MAKE) publish

release-minor: ## Release minor complète (bump + tag + publish)
	$(MAKE) version-minor
	$(MAKE) _git-tag-and-push
	$(MAKE) publish

release-major: ## Release major complète (bump + tag + publish)
	$(MAKE) version-major
	$(MAKE) _git-tag-and-push
	$(MAKE) publish

_git-tag-and-push: ## (Interne) Commit, tag et push git
	$(eval NEW_VERSION := $(shell $(PYTHON) -c "import sangho; print(sangho.__version__)"))
	@echo "$(CYAN)→ Git commit + tag v$(NEW_VERSION)...$(RESET)"
	git add sangho/__init__.py CHANGELOG.md
	git commit -m "chore: release v$(NEW_VERSION)"
	git tag -a "v$(NEW_VERSION)" -m "Release v$(NEW_VERSION)"
	git push origin main --tags
	@echo "$(GREEN)✓ Tag v$(NEW_VERSION) poussé$(RESET)"

# -----------------------------------------------------------------------------
# INFOS
# -----------------------------------------------------------------------------
info: ## Affiche les infos du SDK
	@echo "$(BOLD)Package :$(RESET) $(PKG_NAME)"
	@echo "$(BOLD)Version :$(RESET) $(VERSION)"
	@echo "$(BOLD)Python  :$(RESET) $(shell $(PYTHON) --version)"
	@echo "$(BOLD)Pip     :$(RESET) $(shell $(PIP) --version)"
