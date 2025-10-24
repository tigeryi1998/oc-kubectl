## Local Minikube + Podman / OpenShift Instruction



---

# Minikube Commands (Local Kubenetes K8S Cluster)

1. Start Minikube cluster:

| OS / Architecture               | Recommended Driver(s)                    | Notes                                                                                                         |
| ------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **macOS (Apple Silicon M1/M2)** | `vfkit` (best), `docker`                 | `vfkit` uses Apple’s native virtualization; faster and more reliable. Docker works too. Podman less reliable. |
| **macOS (Intel / x86_64)**      | `docker` (best), `qemu2`                 | Docker is easy; QEMU works but slightly slower. vfkit not available on Intel Macs.                            |
| **Windows (x86_64)**            | `hyperv` (native), `docker`              | Hyper-V recommended if available; Docker Desktop is also common.                                              |
| **Linux (x86_64 / ARM64)**      | `kvm2` (Linux native), `docker`, `qemu2` | KVM2 is fastest if the kernel supports it; Docker is easiest for lightweight testing. QEMU works anywhere.    |



0. Install

- macOS Intel / x86_64
```bash
brew install minikube
# Recommended drivers:
minikube start --driver=docker   # easiest
minikube start --driver=qemu2    # slower but works without Docker
```

- Apple Silicon (M1/M2)
```bash
brew install vfkit
brew install minikube
minikube start --driver=vfkit    # fastest, native VM
minikube start --driver=docker   # works too
```
Experimental / less reliable: podman driver, krunkit, parallels (if you have Parallels Desktop)


- Windows 
Download MSI from: https://minikube.sigs.k8s.io/docs/start/
Recommended drivers:
hyperv (native)
docker (if Docker Desktop installed)
Other: virtualbox (older setups)


- Linux
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```
Recommended drivers:
kvm2 (if KVM available, fastest)
docker (works everywhere)
qemu2 (fallback)
Experimental: podman



1. Drivers 

1.1. vfkit

```bash
# Virtual machine 
minikube start --driver=vfkit
```

1.2 qemu2

```bash
# Virtual machine (via QEMU)
minikube start --driver=qemu2
```

1.3 docker

```bash
# Container runtime: Docker 
minikube start --driver=docker
```

1.4 podman

```bash
# Container runtime: Podman (NOT reliable)
minikube start --driver=podman
```




2. Check status

once start, verify minikube status
```bash
minikube status
```


3. Stop Minikube cluster:
```bash
minikube stop
```


4. Delete Minikube cluster: (Do NOT run this)
```bash
minikube delete
```




---

# Kubernetes / OpenShift Commands

You can use either `kubectl` or `oc`  
both work the same for most cases.
but on minikube, let's use `kubectl` for now


## 1. View Resources

```
Namespaces (default or custom project) # Logical separation of resources
 └─ Nodes                            # Physical or virtual machines running the cluster
      ├─ Deployments / Jobs           # Controllers that manage Pods
      │    └─ Pods                    # Running instances of your app or job
      │         ├─ Containers         # Actual processes running in the Pod
      │         └─ PVCs               # Claims to persistent storage
      │              └─ PVs           # Actual persistent volumes on the cluster
      │                   └─ SC      # StorageClass defines how PVs are provisioned
      └─ Services                     # Abstract way to expose Pods (internal or external)
```


- Namespaces
```bash
kubectl get namespaces
oc get namespaces
# NAME              STATUS   AGE
# default           Active   16h
# kube-node-lease   Active   16h
# kube-public       Active   16h
# kube-system       Active   16h
```

- Nodes:
```bash
kubectl get nodes
oc get nodes
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   16h   v1.34.0
```

- Pods:
```bash
kubectl get pods
oc get pods
# No resources found in default namespace.
```

- Jobs
```bash
kubectl get jobs  
oc get jobs
# No resources found in default namespace.
```

- Deployments
```bash
kubectl get deployments  
oc get deployments
# No resources found in default namespace.
```

- Persistent Volume Claims (PVCs):
```bash
kubectl get pvc
oc get pvc
# No resources found in default namespace.
```

- Persistent Volumes (PVs):
```bash
kubectl get pv
oc get pv
# No resources found
```

- Storage Classes (SCs):
```bash
kubectl get sc
oc get sc
# NAME                 PROVISIONER                RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
# standard (default)   k8s.io/minikube-hostpath   Delete          Immediate           false                  16h
```

- Services 
```bash
kubectl get services
oc get services
# NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
# kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   16h
```

- ConfigMap & secrets
```bash
kubectl get secrets
kubectl get configmaps

