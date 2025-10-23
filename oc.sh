#!/bin/bash
# Containerized OpenShift CLI wrapper
# Usage: ./oc.sh [oc commands and arguments]
# Example: ./oc.sh get pods

# Create .kube directory if it doesn't exist
mkdir -p ~/.kube

podman run --rm -it \
  -v ~/.kube:/root/.kube:Z \
  -v $(pwd):/workspace:Z \
  -w /workspace \
  quay.io/openshift/origin-cli:latest oc "$@"
