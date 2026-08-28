---
title_pl: "Kubernetes od zera #1 – Prosty klaster"
title_en: "Kubernetes from scratch #1 – Simple cluster"
date: 2025-11-14
author: "Marcin Piotrowski"
tags: ["Kubernetes", "DevOps", "K8s", "Deployment", "Service", "ConfigMap"]
description_pl: Pierwszy wpis z serii o Kubernetesie – stworzenie prostego klastra od zera.
description_en: First post in the Kubernetes series – building a simple cluster from scratch.
---

## PL

## 1. Czym jest Kubernetes

Kubernetes (K8S) służy do automatycznego zarządzania kontenerami z różnymi usługami. Jego głównymi korzyściami są:

- Skalowanie horyzontalne: łatwo uruchamiasz wiele replik aplikacji.
- Równoważenie ruchu wewnątrz klastra: Service rozdziela żądania na Pody.
- Self-healing: gdy Pody padają, kontrolery odtwarzają je zgodnie z deklaracją.
- Deklaratywność: opisujesz stan w YAML, a kontrolery dążą do zgodności.

Warto na starcie rozróżnić:

- Skalowanie zapewnia Deployment/ReplicaSet (liczba replik).
- Rozdział ruchu między Pody realizuje Service.
- Publiczny Load Balancer zwykle dostarcza cloud provider; lokalnie k3s ma wbudowany ServiceLB.

### 1.1. Kluczowe pojęcia

#### 1.1.1. Cluster

**Cluster** znajduje się najwyżej w hierarchii, wszystko dzieje się wewnątrz niego. Składa się z:

