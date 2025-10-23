# OpenShift Deployment Guide

Complete guide for deploying the TikTok ETL pipeline on OpenShift (Red Hat Developer Sandbox).

---

## Prerequisites

1. **OpenShift Account**
   - Sign up at: https://developers.redhat.com/developer-sandbox
   - Free tier provides 30-day access

2. **CLI Tools**

   **Option A: Containerized `oc` (Recommended - No Installation)**
   ```bash
   # Create .kube directory (needed for credentials)
   mkdir -p ~/.kube

   # Create an alias for containerized oc
   alias oc='podman run --rm -it \
     -v ~/.kube:/root/.kube:Z \
     -v $(pwd):/workspace:Z \
     -w /workspace \
     quay.io/openshift/origin-cli:latest oc'

   # Verify it works
   oc version
   ```

   To make permanent, add to `~/.bashrc` or `~/.zshrc`:
   ```bash
   mkdir -p ~/.kube
   echo "alias oc='podman run --rm -it -v ~/.kube:/root/.kube:Z -v \$(pwd):/workspace:Z -w /workspace quay.io/openshift/origin-cli:latest oc'" >> ~/.bashrc
   source ~/.bashrc
   ```

   **Option B: Install `oc` Locally**
   ```bash
   # macOS
   brew install openshift-cli

   # Linux
   wget https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
   tar -xvf openshift-client-linux.tar.gz
   sudo mv oc /usr/local/bin/

   # Verify installation
   oc version
   ```

3. **Git Repository**
   - Repository: https://github.com/langd0n-classes/data-eng-at-scale.git
   - Branch: 202504-fa25
   - Path: assignments/openshift-etl-solution

---

## Deployment Steps

### Step 1: Login to OpenShift

```bash
# Copy login command from OpenShift web console
# (Top-right menu → Copy Login Command)
oc login --token=YOUR_TOKEN --server=https://api.sandbox.x8i5.p1.openshiftapps.com:6443
```

### Step 2: Verify Your Project

**Note**: Developer Sandbox provides a single pre-created project (namespace) for you. You cannot create additional projects.

```bash
# Check your assigned project name
oc project

# Output will look like: "USERNAME-dev" or similar
# Example: lwhite-dev
```

Your project name will be used automatically in subsequent commands.

### Step 3: Deploy Secrets

```bash
# Apply database credentials
oc apply -f openshift/secrets.yaml

# Verify secrets created
oc get secrets database-secrets
```

### Step 4: Deploy PostgreSQL

```bash
# Deploy PostgreSQL database
oc apply -f openshift/postgresql-deployment.yaml

# Wait for pod to be ready
oc get pods -l app=postgres -w

# Verify database is accessible
oc exec -it deployment/postgres -- psql -U postgres -d tiktok -c "\dt"
```

### Step 5: Deploy MySQL

```bash
# Deploy MySQL database
oc apply -f openshift/mysql-deployment.yaml

# Wait for pod to be ready
oc get pods -l app=mysql -w

# Verify database is accessible
oc exec -it deployment/mysql -- mysql -u root -pmysql123 -D tiktok -e "SHOW TABLES;"
```

### Step 6: Build ETL Container Image

**Option A: Using OpenShift BuildConfig (Recommended)**

```bash
# 1. Create GitHub credentials secret (repo is private)
#    First, create a GitHub Personal Access Token:
#    GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
#    Required scope: repo (full control)
oc create secret generic github-credentials \
  --from-literal=username=YOUR_GITHUB_USERNAME \
  --from-literal=password=YOUR_GITHUB_PAT \
  --type=kubernetes.io/basic-auth

# 2. Apply BuildConfig (already configured for this repo)
oc apply -f openshift/etl-buildconfig.yaml

# 3. Trigger build
oc start-build tiktok-etl

# Monitor build logs
oc logs -f buildconfig/tiktok-etl

# Verify image created
oc get imagestream tiktok-etl
```

**Option B: Using Local Build + Push**

