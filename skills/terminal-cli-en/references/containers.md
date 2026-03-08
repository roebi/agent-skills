# Containers Reference

## Podman

Podman is a daemonless, rootless-capable container engine compatible with Docker CLI.

### Images

```bash
podman images                             # List local images
podman pull image:tag                     # Pull from registry
podman build -t name:tag .               # Build from Dockerfile in current dir
podman build -t name:tag -f path/Dockerfile .
podman rmi image                          # Remove image
podman image prune                        # Remove dangling images
podman image prune -a                     # Remove all unused images
podman tag source:tag target:tag          # Tag an image
podman push image:tag registry/repo:tag  # Push to registry
podman save -o image.tar image:tag       # Export image to file
podman load -i image.tar                 # Import image from file
```

### Run containers

```bash
podman run image                          # Run and remove
podman run --rm image                     # Auto-remove on exit
podman run -it image bash                 # Interactive shell
podman run -d --name myapp image          # Detached, named
podman run -p 8080:80 image               # Port: host:container
podman run -v /host/path:/container/path image  # Bind mount
podman run --env KEY=VALUE image          # Environment variable
podman run --env-file .env image          # Env from file
podman run --network mynet image          # Attach to network
podman run --memory 512m image            # Memory limit
podman run --cpus 1.5 image              # CPU limit
```

### Manage containers

```bash
podman ps                                 # Running containers
podman ps -a                             # All containers (including stopped)
podman stop container                    # Graceful stop
podman kill container                    # Force stop (SIGKILL)
podman start container                   # Start a stopped container
podman restart container                 # Restart
podman rm container                      # Remove stopped container
podman rm -f container                   # Force remove running container
podman container prune                   # Remove all stopped containers
```

### Inspect & debug

```bash
podman logs container                    # View logs
podman logs -f container                 # Follow (tail) logs
podman logs --tail 100 container         # Last 100 lines
podman exec -it container bash           # Open shell in running container
podman exec container command            # Run command non-interactively
podman inspect container                 # Full metadata as JSON
podman stats                             # Live CPU/memory per container
podman top container                     # Processes inside container
podman diff container                    # Changed files vs image
podman cp container:/path ./local/       # Copy file out of container
podman cp ./local/file container:/path   # Copy file into container
```

### Networks

```bash
podman network ls                        # List networks
podman network create mynet              # Create network
podman network inspect mynet             # Network details
podman network rm mynet                  # Remove network
podman network connect mynet container   # Connect running container
podman network disconnect mynet container
```

### Volumes

```bash
podman volume ls                         # List volumes
podman volume create myvol              # Create named volume
podman volume inspect myvol             # Volume details
podman volume rm myvol                  # Remove volume
podman volume prune                     # Remove all unused volumes
```

### Pods

```bash
podman pod create --name mypod           # Create pod
podman pod ps                            # List pods
podman pod start mypod
podman pod stop mypod
podman pod rm mypod
podman pod inspect mypod
```

### Podman Compose

```bash
podman-compose up -d                     # Start services detached
podman-compose down                      # Stop and remove
podman-compose down -v                   # Also remove volumes
podman-compose logs                      # All service logs
podman-compose logs -f service           # Follow a specific service
podman-compose ps                        # Status of services
podman-compose restart service           # Restart a service
podman-compose exec service bash         # Shell into service
podman-compose pull                      # Pull latest images
```

---

## Kubernetes — kubectl

### Context & cluster

```bash
kubectl config get-contexts              # List available contexts
kubectl config current-context           # Show active context
kubectl config use-context mycontext     # Switch context
kubectl cluster-info                     # Cluster endpoint info
kubectl version                          # Client and server version
```

### Namespaces

```bash
kubectl get namespaces
kubectl create namespace myns
kubectl delete namespace myns
# Set default namespace for current context
kubectl config set-context --current --namespace=myns
```

### Pods

