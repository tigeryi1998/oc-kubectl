#!/bin/bash
# delete.sh - clean up ETL app resources in OpenShift

echo "🧹 Cleaning up ETL-related OpenShift resources..."

# Delete build configs, builds, and imagestreams
oc delete buildconfig,build,imagestream -l app=etl-app --ignore-not-found

# Delete job and its pods
oc delete job,pod -l job-name=etl-job --ignore-not-found
oc delete job etl-job --ignore-not-found

# Delete Postgres deployment and pods
oc delete deploy postgres --ignore-not-found
oc delete pod -l app=postgres --ignore-not-found

# Delete services
oc delete svc postgres --ignore-not-found
oc delete svc etl-app --ignore-not-found

# Delete PVCs (volumes)
oc delete pvc etl-pvc --ignore-not-found
oc delete pvc postgres-pvc --ignore-not-found

# Delete any leftover configmaps
oc delete configmap -l app=etl-app --ignore-not-found
oc delete configmap etl-app-1-ca etl-app-1-global-ca etl-app-1-sys-config --ignore-not-found

echo "✅ Cleanup complete."