```bash
# Build locally
podman build -t tiktok-etl:latest -f Containerfile .

# Tag for OpenShift registry
podman tag tiktok-etl:latest \
  image-registry.openshift-image-registry.svc:5000/tiktok-etl/tiktok-etl:latest

# Login to OpenShift registry
podman login -u $(oc whoami) -p $(oc whoami -t) \
  default-route-openshift-image-registry.apps.sandbox.x8i5.p1.openshiftapps.com

# Push image
podman push tiktok-etl:latest \
  default-route-openshift-image-registry.apps.sandbox.x8i5.p1.openshiftapps.com/tiktok-etl/tiktok-etl:latest
```

### Step 7: Update Job Manifests

Replace `YOUR_NAMESPACE` placeholders with your actual project name:

```bash
# Capture project name and strip carriage returns/newlines
# Note: containerized oc outputs \r\n which breaks sed
OC_PROJECT=$(oc project -q | tr -d '\r\n')

# Automatically update both manifests with your project name
sed -i "s/YOUR_NAMESPACE/${OC_PROJECT}/g" openshift/etl-job.yaml
sed -i "s/YOUR_NAMESPACE/${OC_PROJECT}/g" openshift/query-deployment.yaml

# Verify the changes
grep "image-registry" openshift/etl-job.yaml
# Should show: image-registry.openshift-image-registry.svc:5000/YOUR_ACTUAL_PROJECT/tiktok-etl:latest
```

### Step 8: Run ETL Job

```bash
# Deploy one-time job
oc apply -f openshift/etl-job.yaml

# Monitor job execution
oc get jobs -w

# View job logs
oc logs -f job/tiktok-etl-job

# Check completion
oc get job tiktok-etl-job
```

Expected output in logs:
```
{"timestamp": "...", "level": "INFO", "message": "Starting full ETL pipeline"}
{"timestamp": "...", "level": "INFO", "message": "PART 1: Data Ingestion"}
{"timestamp": "...", "level": "INFO", "message": "PostgreSQL load complete: 19382 rows processed"}
{"timestamp": "...", "level": "INFO", "message": "PART 4: Data Transformation"}
{"timestamp": "...", "level": "INFO", "message": "95th percentile engagement rate: 0.123456"}
{"timestamp": "...", "level": "INFO", "message": "Viral feature calculation complete: 969/19382 videos marked as viral (5.00%)"}
{"timestamp": "...", "level": "INFO", "message": "PART 3: Data Migration"}
{"timestamp": "...", "level": "INFO", "message": "Migration complete: 19382 rows migrated"}
{"timestamp": "...", "level": "INFO", "message": "✓ Row counts match"}
{"timestamp": "...", "level": "INFO", "message": "ETL pipeline completed successfully"}
```

### Step 9: Deploy Query Service (Optional)

```bash
# Deploy persistent query pod
oc apply -f openshift/query-deployment.yaml

# Wait for pod to be ready
oc get pods -l app=tiktok-query -w

# Run top viral videos query
oc exec -it deployment/tiktok-query -- python top_viral_videos.py
```

### Step 10: Enable Scheduled Runs (Optional)

```bash
# CronJob is already included in etl-job.yaml
# It will run daily at 2 AM UTC

# Verify CronJob created
oc get cronjob

# Manually trigger a run
oc create job --from=cronjob/tiktok-etl-cronjob manual-run-1

# Suspend scheduled runs
oc patch cronjob/tiktok-etl-cronjob -p '{"spec": {"suspend": true}}'
```

---

## Verification & Testing

### Check Data in PostgreSQL

```bash
# Connect to PostgreSQL
oc exec -it deployment/postgres -- psql -U postgres -d tiktok

# Run queries
SELECT COUNT(*) FROM tiktok_videos;
SELECT COUNT(*) FROM tiktok_videos WHERE going_viral = TRUE;
SELECT video_id, engagement_rate FROM tiktok_videos ORDER BY engagement_rate DESC LIMIT 10;
\q
```

### Check Data in MySQL

```bash
# Connect to MySQL
oc exec -it deployment/mysql -- mysql -u root -pmysql123 -D tiktok

# Run queries
SELECT COUNT(*) FROM tiktok_videos;
SELECT COUNT(*) FROM tiktok_videos WHERE going_viral = TRUE;
SELECT video_id, engagement_rate FROM tiktok_videos ORDER BY engagement_rate DESC LIMIT 10;
exit
```

### Run Viral Videos Report

