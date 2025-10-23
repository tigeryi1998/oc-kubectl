# Quick Start Guide

This is a simplified deployment guide. For complete documentation, see `docs/deployment-guide.md`.

---

## Local Testing (5 minutes)

```bash
# 1. Start databases
podman run -d --name postgres \
  -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=tiktok \
  -p 5432:5432 postgres:15-alpine

podman run -d --name mysql \
  -e MYSQL_ROOT_PASSWORD=mysql -e MYSQL_DATABASE=tiktok \
  -p 3306:3306 mysql:8.0

# Wait for databases to be ready (5-10 seconds)
sleep 10

# 2. Build the container image (same as OpenShift will use)
podman build -t tiktok-etl:latest -f Containerfile .

# 3. Run ETL pipeline in container
podman run --rm --network host \
  -e POSTGRES_URI="postgresql://postgres:postgres@localhost:5432/tiktok" \
  -e MYSQL_URI="mysql+pymysql://root:mysql@localhost:3306/tiktok" \
  tiktok-etl:latest

# 4. View results from MySQL (also in container)
podman run --rm --network host \
  -e MYSQL_URI="mysql+pymysql://root:mysql@localhost:3306/tiktok" \
  --entrypoint python \
  tiktok-etl:latest top_viral_videos.py

# Cleanup
podman stop postgres mysql
podman rm postgres mysql
```

**Alternative: Direct Python (for development only)**
```bash
pip install -r requirements.txt
# Start databases as above, then:
python etl_elt.py --mode=full
python top_viral_videos.py
```

---

## OpenShift Deployment (15 minutes)

### Setup: Choose Your `oc` Method

**Recommended: Containerized `oc` (No Installation)**

```bash
# One-time setup: create .kube directory and alias
mkdir -p ~/.kube
alias oc='podman run --rm -it \
  -v ~/.kube:/root/.kube:Z \
  -v $(pwd):/workspace:Z \
  -w /workspace \
  quay.io/openshift/origin-cli:latest oc'

# Test it works
oc version
```

**To make permanent** (optional), add to `~/.bashrc`:
```bash
echo "alias oc='podman run --rm -it -v ~/.kube:/root/.kube:Z -v \$(pwd):/workspace:Z -w /workspace quay.io/openshift/origin-cli:latest oc'" >> ~/.bashrc
source ~/.bashrc
```

**Alternative: Install `oc` Locally**
```bash
# macOS
brew install openshift-cli

# Linux
curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
tar -xzf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/
```

---

### Deployment Steps (Copy/Paste Ready)

**Note**: The commands below work with either method (alias or native `oc`).

```bash
# 1. Login to OpenShift (get token from web console: top-right → Copy Login Command)
oc login --token=YOUR_TOKEN --server=YOUR_SERVER

# 2. Verify your project (Developer Sandbox provides one pre-created project)
oc project

# 3. Deploy infrastructure
oc apply -f openshift/secrets.yaml
oc apply -f openshift/postgresql-deployment.yaml
oc apply -f openshift/mysql-deployment.yaml

# Wait for databases to be ready (watch until both show "Running", then Ctrl+C)
oc get pods -w

# 4. Create GitHub credentials (repo is private)
# Create a GitHub PAT: Settings → Developer settings → Personal access tokens → Tokens (classic)
# Required scope: repo (full control)
oc create secret generic github-credentials \
  --from-literal=username=YOUR_GITHUB_USERNAME \
  --from-literal=password=YOUR_GITHUB_PAT \
  --type=kubernetes.io/basic-auth

# 5. Build ETL image
oc apply -f openshift/etl-buildconfig.yaml
oc start-build tiktok-etl
oc logs -f bc/tiktok-etl

# 6. Update namespace in job manifests (replaces YOUR_NAMESPACE with your actual project)
# Note: tr -d '\r\n' strips carriage returns from containerized oc output
OC_PROJECT=$(oc project -q | tr -d '\r\n')
sed -i "s/YOUR_NAMESPACE/${OC_PROJECT}/g" openshift/etl-job.yaml
sed -i "s/YOUR_NAMESPACE/${OC_PROJECT}/g" openshift/query-deployment.yaml

# 7. Run ETL job
oc apply -f openshift/etl-job.yaml
oc logs -f job/tiktok-etl-job

# 8. Deploy query service and get results
oc apply -f openshift/query-deployment.yaml
oc get pods -l app=tiktok-query -w
# (Press Ctrl+C once Running)

oc exec -it deployment/tiktok-query -- python top_viral_videos.py
```

