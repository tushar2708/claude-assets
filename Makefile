.DEFAULT_GOAL := help

.PHONY: help test test-flow test-myhooks

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2}'

test: test-flow test-myhooks  ## Run every plugin test suite

test-flow:  ## Run the docsmith pytest suite (flow plugin)
	@bash plugins/flow/skills/docs/scripts/run_tests.sh

test-myhooks:  ## Run the myhooks rule tests (pytest)
	@cd plugins/myhooks/hooks && uv run --with pytest --with ruff python -m pytest tests/