```bash
# From query pod
oc exec -it deployment/tiktok-query -- python top_viral_videos.py

# Or create a temporary pod
oc run temp-query --rm -it --image=image-registry.openshift-image-registry.svc:5000/$(oc project -q)/tiktok-etl:latest \
  --env="DB_URI=$(oc get secret database-secrets -o jsonpath='{.data.postgres-uri}' | base64 -d)" \
  --command -- python top_viral_videos.py
```

---

## Troubleshooting

### Pod Won't Start

```bash
# Check pod status
oc get pods

# Describe pod for events
oc describe pod POD_NAME

# Check logs
oc logs POD_NAME

# Common issues:
# - Image pull errors: verify BuildConfig succeeded
# - CrashLoopBackOff: check database connectivity
# - Pending: resource quota exceeded (sandbox limits)
```

### Database Connection Errors

```bash
# Verify secrets are correct
oc get secret database-secrets -o yaml

# Decode secret values
oc get secret database-secrets -o jsonpath='{.data.postgres-uri}' | base64 -d

# Test connectivity from ETL pod
oc run test-db --rm -it --image=postgres:15-alpine -- \
  psql "$(oc get secret database-secrets -o jsonpath='{.data.postgres-uri}' | base64 -d)"

# Check if services exist
oc get svc postgres mysql
```

### Job Failures

```bash
# Check job status
oc describe job tiktok-etl-job

# View failed pod logs
oc logs job/tiktok-etl-job

# Delete and recreate job
oc delete job tiktok-etl-job
oc apply -f openshift/etl-job.yaml
```

### Build Failures

```bash
# Check BuildConfig
oc get buildconfig

# View build logs
oc logs -f buildconfig/tiktok-etl

# Common issues:
# - Git authentication: ensure repo is public
# - Containerfile syntax: test locally with podman build
# - Resource limits: wait and retry
```

---

## Local Development & Testing

### Run Pipeline Locally

```bash
# Start local databases with Docker/Podman
podman run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=tiktok \
  -p 5432:5432 \
  postgres:15-alpine

podman run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=mysql \
  -e MYSQL_DATABASE=tiktok \
  -p 3306:3306 \
  mysql:8.0

# Install dependencies
pip install -r requirements.txt

# Run ETL pipeline
python etl_elt.py --mode=full

# Query results
python top_viral_videos.py
```

### Test Container Locally

```bash
# Build image
podman build -t tiktok-etl:test -f Containerfile .

# Run container with local databases
podman run --rm \
  --network host \
  -e POSTGRES_URI="postgresql://postgres:postgres@localhost:5432/tiktok" \
  -e MYSQL_URI="mysql+pymysql://root:mysql@localhost:3306/tiktok" \
  tiktok-etl:test
```

---

## Resource Limits (Developer Sandbox)

Red Hat Developer Sandbox has quotas:

- **CPU**: 7000m (7 cores total)
- **Memory**: 15 Gi
- **Storage**: Limited to emptyDir (ephemeral)
- **Duration**: 30 days

Our deployment uses:
- PostgreSQL: 512Mi RAM, 500m CPU
- MySQL: 512Mi RAM, 500m CPU
- ETL Job: 1Gi RAM, 1000m CPU
- Query Pod: 512Mi RAM, 500m CPU
- **Total**: ~2.5Gi RAM, ~2 CPU (within limits ✓)

**Note**: Using `emptyDir` for databases means data is **ephemeral**. For persistent storage, upgrade to a paid OpenShift plan and use PersistentVolumeClaims.

---

## Cleanup

```bash
# Delete all resources (keeps your project)
oc delete -f openshift/

# Note: You cannot delete your project in Developer Sandbox
# It's your only project and is managed by the platform
```

---

## Next Steps

1. **Monitor Production Runs**
   - Set up logging aggregation (OpenShift Console → Logs)
   - Configure alerts for job failures

2. **Optimize Performance**
   - Add database indices for query performance
   - Increase batch commit sizes for large datasets

3. **Enhance Security**
   - Rotate database passwords (update secrets)
   - Use SealedSecrets for GitOps workflows
   - Enable network policies to restrict pod communication

4. **Add Observability**
   - Export metrics to Prometheus
   - Create Grafana dashboards for viral trends
   - Set up alerting for data quality issues

5. **Scale Up**
   - Switch to PersistentVolumes for database storage
   - Use StatefulSets for database high availability
   - Implement CDC for real-time viral detection
