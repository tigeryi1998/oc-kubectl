# ETL App Deployment on OpenShift

This guide documents how the **ETL job and Postgres database** were deployed to **Red Hat OpenShift**, using the **OpenShift Web Console (UI)** — not the CLI.  
The goal is to show how to build container images, create supporting services, and run a one-time ETL job in a cloud environment.

---

## 🧱 Repository Contents

| File | Description |
|------|--------------|
| `Containerfile` | Dockerfile defining the ETL container image |
| `docker-compose.yml` | Local test setup (Postgres + ETL job) using Podman or Docker |
| `buildconfig.yaml` | OpenShift BuildConfig + ImageStream for building and storing the image |
| `postgres-deployment.yaml` | Deployment for running the Postgres database |
| `postgres-service.yaml` | Service for connecting to Postgres within the project |
| `postgres-persistent-volume.yaml` | PVC for persistent database storage |
| `etl-job.yaml` | Kubernetes Job for running the ETL task once |
| `screenshot/` | Folder of UI screenshots showing setup and build process |

---

## 🚀 Deployment Steps (via OpenShift Web Console)

### 1. Log in to OpenShift
Go to the **Developer View** of your assigned project (namespace).  
Verify that your project quota allows for at least:
- 1 CPU
- 8 GiB memory
- 2 persistent volume

---

### 2. Create the Build and Image
**Goal:** Build the container image from GitHub inside OpenShift.

1. In the **Add** menu → choose **“Import YAML”**.  
2. Copy the content of [`buildconfig.yaml`](./buildconfig.yaml) and paste it.  
3. Apply it — this creates both:
   - a **BuildConfig** (for automated builds), and  
   - an **ImageStream** (to store your resulting image).  
4. Once created, go to **Builds → Builds → etl-app → Start build**.  
5. Wait until the build finishes successfully (status: *Complete*).  

📸 See [`log-build.png`](./screenshot/log-build.png) for reference.

---

### 3. Deploy Postgres
1. Again go to **Add → Import YAML**.  
2. Apply the following, in order:
   - [`postgres-persistent-volume.yaml`](./postgres-persistent-volume.yaml)
   - [`postgres-deployment.yaml`](./postgres-deployment.yaml)
   - [`postgres-service.yaml`](./postgres-service.yaml)
   - [`etl-persistent-volume.yaml`](./etl-persistent-volume.yaml)
3. Wait until the Postgres pod is running and the service shows a valid cluster IP.

📸 See [`log-postgres.png`](./screenshot/log-postgres.png) for reference.

📸 Also see [`resource-creation.png`](./screenshot/resource-creation.png) for reference.

---

### 4. Run the ETL Job
1. In **Add → Import YAML**, paste the contents of [`etl-job.yaml`](./etl-job.yaml).  
2. This job uses the image built from step 2 (`etl-app:latest` ImageStreamTag).  
3. Once created, check **Jobs → etl-job → Pods → Logs** to verify it completed successfully.  

📸 See [`log-job.png`](./screenshot/log-job.png) for reference.

📸 Also see [`resource-creation.png`](./screenshot/resource-creation.png) for reference.

---

### 5. (Optional) Verify Data
If your ETL job writes results into Postgres:
1. Open the **Pod Terminal** for the Postgres pod.  
2. Run:
   ```bash 
   psql -U user -d mydb
   ```

   ```sql
   postgres=#  -- PostgreSQL prompt
   \dt   -- list tables
   SELECT * FROM titanic LIMIT 5;
   \q    -- exit view
   \q    -- exit psql
   ```
3. Confirm that data loaded as expected.

---

## 🧩 Local Testing (Optional)

You can also test everything locally before uploading to OpenShift using **Podman Desktop** or Docker:

```bash
podman compose build
podman compose up
```

This runs the same ETL + Postgres setup locally for quick debugging.

---

## 📝 Notes
- Always **apply BuildConfig + ImageStream first**, otherwise your ETL job won’t find its image tag.
- If you hit a *resource quota exceeded* error, scale down or delete old Deployments.
- For reproducibility, all YAML files are included in this repo.