oc get secrets
oc get configmaps

# NAME               DATA   AGE
# kube-root-ca.crt   1      16h
```




## 2. Apply Kubernetes Configurations (Wait, do not run yet)

Let's skip and come back later. Build and push container image first. 


```bash
# kubectl
kubectl apply -f postgres-persistent-volume.yaml  # Postgres PV + PVC
kubectl apply -f postgres-deployment.yaml         # Postgres Deployment
kubectl apply -f postgres-service.yaml            # Postgres Service
kubectl apply -f persistent-volume.yaml           # ETL PV + PVC
kubectl apply -f etl-job.yaml                     # ETL Job
```

```bash
# openshift oc
oc apply -f postgres-persistent-volume.yaml       # Postgres PV + PVC
oc apply -f postgres-deployment.yaml              # Postgres Deployment
oc apply -f postgres-service.yaml                 # Postgres Service
oc apply -f persistent-volume.yaml                # ETL PV + PVC
oc apply -f etl-job.yaml                          # ETL Job
```

Tip: After each step, you can optionally check the resources:

```bash
kubectl get pv,pvc,pods,services,jobs
kubectl describe pvc <name>
```



For example, more detailed steps below:

```bash
## 1. Apply Postgres Persistent Volume
# Creates PV + PVC for Postgres
kubectl apply -f postgres-persistent-volume.yaml  
# Check PV and PVC
kubectl get pv,pvc
# Optional: inspect PVC details
kubectl describe pvc postgres-pvc


## 2. Deploy Postgres
# Creates Postgres Deployment (Pod)
kubectl apply -f postgres-deployment.yaml   
# Check deployment status
kubectl get deployments      
# Check Pod status
kubectl get pods
kubectl get pods -l app=postgres
# Optional: inspect Pod details
kubectl describe pod <postgres-pod-name>
kubectl describe pod -l app=postgres


## 3. Create Postgres Service
# Creates Service to expose Postgres internally
kubectl apply -f postgres-service.yaml           
# Check Service
kubectl get services


## 4. Apply ETL Persistent Volume
# Creates PV + PVC for ETL Job
kubectl apply -f persistent-volume.yaml           
# Check PV and PVC
kubectl get pv,pvc
# Optional: inspect PVC details
kubectl describe pvc etl-pvc


## 5. Deploy ETL Job (Do not run this step yet, wait!)
# Creates a one-time ETL Job Pod 
kubectl apply -f etl-job.yaml

# Check Job Pod
kubectl get pods

# check jobs
kubectl get jobs

# delte jobs (Do NOT delete, until finish job)
kubectl delete job etl-job

# Optional: inspect Pod logs
kubectl logs <etl-job-pod-name>
kubectl logs job/etl-job


## 6. Full Snapshot
### After all resources are applied, check everything together
kubectl get pv,pvc,pods,services,jobs

```



## 3. Execute a Shell in a Pod (jump down, same name)

```bash
kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -- sh

oc exec -it <pod-name> -- bash
oc exec -it <pod-name> -- sh

# oc short cut
oc rsh <pod-name>
```


## 4. Scale a Deployment

```bash
kubectl scale deployment <deployment-name> --replicas=<number>
oc scale deployment <deployment-name> --replicas=<number>
```







---


# Building and Managing Container Images

## Local Build with Minikube (Do NOT try this)
```bash
minikube podman-env  # or minikube docker-env if using Docker driver
eval $(minikube podman-env)

# Now, you’re “inside” Minikube’s Podman environment — if you build here:
podman build -f Containerfile -t etl_app:latest .

# the image goes directly into Minikube’s Podman, and you can immediately run:
# minikube image load etl_app:latest
kubectl apply -f etl-job.yaml