---

## File Structure

```
.
├── etl_elt.py              # Main ETL pipeline (Parts 1-4)
├── top_viral_videos.py     # Reporting script (Part 6)
├── Containerfile           # Container definition (Part 2)
├── requirements.txt        # Python dependencies
├── tiktok_dataset.csv      # Dataset backup
├── openshift/              # Kubernetes manifests
│   ├── secrets.yaml
│   ├── postgresql-deployment.yaml
│   ├── mysql-deployment.yaml
│   ├── etl-buildconfig.yaml
│   ├── etl-job.yaml
│   └── query-deployment.yaml
└── docs/                   # Documentation (Parts 5, 7, 8)
    ├── deployment-guide.md
    ├── etl-vs-elt.md
    └── viral-algorithm.md
```

---

## Architecture

```
┌─────────────┐
│  TikTok CSV │
└──────┬──────┘
       │ Extract
       ▼
┌─────────────┐
│ PostgreSQL  │ ← Load (raw data)
│   (Source)  │
└──────┬──────┘
       │ Transform (in-database)
       │ - Calculate engagement_rate
       │ - Mark going_viral
       ▼
┌─────────────┐
│   MySQL     │ ← Migrate (transformed data)
│  (Target)   │
└─────────────┘
```

---

## Key Features

✅ **Idempotent**: Safe to rerun without duplicating data
✅ **ELT Pattern**: Raw data loaded first, transformed in-database
✅ **Viral Algorithm**: 95th percentile engagement + 100K views
✅ **Containerized**: Runs anywhere (local, OpenShift, K8s)
✅ **Production-Ready**: Error handling, logging, validation

---

## Sample Output

```
====================================================================================================
TOP 10 VIRAL TIKTOK VIDEOS
====================================================================================================

+--------+------------+----------+----------+----------+------------+--------------+---------------------------+
|   Rank | Video ID   | Views    | Likes    | Shares   | Comments   | Engagement   | Transcription Snippet     |
+========+============+==========+==========+==========+============+==============+===========================+
|      1 | 4014381136 | 140,877  | 77,355   | 19,034   | 684        | 0.688234     | someone shared with me... |
|      2 | 5842397981 | 236,771  | 92,153   | 41,928   | 1,832      | 0.573412     | someone shared with me... |
|      3 | 3609761483 | 700,081  | 434,565  | 97,995   | 1,411      | 0.762891     | someone shared with me... |
+--------+------------+----------+----------+----------+------------+--------------+---------------------------+

====================================================================================================
SUMMARY STATISTICS
====================================================================================================

Total Views (Top 10):          4,823,901
Total Engagement Actions:      2,104,672
Average Engagement Rate:       0.623456

Engagement Rate = (Likes + Shares + Comments) / Views
Viral Threshold = 95th percentile engagement + 100K+ views
```

---

## Troubleshooting

**Issue**: `ImportError: No module named 'sqlalchemy'`
**Fix**: `pip install -r requirements.txt`

**Issue**: Database connection refused
**Fix**: Check databases are running: `podman ps`

**Issue**: OpenShift build fails
**Fix**: Verify GitHub repo is public and Containerfile path is correct

**Issue**: Job shows `ImagePullBackOff`
**Fix**: Update namespace in `etl-job.yaml`: `sed -i "s/YOUR_NAMESPACE/$(oc project -q)/g" openshift/etl-job.yaml`

---

For detailed explanations, see:
- **ETL vs ELT Discussion**: `docs/etl-vs-elt.md`
- **Viral Algorithm Details**: `docs/viral-algorithm.md`
- **Full Deployment Guide**: `docs/deployment-guide.md`
