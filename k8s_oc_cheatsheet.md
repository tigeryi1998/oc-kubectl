# Kubernetes / OpenShift Cheat Sheet

This cheat sheet covers the basic commands for **Minikube/Kubernetes** using `kubectl` and **OpenShift** using `oc`.

---

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

---

## 1. Cluster / Node Info

| Action                    | kubectl (Minikube/K8s)        | oc (OpenShift)                  |
|----------------------------|-------------------------------|--------------------------------|
| Show nodes                 | `kubectl get nodes`           | `oc get nodes`                 |
| Show cluster info          | `kubectl cluster-info`        | `oc status`                    |

---

## 2. Pods

| Action                     | kubectl                       | oc                              |
|-----------------------------|-------------------------------|--------------------------------|
| List all pods               | `kubectl get pods`            | `oc get pods`                  |
| List pods in a namespace    | `kubectl get pods -n <ns>`    | `oc get pods -n <ns>`          |
| Describe pod                | `kubectl describe pod <pod>`  | `oc describe pod <pod>`        |
| View pod logs               | `kubectl logs <pod>`          | `oc logs <pod>`                |
| Exec into pod shell         | `kubectl exec -it <pod> -- /bin/sh` | `oc rsh <pod>`           |

---

## 3. Persistent Storage

| Action                     | kubectl                       | oc                              |
|-----------------------------|-------------------------------|--------------------------------|
| List PVCs                   | `kubectl get pvc`             | `oc get pvc`                   |
| Describe PVC                | `kubectl describe pvc <pvc>` | `oc describe pvc <pvc>`       |
| List PVs                    | `kubectl get pv`              | `oc get pv`                    |
| List Storage Classes        | `kubectl get sc`              | `oc get sc`                    |

---

## 4. Namespaces / Projects

| Action                     | kubectl                       | oc                              |
|-----------------------------|-------------------------------|--------------------------------|
| List namespaces             | `kubectl get ns`              | `oc get projects`              |
| Switch namespace/project    | `kubectl config set-context --current --namespace=<ns>` | `oc project <project>` |

---

## 5. Deployments / Services

| Action                     | kubectl                       | oc                              |
|-----------------------------|-------------------------------|--------------------------------|
| List deployments            | `kubectl get deployments`     | `oc get deployments`           |
| Describe deployment         | `kubectl describe deployment <dep>` | `oc describe deployment <dep>` |
| Expose a deployment         | `kubectl expose deployment <dep> --type=LoadBalancer --port=80` | `oc expose deployment <dep> --port=80` |
| Get services                | `kubectl get svc`             | `oc get svc`                   |

---

## 6. Apply / Delete Resources

| Action                     | kubectl                       | oc                              |
|-----------------------------|-------------------------------|--------------------------------|
| Apply from YAML             | `kubectl apply -f <file.yaml>` | `oc apply -f <file.yaml>`      |
| Delete resource             | `kubectl delete -f <file.yaml>` | `oc delete -f <file.yaml>`    |

---

## 7. Useful Minikube Commands

```bash
minikube start --driver=<driver>   # start local cluster (driver: vfkit, docker, podman)
minikube status                     # check cluster status
minikube dashboard                  # open K8s dashboard
minikube stop                        # stop cluster
minikube delete                      # delete cluster
```

---

## 8. Notes / Tips

- Order matters: Nodes → Pods → PVC → PV → SC.
- On Minikube, only kubectl is needed.
- On OpenShift Sandbox / EDU, use oc.
- oc can run all kubectl commands plus OpenShift extras like routes, templates, projects.

---