# 💡 Tip: when done, exit back to your normal environment with:
eval $(minikube podman-env -u)
```



## Docker

0. Register account on Docker Hub docker.io

https://hub.docker.com/repositories/

image-name = [registry/]username/image-name:tag

```bash
docker login docker.io
```

1. Build:
```bash
docker build -f Containerfile -t etl_app:latest .
podman run --rm -it -d etl_app:latest
```

2. Tag (explicit Docker Hub):
```bash
docker tag etl_app:latest docker.io/<username>/etl_app:latest
```

3. Push:
```bash
docker login docker.io
docker push docker.io/<username>/etl_app:latest
```

4. Run ETL Job: 
```bash
# simple create job (do not run)
# kubectl create job etl-job --image=quay.io/tigeryi/etl_app:latest

# run the etl job yaml manifest instead
kubectl apply -f etl-job.yaml              

kubectl get jobs
kubectl get pods

kubectl logs -l job-name=etl-job
kubectl logs <etl-job-pod-name>

# delte jobs (Do NOT delete, until finish job)
kubectl delete job etl-job
```


## Podman 

0. Register account on quay.io
https://quay.io/repository/

Create New Repository 
Repository Name: etl_app
Public view, Empty 

```bash
podman login quay.io
```

1. Build:
```bash
podman build -f Containerfile -t etl_app:latest .
```

2. Tag (quay.io example):
```bash
podman tag etl_app:latest quay.io/<username>/etl_app:latest
# podman tag etl_app:latest quay.io/tigeryi/etl_app:latest

podman image prune
```

3. Push:
```bash
podman login quay.io

podman push quay.io/<username>/etl_app:latest
# podman push quay.io/tigeryi/etl_app:latest

podman pull quay.io/<username>/etl_app:latest
# podman pull quay.io/tigeryi/etl_app:latest
```

4. Run ETL Job: 
```bash
# simple create job (do not run)
# kubectl create job etl-job --image=quay.io/tigeryi/etl_app:latest

# run the etl job yaml manifest instead
kubectl apply -f etl-job.yaml                   

kubectl get jobs
kubectl get pods

kubectl logs -l job-name=etl-job
kubectl logs <etl-job-pod-name>

# delte jobs (Do NOT delete, until finish job)
kubectl delete job etl-job
```



## OpenShift Internal Registry (Homework try this one)

```bash
podman build -f Containerfile -t etl_app:latest .
podman login --username=$(oc whoami) --password=$(oc whoami -t) \
  image-registry.openshift-image-registry.svc:5000
podman tag etl_app:latest \
  image-registry.openshift-image-registry.svc:5000/<project>/etl_app:latest
podman push etl_app:latest \
  image-registry.openshift-image-registry.svc:5000/<project>/etl_app:latest
```






---

## Execute a Shell in a Pod (jump to here)

Now, go inside of the postgres pod. 
Grab the name of the postgres pod. 

```bash
# check the name of the pods
kubectl get pods

kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -- sh

oc exec -it <pod-name> -- bash
oc exec -it <pod-name> -- sh

# oc short cut
oc rsh <pod-name>
```

## 🐘 PostgreSQL Commands Inside the Pod

1. Connect to PostgreSQL:

```bash 
psql -U user -d mydb
```

Opens a PostgreSQL prompt.
```sql
postgres=#  -- PostgreSQL prompt:
```

2. Inside of the psql:

```sql
\dt          -- list tables

SELECT * FROM <table_name> LIMIT 5;
-- SELECT * FROM titanic LIMIT 5;

\q           -- exit view
\q           -- exit psql
```

3. Exit PostgreSQL:

```bash
exit
```

You can do everything in 1 go

kubectl exec -it <pod-name> -- psql -U user -d mydb -c "\dt; SELECT * FROM titanic LIMIT 5;"


---

# Clean up 

## Delete individual resources

You can remove the YAML you applied:
This keeps Minikube running but clears all your deployed apps and PV/PVC.

```bash
# Delete Jobs
kubectl delete -f etl-job.yaml

# Delete Deployments
kubectl delete -f postgres-deployment.yaml

