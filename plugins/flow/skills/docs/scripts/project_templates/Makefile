# Managed by docsmith scaffold. Convenience targets for documentation
# governance and the doc site. Safe to edit; re-scaffolding will not clobber
# a Makefile that already contains the docsmith targets.
.DEFAULT_GOAL := help
DOCSMITH := uv run .docsmith/engine/docsmith.py

.PHONY: help setup validate score docs-render docs-build docs-serve precommit clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2}'

setup:  ## Idempotent full bootstrap (uv, docs venv + deps, pre-commit hooks)
	@bash .docsmith/setup.sh

validate:  ## Validate documentation (fails on errors)
	@$(DOCSMITH) validate

score:  ## Score documentation freshness and update state
	@$(DOCSMITH) score --all --update-state

docs-render:  ## Regenerate the mkdocs config + nav from the docs tree
	@$(DOCSMITH) collect render

docs-build:  ## Build the static doc site (run 'make setup' first)
	@$(DOCSMITH) collect build

docs-serve:  ## Serve the doc site with live reload (run 'make setup' first)
	@$(DOCSMITH) collect serve

precommit:  ## Run all pre-commit hooks across the repo
	@pre-commit run --all-files

clean:  ## Remove the built site output
	@rm -rf .docsmith/site/site