- **Control Plane** — centrum dowodzenia, które zarządza clustrem. Składa się min. z:
    - kube-apiserver (API),
    - scheduler (przypisuje Pody do Node'ów),
    - controller-manager (kontrolery),
    - etcd (magazyn stanu).
- **Node** — wirtualna bądź fizyczna maszyna, w której uruchamiane są **Workloady**.

#### 1.1.2. Workload

**Workload** to aplikacja uruchamiana w clustrze. Kubernetes na podstawie workloadu tworzy Pody, w których bezpośrednio są uruchamiane kontenery. W architekturze mikroserwisów jeden workload odpowiada jednemu mikroserwisowi. Istnieje kilka typów workloadów:

- **Deployment** — najczęściej wykorzystywany do bezstanowych aplikacji, czyli mikroserwisów,
  gdzie każdy Pod może być w dowolnej chwili doskalowany i zastąpiony nowym (rolling update).
- **ReplicaSet** — zarządza liczbą replik Podów (pilnuje, żeby było X kopii). Zwykle NIE
  tworzysz go ręcznie — Deployment tworzy go automatycznie pod spodem.
- **StatefulSet** — dla aplikacji stanowych; zapewnia stabilne nazwy Podów, uporządkowane
  rollouty, integrację z PersistentVolumeClaims.
- **DaemonSet** — uruchamia jedną instancję Poda na każdym (lub wybranym) Node'dzie
  (np. loggery, monitoring).
- **Job/CronJob** — jednorazowe zadania wsadowe / cykliczne.

**Pod** jest najmniejszą jednostką w K8S, najczęściej składa się z jednego kontenera. Pod jest wrapperem dla kontenerów; Kubernetes zarządza Podami, a nie kontenerami. Z tego powodu nie tworzy się ich ręcznie, wystarczy stworzyć workload, a K8S ogarnie resztę.

#### 1.1.3. Service

**Service** umożliwia udostępnienie endpointów aplikacji uruchomionych wewnątrz Podów. Niezbędny, gdy naszą aplikacją jest mikroserwis z REST API i chcemy, żeby jego endpointy były dostępne na zewnątrz clustra. W praktyce oznacza to, że możemy mieć wiele Podów z tą samą usługą i dostęp do nich będzie możliwy tylko przez jeden adres IP, z kolei control plane clustra będzie decydować, który Pod faktycznie obsłuży żądanie. Dla końcowego użytkownika jest to niewidoczne, bo typowa aplikacja webowa nie przechowuje stanu, więc nie ma różnicy pomiędzy Podami.

Istnieje kilka typów Service:

- **ClusterIP** — domyślny, udostępnia serwis tylko wewnątrz clustra. Pody mogą komunikować się
  ze sobą, ale z zewnątrz nie ma dostępu. Przydatne, jeśli nie chcemy wystawiać jakiegoś serwisu
  na zewnątrz.
- **NodePort** — udostępnia serwis na określonym porcie każdego Node'a w clustrze. Dzięki temu
  można się dostać do aplikacji z zewnątrz, używając adresu IP Node'a i portu.
- **LoadBalancer** — udostępnia serwis na zewnątrz, ale wymagany jest zewnętrzny load balancer.
  Kubernetes nie posiada wbudowanego load balancera, więc trzeba go dołączyć samodzielnie, często
  zapewnia go cloud provider.
- **ExternalName** — mapuje serwis na zewnętrzną domenę DNS. Używane, gdy chcemy się odwołać do
  zewnętrznych zasobów tak, jakby były wewnątrz clustra.

#### 1.1.4. ConfigMap

W Kubernetesie aplikacja powinna być oddzielona od konfiguracji. Do tego celu służy **ConfigMap** - obiekt K8S służący do przechowywania danych konfiguracyjnych w formie par _klucz-wartość_.

Przykładowe zastosowania:
* ustawienie portu aplikacji
* nazwy środowisk (`dev`, `stage`, `prod`)
* teksty komunikatów
* adresy innych serwisów

Bez ConfigMap każda zmiana konfiguracji oznacza rebuild obrazu Dockera oraz brak podziału pomiędzy kodem a środowiskiem uruchomieniowym. Dzięki ConfigMap można korzystać z jednej wersji obrazu na wielu środowiskach i zarządzać wszystkim centralnie z poziomu Kubernetesa.

## 2. Implementacja

W tej części wpisu sprawdzimy, jak opisane wyżej pojęcia znajdują zastosowanie w implementacji prostego clustra.

> **Uwaga**: Zakładam, że Kubernetes jest już zainstalowany. Ja wykorzystałem w tym celu Rancher Desktop — darmową alternatywę dla Docker Desktop z wbudowanym K8S. Dobrym ćwiczeniem jest postawienie wszystkiego od absolutnego zera, ale na początek zdecydowałem się uprościć ten krok, aby skupić się na reszcie. W kolejnych wpisach wrócę do tego tematu.

Najpierw sprawdźmy, czy istnieje jakikolwiek cluster:

```
PS C:\blog\k8s> kubectl config get-contexts
CURRENT   NAME              CLUSTER           AUTHINFO          NAMESPACE
*         rancher-desktop   rancher-desktop   rancher-desktop
```

Jest dostępny jeden cluster o nazwie `rancher-desktop` (domyślny cluster zapewniany przez Ranchera). Gwiazdka (`*`) oznacza, że jest to aktywny cluster i wszystkie komendy będą na nim wykonywane. Na potrzeby tego wpisu to nam wystarczy, aczkolwiek warto wiedzieć, że cała konfiguracja jest brana z folderu `C:\Users\{user}\.kube\config` i można łatwo ją rozszerzać o kolejne clustry.
Przy okazji możemy jeszcze sprawdzić, z czego składa się nasz cluster, następującymi komendami:

```
PS C:\blog\k8s> kubectl get nodes
NAME       STATUS   ROLES                  AGE    VERSION
pf30xeyh   Ready    control-plane,master   289d   v1.31.4+k3s1
PS C:\blog\k8s_dashboard\k8s> kubectl get deployments
No resources found in default namespace.
PS C:\blog\k8s_dashboard\k8s> kubectl get pods
No resources found in default namespace.
```

Widzimy, że cluster składa się tylko z jednego Node'a, który odgrywa rolę control-plane. Na początek jeden Node nam wystarczy, w przyszłości spróbujemy stworzyć ich więcej. Ponadto w clustrze nie ma żadnych Deploymentów ani Podów.
Gdy mamy już cluster, potrzebujemy obrazu aplikacji, który chcemy w nim wdrożyć. Do celów testowych stworzyłem proste REST API z jednym endpointem:

```
PS C:\blog\k8s> iwr http://localhost:8082/api/hello | Select-Object -ExpandProperty Content
{"message":"Hello World"}
```

Następnie zbudowałem dockerowy obraz:

```
PS C:\blog\k8s_dashboard\k8s> docker images
REPOSITORY                                                    TAG                    IMAGE ID       CREATED         SIZE
demo-api                                                      1.0                    186d7473fc93   4 days ago      285MB
```

### 2.1. Workload

Mamy wszystko, aby zabrać się do stworzenia pierwszego workloadu z naszą aplikacją. Z racji że aplikacja jest bezstanowa, wykorzystamy w tym celu **Deployment**. Workload (jak i każdy inny obiekt w k8s) definiujemy w postaci pliku YAML. Poniżej zamieściłem definicję naszego Deploymentu. Pochodzi ona z oficjalnej dokumentacji k8s, zmieniłem jedynie nazwę wykorzystywanego obrazu.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-api
  labels:
    app: demo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-api
  template:
    metadata:
      labels:
        app: demo-api
    spec:
      containers:
        - name: demo-api
          image: demo-api:1.0
          imagePullPolicy: Never
          ports:
            - containerPort: 8082
```

Przyjrzyjmy się kluczowym polom w definicji:

- `replicas: 3` — ile kopii Poda chcemy uruchomić (horyzontalne skalowanie)
- `selector.matchLabels` — mówi Deploymentowi, które Pody do niego należą (po labelce
  `app: demo-api`)
- `template.metadata.labels` — labelka przypisana do każdego Poda, musi pasować do `selector`
- `image: demo-api:1.0` — nazwa lokalnego obrazu Dockera
- `imagePullPolicy: Never` — nie próbuj ściągać obrazu z internetu, użyj lokalnego
- `containerPort: 8082` — port, na którym nasłuchuje aplikacja w kontenerze (to tylko
  dokumentacja, faktyczny dostęp zapewni Service)

Następnie przy wykorzystaniu poniższej komendy wdrożyłem mój Deployment w clustrze k8s:

```
PS C:\blog\k8s> kubectl apply -f deployment.yaml
deployment.apps/demo-api created
PS C:\blog\k8s> kubectl get deployments
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
demo-api   3/3     3            3           8s
PS C:\blog\k8s> kubectl get pods
NAME                       READY   STATUS    RESTARTS   AGE
demo-api-8886d869b-6z9c7   1/1     Running   0          16s
demo-api-8886d869b-xzctq   1/1     Running   0          16s
demo-api-8886d869b-zgxfd   1/1     Running   0          16s
```

Widać, że Deployment został poprawnie utworzony i zgodnie z tym, co zdefiniowałem wcześniej, mamy 3 Pody z naszą aplikacją.
Warto zwrócić uwagę na nazwy Podów — wszystkie zawierają dziwny ciąg znaków `8886d869b`. To **hash ReplicaSetu**, który Deployment automatycznie stworzył pod spodem. Możemy to sprawdzić w następujący sposób:

```
PS C:\blog\k8s> kubectl get replicasets
NAME                 DESIRED   CURRENT   READY   AGE
demo-api-8886d869b   3         3         3       22m
```

Deployment nie zarządza Podami bezpośrednio — tworzy **ReplicaSet**, a ten już pilnuje, żeby był dokładnie 3 Pody. Dzięki temu podczas aktualizacji aplikacji (np. nowej wersji obrazu) Kubernetes może stworzyć nowy **ReplicaSet** z innym hashem i stopniowo zastępować stare Pody nowymi (rolling update).

### 2.2. Service

Jest tylko jeden problem — nie mamy dostępu do żadnego z portów wystawianych przez Pody z aplikacją. Aby temu zaradzić, potrzebny jest **Service**.
Service działa jak "brama" do naszych Podów. Pody mogą się restartować, zmieniać IP, ale Service zapewnia stały adres, przez który zawsze możemy się z nimi połączyć. Poniżej definicja Service dla naszej aplikacji:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-api
spec:
  selector:
    app: demo-api
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8082
  type: LoadBalancer
```

Kluczowe pola:

- `selector.app: demo-api` — Service znajduje wszystkie Pody z tą labelką (te z naszego
  Deploymentu)
- `port: 8080` — port, na którym Service będzie dostępny
- `targetPort: 8082` — port w kontenerze, na który Service przekieruje ruch (nasz REST API
  nasłuchuje na 8082)
- `type: LoadBalancer` — w środowisku chmurowym utworzyłby zewnętrzny load balancer. Rancher Desktop symuluje to lokalnie i automatycznie mapuje Service na localhost dzięki czemu nie musimy używać wewnętrznych IP. Pod spodem tworzy również NodePort jako backup.

Wdrażamy Service:

```
PS C:\blog\k8s> kubectl apply -f service.yaml
service/demo-api created
PS C:\blog\k8s> kubectl get services
NAME         TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)          AGE
demo-api     LoadBalancer   10.43.28.41   192.168.127.2   8080:32026/TCP   6s
```

Przyjrzyjmy się, co oznaczają poszczególne IP:

- `CLUSTER-IP: 10.43.28.41` — wewnętrzny adres Service w clustrze, używany przez inne Pody do
  komunikacji
- `EXTERNAL-IP: 192.168.127.2` — IP Node'a w Rancher Desktop (wirtualna maszyna z K8s). W k3s typ LoadBalancer obsługuje wbudowany ServiceLB (Klipper), który otwiera port na hoście VM, a Rancher Desktop mapuje go dodatkowo na localhost.
- `8080` — port, na którym Service jest dostępny
- `32026` — automatycznie przydzielony NodePort (backup dostępu przez `<NodeIP>:32026`)

**Dlaczego nie NodePort?**

W prawdziwym clustrze chmurowym (AWS/GCP) `EXTERNAL-IP` byłby publicznym adresem w internecie. Rancher Desktop symuluje to lokalnie i dodatkowo mapuje `192.168.127.2:8080` na `localhost:8080` dla wygody.
Teraz możemy przetestować naszą aplikację:

```
PS C:\blog\k8s> curl -s http://localhost:8080/api/hello
{"message":"Hello World"}
```

Działa! A przynajmniej musisz uwierzyć mi na słowo, bo ten curl niczym się nie różni od przykładu, który umieściłem wcześniej. Tym razem różnica jest taka, że wysyłamy żądanie nie prosto do webservera aplikacji, lecz do Service, który automatycznie rozdziela ruch między wszystkie 3 Pody. Dla nas to niewidoczne — zawsze łączymy się przez `localhost:8080`, a Kubernetes decyduje, który Pod obsłuży żądanie.

### 2.3. ConfigMap

Na obecną chwilę aplikacja działa na sztywno, po zbudowaniu obrazu nie możemy nic w niej zmienić. Aby to naprawić, dodam ConfigMap. Załóżmy że aplikacja obsługuje następujące zmienne środowiskowe:\

* `APP_PORT`
* `APP_MESSAGE`

Tworzymy plik `configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo-api-config
data:
  APP_PORT: "8082"
  APP_MESSAGE: "Hello from ConfigMap"
```

Po stworzeniu ConfigMap zmieniam jeszcze deployment, aby z niej korzystał:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-api
  labels:
    app: demo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-api
  template:
    metadata:
      labels:
        app: demo-api
    spec:
      containers:
      - name: demo-api
        image: demo-api:1.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8082
        envFrom:
        - configMapRef:
            name: demo-api-config
```

Nowy fragment:

* `envFrom.configMapRef.name` — wszystkie wartości z ConfigMap trafiają do Poda jako zmienne środowiskowe

Wdrażamy nowy deployment oraz ConfigMap do clustra:

```
PS C:\blog\k8s> kubectl apply -f deployment.yaml
deployment.apps/demo-api configured
PS C:\blog\k8s> kubectl apply -f configmap.yaml
configmap/demo-api-config created
PS C:\blog\k8s> kubectl get configmaps
NAME              DATA   AGE
demo-api-config   2      5s
```

Od tej pory Kubernetes przechowuje konfigurację naszej aplikacji w jednym miejscu i może ją wstrzykiwać do Podów.

Dla pewności możemy sprawdzić, czy zmienne faktycznie działają:

```
PS C:\blog\k8s> kubectl exec -it demo-api-xxxx -- printenv | findstr APP
APP_PORT=8082
APP_MESSAGE=Hello from ConfigMap
```

Od teraz zmiana tekstu w ConfigMap nie wymaga rebuilda obrazu Dockera – wystarczy kubectl apply, a po restarcie Podów aplikacja dostaje nowe wartości.

## 3. Podsumowanie

W tym wpisie stworzyliśmy prosty, ale w pełni funkcjonalny cluster Kubernetes z:

* Deploymentem zarządzającym replikami Podów
* Service typu LoadBalancer
* ConfigMap jako zewnętrznym źródłem konfiguracji aplikacji
* Automatycznym self-healingiem

Dzięki ConfigMap:

* nie trzeba rebuildować obrazu przy zmianie konfiguracji,
* łatwo wspierać różne środowiska (dev/stage/prod),
* konfiguracja znajduje się w jednym, kontrolowanym miejscu.

## EN

## 1. What is Kubernetes

Kubernetes (K8S) is used for automated container management across different services. Its main benefits are:

- Horizontal scaling: easily run multiple replicas of your application.
- In-cluster traffic balancing: Service distributes requests across Pods.
- Self-healing: when Pods crash, controllers recreate them according to the declaration.
- Declarativeness: you describe the desired state in YAML, and controllers work to maintain it.

It's worth distinguishing from the start:

- Scaling is handled by Deployment/ReplicaSet (replica count).
- Traffic distribution between Pods is done by Service.
- A public Load Balancer is usually provided by the cloud provider; locally, k3s has a built-in ServiceLB.

### 1.1. Key concepts

#### 1.1.1. Cluster

A **Cluster** sits at the top of the hierarchy — everything happens inside it. It consists of:

- **Control Plane** — the command center that manages the cluster. It includes, among others:
    - kube-apiserver (API),
    - scheduler (assigns Pods to Nodes),
    - controller-manager (controllers),
    - etcd (state store).
- **Node** — a virtual or physical machine on which **Workloads** are run.

#### 1.1.2. Workload

A **Workload** is an application running in the cluster. Kubernetes creates Pods based on the workload, and containers run directly inside those Pods. In a microservice architecture, one workload corresponds to one microservice. There are several types of workloads:

- **Deployment** — most commonly used for stateless applications, i.e. microservices, where any Pod can be scaled out or replaced at any time (rolling update).
- **ReplicaSet** — manages the number of Pod replicas (ensures there are exactly X copies). You typically do NOT create it manually — Deployment creates it automatically under the hood.
- **StatefulSet** — for stateful applications; provides stable Pod names, ordered rollouts, and integration with PersistentVolumeClaims.
- **DaemonSet** — runs one Pod instance on every (or selected) Node (e.g. loggers, monitoring).
- **Job/CronJob** — one-off batch tasks / recurring scheduled tasks.

A **Pod** is the smallest unit in K8S and typically consists of a single container. A Pod is a wrapper for containers; Kubernetes manages Pods, not containers directly. For this reason, you don't create them manually — just create a workload and K8S handles the rest.

#### 1.1.3. Service

A **Service** exposes the endpoints of applications running inside Pods. It's essential when your application is a microservice with a REST API and you want its endpoints to be accessible from outside the cluster. In practice, this means you can have multiple Pods running the same service, all reachable through a single IP address, while the cluster's control plane decides which Pod actually handles each request. This is transparent to the end user — a typical web application is stateless, so there's no difference between Pods.

There are several types of Service:

- **ClusterIP** — the default type; exposes the service only within the cluster. Pods can communicate with each other, but there's no external access. Useful when you don't want to expose a service outside the cluster.
- **NodePort** — exposes the service on a specific port on every Node in the cluster. This allows access from outside using the Node's IP address and the assigned port.
- **LoadBalancer** — exposes the service externally, but requires an external load balancer. Kubernetes doesn't have a built-in load balancer, so one must be provided separately — often by the cloud provider.
- **ExternalName** — maps the service to an external DNS name. Used when you want to reference external resources as if they were inside the cluster.

#### 1.1.4. ConfigMap

In Kubernetes, application configuration should be separated from the application itself. This is the purpose of a **ConfigMap** — a K8S object used to store configuration data as _key-value_ pairs.

Common use cases:
* setting the application port
* environment names (`dev`, `stage`, `prod`)
* message texts
* addresses of other services

Without ConfigMap, every configuration change requires rebuilding the Docker image, and there's no separation between code and runtime environment. With ConfigMap, you can use a single image across multiple environments and manage everything centrally from within Kubernetes.

## 2. Implementation

In this section, we'll see how the concepts described above apply in practice when implementing a simple cluster.

> **Note**: I'm assuming Kubernetes is already installed. I used Rancher Desktop for this — a free alternative to Docker Desktop with built-in K8S. Setting everything up from absolute scratch is a great exercise, but for now I decided to simplify this step and focus on the rest. I'll come back to this topic in future posts.

First, let's check if any cluster exists:

```
PS C:\blog\k8s> kubectl config get-contexts
CURRENT   NAME              CLUSTER           AUTHINFO          NAMESPACE
*         rancher-desktop   rancher-desktop   rancher-desktop
```

There is one cluster available named `rancher-desktop` (the default cluster provided by Rancher). The asterisk (`*`) indicates it's the active cluster and all commands will be executed against it. For the purposes of this post, that's enough — though it's worth knowing that all configuration is read from `C:\Users\{user}\.kube\config` and can easily be extended with additional clusters.
While we're at it, let's also check what our cluster is made of:

```
PS C:\blog\k8s> kubectl get nodes
NAME       STATUS   ROLES                  AGE    VERSION
pf30xeyh   Ready    control-plane,master   289d   v1.31.4+k3s1
PS C:\blog\k8s_dashboard\k8s> kubectl get deployments
No resources found in default namespace.
PS C:\blog\k8s_dashboard\k8s> kubectl get pods
No resources found in default namespace.
```

We can see the cluster consists of a single Node, which also acts as the control plane. One Node is enough for now — in the future we'll try creating more. There are also no Deployments or Pods in the cluster yet.
Now that we have a cluster, we need an application image to deploy. For testing purposes, I created a simple REST API with a single endpoint:

```
PS C:\blog\k8s> iwr http://localhost:8082/api/hello | Select-Object -ExpandProperty Content
{"message":"Hello World"}
```

Then I built a Docker image:

```
PS C:\blog\k8s_dashboard\k8s> docker images
REPOSITORY                                                    TAG                    IMAGE ID       CREATED         SIZE
demo-api                                                      1.0                    186d7473fc93   4 days ago      285MB
```

### 2.1. Workload

We have everything we need to create our first workload. Since the application is stateless, we'll use a **Deployment**. Workloads (like any other object in k8s) are defined as YAML files. Below is the definition of our Deployment — taken from the official k8s documentation, with only the image name changed.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-api
  labels:
    app: demo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-api
  template:
    metadata:
      labels:
        app: demo-api
    spec:
      containers:
        - name: demo-api
          image: demo-api:1.0
          imagePullPolicy: Never
          ports:
            - containerPort: 8082
```

Let's look at the key fields:

- `replicas: 3` — how many Pod copies we want to run (horizontal scaling)
- `selector.matchLabels` — tells the Deployment which Pods belong to it (via the `app: demo-api` label)
- `template.metadata.labels` — label assigned to each Pod, must match `selector`
- `image: demo-api:1.0` — name of the local Docker image
- `imagePullPolicy: Never` — don't try to pull the image from the internet, use the local one
- `containerPort: 8082` — the port the application listens on inside the container (this is documentation only; actual external access is provided by the Service)

I then deployed my Deployment to the k8s cluster:

```
PS C:\blog\k8s> kubectl apply -f deployment.yaml
deployment.apps/demo-api created
PS C:\blog\k8s> kubectl get deployments
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
demo-api   3/3     3            3           8s
PS C:\blog\k8s> kubectl get pods
NAME                       READY   STATUS    RESTARTS   AGE
demo-api-8886d869b-6z9c7   1/1     Running   0          16s
demo-api-8886d869b-xzctq   1/1     Running   0          16s
demo-api-8886d869b-zgxfd   1/1     Running   0          16s
```

The Deployment was created successfully and, as defined, we have 3 Pods running our application.
Notice the Pod names — they all contain a strange string of characters, `8886d869b`. That's the **ReplicaSet hash**, which Deployment automatically created under the hood. We can verify this:

```
PS C:\blog\k8s> kubectl get replicasets
NAME                 DESIRED   CURRENT   READY   AGE
demo-api-8886d869b   3         3         3       22m
```

Deployment doesn't manage Pods directly — it creates a **ReplicaSet**, which in turn ensures there are exactly 3 Pods running. This way, when updating the application (e.g. a new image version), Kubernetes can create a new **ReplicaSet** with a different hash and gradually replace old Pods with new ones (rolling update).

### 2.2. Service

There's just one problem — we have no access to any of the ports exposed by the Pods. To fix this, we need a **Service**.
A Service acts as a "gateway" to our Pods. Pods may restart and change IPs, but the Service provides a stable address through which we can always reach them. Below is the Service definition for our application:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-api
spec:
  selector:
    app: demo-api
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8082
  type: LoadBalancer
```

Key fields:

- `selector.app: demo-api` — the Service finds all Pods with this label (those from our Deployment)
- `port: 8080` — the port on which the Service will be available
- `targetPort: 8082` — the port inside the container to which the Service will forward traffic (our REST API listens on 8082)
- `type: LoadBalancer` — in a cloud environment this would create an external load balancer. Rancher Desktop simulates this locally and automatically maps the Service to localhost, so we don't need to use internal IPs. It also creates a NodePort as a backup under the hood.

Deploying the Service:

```
PS C:\blog\k8s> kubectl apply -f service.yaml
service/demo-api created
PS C:\blog\k8s> kubectl get services
NAME         TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)          AGE
demo-api     LoadBalancer   10.43.28.41   192.168.127.2   8080:32026/TCP   6s
```

Let's break down what each IP means:

- `CLUSTER-IP: 10.43.28.41` — the internal address of the Service within the cluster, used by other Pods for communication
- `EXTERNAL-IP: 192.168.127.2` — the Node's IP in Rancher Desktop (the virtual machine running K8s). In k3s, the LoadBalancer type uses the built-in ServiceLB (Klipper), which opens a port on the VM host, and Rancher Desktop additionally maps it to localhost.
- `8080` — the port on which the Service is available
- `32026` — automatically assigned NodePort (backup access via `<NodeIP>:32026`)

**Why not NodePort?**

In a real cloud cluster (AWS/GCP), `EXTERNAL-IP` would be a public internet address. Rancher Desktop simulates this locally and additionally maps `192.168.127.2:8080` to `localhost:8080` for convenience.
Now we can test our application:

```
PS C:\blog\k8s> curl -s http://localhost:8080/api/hello
{"message":"Hello World"}
```

It works! At this point you'll have to take my word for it, since this curl output looks identical to the earlier example. The difference this time is that we're sending the request not directly to the application's web server, but to the Service, which automatically distributes traffic across all 3 Pods. From our perspective it's invisible — we always connect via `localhost:8080`, and Kubernetes decides which Pod handles the request.

### 2.3. ConfigMap

Right now the application is hardcoded — once the image is built, nothing can be changed. To fix this, I'll add a ConfigMap. Let's say the application supports the following environment variables:

* `APP_PORT`
* `APP_MESSAGE`

We create a `configmap.yaml` file:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: demo-api-config
data:
  APP_PORT: "8082"
  APP_MESSAGE: "Hello from ConfigMap"
```