# Delete Services
kubectl delete -f postgres-service.yaml

# Delete Persistent Volumes / Claims
kubectl delete -f persistent-volume.yaml
kubectl delete -f postgres-persistent-volume.yaml

# check what is left
kubectl get pods,pv,pvc,services,jobs
```


## Delete all resources in default namespace

This will remove all pods, deployments, services, jobs, PVCs, PVs in the cluster.

```bash
kubectl delete all --all
kubectl delete pvc --all
kubectl delete pv --all

# check what is left
kubectl get all,pv,pvc,jobs,pods,configmaps,secrets
```


## Full Minikube reset at the cluster level (Do NOT do this)

```bash
minikube stop

# ok Do NOT delete
# minikube delete --all

minikube start --driver=vfkit
```




---

## 🗂 Quick Reference: Local vs OpenShift Sandbox

| Task                          | Local (Minikube + Podman)                             | OpenShift Sandbox / edu console                   |
| ----------------------------- | ----------------------------------------------------- | ------------------------------------------------ |
| Start local cluster            | `minikube start --driver=podman`                     | N/A (use sandbox cluster, already running)      |
| Stop cluster                   | `minikube stop`                                      | N/A                                              |
| Delete cluster                 | `minikube delete`                                    | N/A                                              |
| Get pods                       | `kubectl get pods`                                   | `oc get pods`                                    |
| Exec / shell into pod          | `kubectl exec -it <pod> -- bash` <br> `kubectl exec -it <pod> -- sh` | `oc rsh <pod>` <br> `oc exec -it <pod> -- bash` <br> `oc exec -it <pod> -- sh` |
| Apply configs                  | `kubectl apply -f *.yaml`                            | `oc apply -f *.yaml`                             |
| Scale deployment               | `kubectl scale deployment <name> --replicas=N`       | `oc scale deployment <name> --replicas=N`        |
| Build container image          | `podman build -t <image>:latest -f Containerfile`   | Optional local build, usually `oc start-build`  |
| Tag for registry               | `podman tag <image>:latest quay.io/<user>/<image>:latest` | `podman tag <image>:latest image-registry.openshift-image-registry.svc:5000/<project>/<image>:latest` |
| Push to registry               | `podman push quay.io/<user>/<image>:latest`          | `podman push image-registry.openshift-image-registry.svc:5000/<project>/<image>:latest` |
| View PV / PVC / SC             | `kubectl get pv/pvc/sc`                              | `oc get pv/pvc/sc`                               |
| Postgres inside pod            | `kubectl exec -it <pod> -- psql -U postgres`        | `oc rsh <pod>` → `psql -U postgres`            |







---

# Homework 4: openshift-etl-elt Instructions 

Check professor's `DEPLOYMENT.md` and `deployment-guide.md`


## Step 1: Login to OpenShift
```bash
oc login --token=YOUR_TOKEN --server=https://api.sandbox.x8i5.p1.openshiftapps.com:6443
```

## Step 2: Verify Project
```bash
oc project
```



## Step 6: Build ETL Container Image

**Option A: OpenShift BuildConfig**
```bash
oc create secret generic github-credentials \
  --from-literal=username=YOUR_GITHUB_USERNAME \
  --from-literal=password=YOUR_GITHUB_PAT \
  --type=kubernetes.io/basic-auth
oc apply -f openshift/etl-buildconfig.yaml
oc start-build tiktok-etl
oc logs -f buildconfig/tiktok-etl
oc get imagestream tiktok-etl
```

**Option B: Local Build + Push**
```bash
podman build -t tiktok-etl:latest -f Containerfile .
podman tag tiktok-etl:latest \
  image-registry.openshift-image-registry.svc:5000/tiktok-etl/tiktok-etl:latest
podman login -u $(oc whoami) -p $(oc whoami -t) \
  default-route-openshift-image-registry.apps.sandbox.x8i5.p1.openshiftapps.com
podman push tiktok-etl:latest \
  default-route-openshift-image-registry.apps.sandbox.x8i5.p1.openshiftapps.com/tiktok-etl/tiktok-etl:latest
```

