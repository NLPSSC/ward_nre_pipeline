the-auditor-build:
	THE_AUDITOR_PROJECT_PATH=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
	docker build -t the_auditor:latest -f "$${THE_AUDITOR_PROJECT_PATH}auditor_api/Dockerfile" "$${THE_AUDITOR_PROJECT_PATH}auditor_api"