After creating the ConfigMap, I also update the Deployment to use it:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-api
  labels:
    app: demo-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo-api
  template:
    metadata:
      labels:
        app: demo-api
    spec:
      containers:
      - name: demo-api
        image: demo-api:1.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8082
        envFrom:
        - configMapRef:
            name: demo-api-config
```

The new part:

* `envFrom.configMapRef.name` — all values from the ConfigMap are injected into the Pod as environment variables

Deploying the updated Deployment and ConfigMap to the cluster:

```
PS C:\blog\k8s> kubectl apply -f deployment.yaml
deployment.apps/demo-api configured
PS C:\blog\k8s> kubectl apply -f configmap.yaml
configmap/demo-api-config created
PS C:\blog\k8s> kubectl get configmaps
NAME              DATA   AGE
demo-api-config   2      5s
```

From now on, Kubernetes stores our application's configuration in one place and can inject it into Pods.

We can verify that the variables are actually working:

```
PS C:\blog\k8s> kubectl exec -it demo-api-xxxx -- printenv | findstr APP
APP_PORT=8082
APP_MESSAGE=Hello from ConfigMap
```

From this point on, changing a value in the ConfigMap doesn't require rebuilding the Docker image — just run `kubectl apply`, and after the Pods restart the application picks up the new values.

## 3. Summary

In this post we created a simple but fully functional Kubernetes cluster with:

* A Deployment managing Pod replicas
* A LoadBalancer-type Service
* A ConfigMap as an external configuration source for the application
* Automatic self-healing

Thanks to ConfigMap:

* no image rebuild is needed when configuration changes,
* it's easy to support multiple environments (dev/stage/prod),
* configuration lives in one, centrally controlled place.