```bash
kubectl get pods                         # Current namespace
kubectl get pods -A                      # All namespaces
kubectl get pods -o wide                 # Include node and IP
kubectl get pods -w                      # Watch for changes
kubectl describe pod podname             # Full details and events
kubectl logs podname                     # Stdout logs
kubectl logs -f podname                  # Follow logs
kubectl logs podname -c container        # Specific container
kubectl logs --previous podname          # Previous container instance
kubectl exec -it podname -- bash         # Interactive shell
kubectl exec podname -- command          # Run command
kubectl delete pod podname               # Delete (will restart if managed)
kubectl delete pod podname --force       # Force delete immediately
```

### Deployments

```bash
kubectl get deployments
kubectl describe deployment name
kubectl scale deployment name --replicas=3
kubectl rollout status deployment/name
kubectl rollout history deployment/name
kubectl rollout undo deployment/name          # Roll back one version
kubectl rollout undo deployment/name --to-revision=2
kubectl set image deployment/name container=image:tag  # Update image
```

### Services & ingress

```bash
kubectl get services
kubectl get ingress
kubectl describe service name
kubectl port-forward svc/name 8080:80         # Local → service
kubectl port-forward pod/name 8080:80         # Local → pod
```

### Apply & delete resources

```bash
kubectl apply -f manifest.yaml
kubectl apply -f ./directory/
kubectl delete -f manifest.yaml
kubectl apply -k ./kustomize-dir/

# Dry run (no changes applied)
kubectl apply -f manifest.yaml --dry-run=client
```

### ConfigMaps & Secrets

```bash
kubectl get configmaps
kubectl describe configmap name
kubectl get secrets
kubectl describe secret name
kubectl create secret generic mysecret \
  --from-literal=key=value \
  --from-file=cert.pem
kubectl create configmap myconfig --from-file=config.yaml
```

### Inspection & debugging

```bash
kubectl get all                          # All resources in namespace
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl top pods                         # CPU/memory (metrics-server required)
kubectl top nodes
kubectl get pods -o yaml                 # Full YAML of all pods
kubectl get pod name -o jsonpath='{.spec.containers[*].image}'
```

---

## Helm

### Repos

```bash
helm repo add stable https://charts.helm.sh/stable
helm repo add myrepo https://example.com/charts
helm repo update                         # Refresh all repos
helm repo list
helm repo remove myrepo
```

### Search

```bash
helm search repo keyword                 # Search configured repos
helm search hub keyword                  # Search Artifact Hub (public)
```

### Install & upgrade

```bash
helm install release-name chart-name
helm install myapp myrepo/chart \
  --namespace myns \
  --create-namespace \
  --values values.yaml \
  --set key=value \
  --set-string key=stringvalue

helm upgrade myapp myrepo/chart --values values.yaml
helm upgrade --install myapp chart/     # Install if not exists, else upgrade

# Atomic: roll back automatically if hooks fail
helm upgrade --install --atomic myapp chart/
```

### Releases

```bash
helm list                                # Current namespace
helm list -A                             # All namespaces
helm status myapp                        # Release details
helm history myapp                       # Revision history
helm rollback myapp 1                    # Roll back to revision 1
helm uninstall myapp
helm uninstall myapp --keep-history      # Uninstall but keep history
```

### Debug & template

```bash
helm template myapp chart/ --values values.yaml   # Render templates locally
helm install myapp chart/ --dry-run --debug        # Server-side dry run
helm lint chart/                                   # Check chart for issues
helm get values myapp                              # Values used in release
helm get manifest myapp                            # Rendered manifests
```

### Chart info

```bash
helm show values chart-name              # Default values.yaml
helm show chart chart-name               # Chart.yaml metadata
helm show all chart-name                 # Everything
```

### Package & distribute

```bash
helm package ./mychart                   # Create .tgz
helm push mychart-0.1.0.tgz oci://registry.example.com/charts
helm pull myrepo/chart --untar           # Download and extract chart
```
