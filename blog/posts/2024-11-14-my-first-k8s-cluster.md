---
title_pl: "Kubernetes od zera #1 – Prosty klaster"
title_en: "Kubernetes from scratch #1 – Simple cluster"
date: 2025-11-17
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

**Workload** to aplikacja uruchamiana w clustrze. Kubernetes na podstawie workloadu tworzy Pody, w których bezpośrednio
są uruchamiane kontenery. W architekturze mikroserwisów jeden workload odpowiada jednemu mikroserwisowi. Istnieje kilka
typów workloadów:

- **Deployment** — najczęściej wykorzystywany do bezstanowych aplikacji, czyli mikroserwisów, gdzie każdy Pod może być w
  dowolnej chwili doskalowany i zastąpiony nowym (rolling update).
- **ReplicaSet** — zarządza liczbą replik Podów (pilnuje, żeby było X kopii). Zwykle NIE tworzysz go ręcznie —
  Deployment tworzy go automatycznie pod spodem.
- **StatefulSet** — dla aplikacji stanowych; zapewnia stabilne nazwy Podów, uporządkowane rollouty, integrację z
  PersistentVolumeClaims.
- **DaemonSet** — uruchamia jedną instancję Poda na każdym (lub wybranym) Node'dzie (np. loggery, monitoring).
- **Job/CronJob** — jednorazowe zadania wsadowe / cykliczne.

**Pod** jest najmniejszą jednostką w K8S, najczęściej składa się z jednego kontenera. Pod jest wrapperem dla kontenerów;
Kubernetes zarządza Podami, a nie kontenerami. Z tego powodu nie tworzy się ich ręcznie, wystarczy stworzyć workload, a
K8S ogarnie resztę.

#### 1.1.3. Service

**Service** umożliwia udostępnienie endpointów aplikacji uruchomionych wewnątrz Podów. Niezbędny, gdy naszą aplikacją
jest mikroserwis z REST API i chcemy, żeby jego endpointy były dostępne na zewnątrz clustra. W praktyce oznacza to, że
możemy mieć wiele Podów z tą samą usługą i dostęp do nich będzie możliwy tylko przez jeden adres IP, z kolei control
plane clustra będzie decydować, który Pod faktycznie obsłuży żądanie. Dla końcowego użytkownika jest to niewidoczne, bo
typowa aplikacja webowa nie przechowuje stanu, więc nie ma różnicy pomiędzy Podami.

Istnieje kilka typów Service:

- **ClusterIP** — domyślny, udostępnia serwis tylko wewnątrz clustra. Pody mogą komunikować się ze sobą, ale z zewnątrz
  nie ma dostępu. Przydatne, jeśli nie chcemy wystawiać jakiegoś serwisu na zewnątrz.
- **NodePort** — udostępnia serwis na określonym porcie każdego Node'a w clustrze. Dzięki temu można się dostać do
  aplikacji z zewnątrz, używając adresu IP Node'a i portu.
- **LoadBalancer** — udostępnia serwis na zewnątrz, ale wymagany jest zewnętrzny load balancer. Kubernetes nie posiada
  wbudowanego load balancera, więc trzeba go dołączyć samodzielnie, często zapewnia go cloud provider.
- **ExternalName** — mapuje serwis na zewnętrzną domenę DNS. Używane, gdy chcemy się odwołać do zewnętrznych zasobów
  tak, jakby były wewnątrz Clustra.

## 2. Implementacja

W tej części wpisu sprawdzimy, jak opisane wyżej pojęcia znajdują zastosowanie w implementacji prostego clustra.

> **Uwaga**: Zakładam, że Kubernetes jest już zainstalowany. Ja wykorzystałem w tym celu Rancher Desktop — darmowej
> alternatywy dla Docker Desktop z wbudowanym K8S. Dobrym ćwiczeniem jest postawienie wszystkiego od absolutnego zera,
> ale
> na początek zdecydowałem się uprościć ten krok, aby skupić się na reszcie. W kolejnych wpisach wrócę do tego tematu.

Najpierw sprawdźmy, czy istnieje jakikolwiek cluster:

```
PS C:\blog\k8s> kubectl config get-contexts
CURRENT   NAME              CLUSTER           AUTHINFO          NAMESPACE
*         rancher-desktop   rancher-desktop   rancher-desktop
```

Jest dostępny jeden cluster o nazwie `rancher-desktop` (domyślny cluster zapewniany przez Ranchera). Gwiazdka (`*`)
oznacza, że jest to aktywny cluster i wszystkie komendy będą na nim wykonywane. Na potrzeby tego wpisu to nam wystarczy,
aczkolwiek warto wiedzieć, że cała konfiguracja jest brana z folderu `C:\Users\{user}\.kube\config` i można łatwo ją
rozszerzać o kolejne clustry.

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

Widzimy, że cluster składa się tylko z jednego Node'a, który odgrywa rolę control-plane. Na początek jeden Node nam
wystarczy, w przyszłości spróbujemy stworzyć ich więcej. Ponadto w clustrze nie ma żadnych Deploymentów ani Podów.

Gdy mamy już cluster, potrzebujemy obrazu aplikacji, który chcemy w nim wdrożyć. Do celów testowych stworzyłem proste
REST API z jednym endpointem:

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

Mamy wszystko, aby zabrać się do stworzenia pierwszego workloadu z naszą aplikacją. Z racji że aplikacja jest
bezstanowa, wykorzystamy w tym celu **Deployment**.

Workload (jak i każdy inny obiekt w k8s) definiujemy w postaci pliku YAML. Poniżej zamieściłem definicję naszego
Deploymentu. Pochodzi ona z oficjalnej dokumentacji k8s, zmieniłem jedynie nazwę wykorzystywanego obrazu.

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
- `selector.matchLabels` — mówi Deploymentowi, które Pody do niego należą (po labelce `app: demo-api`)
- `template.metadata.labels` — labelka przypisana do każdego Poda, musi pasować do `selector`
- `image: demo-api:1.0` — nazwa lokalnego obrazu Dockera
- `imagePullPolicy: Never` — nie próbuj ściągać obrazu z internetu, użyj lokalnego
- `containerPort: 8082` — port, na którym nasłuchuje aplikacja w kontenerze (to tylko dokumentacja, faktyczny dostęp
  zapewni Service)

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

Widać, że Deployment został poprawnie utworzony i zgodnie z tym, co zdefiniowałem wcześniej, mamy 3 Pody z naszą
aplikacją.

Warto zwrócić uwagę na nazwy Podów — wszystkie zawierają dziwny ciąg znaków `8886d869b`. To **hash ReplicaSetu**, który
Deployment automatycznie stworzył pod spodem. Możemy to sprawdzić w następujący sposób:

```
PS C:\blog\k8s> kubectl get replicasets
NAME                 DESIRED   CURRENT   READY   AGE
demo-api-8886d869b   3         3         3       22m
```

Deployment nie zarządza Podami bezpośrednio — tworzy **ReplicaSet**, a ten już pilnuje, żeby było dokładnie 3 Pody.
Dzięki temu podczas aktualizacji aplikacji (np. nowej wersji obrazu) Kubernetes może stworzyć nowy **ReplicaSet** z
innym hashem i stopniowo zastępować stare Pody nowymi (rolling update).

### 2.2. Service

Jest tylko jeden problem — nie mamy dostępu do żadnego z portów wystawianych przez Pody z aplikacją. Aby temu zaradzić,
potrzebny jest **Service**.

Service działa jak "brama" do naszych Podów. Pody mogą się restartować, zmieniać IP, ale Service zapewnia stały adres,
przez który zawsze możemy się z nimi połączyć. Poniżej definicja Service dla naszej aplikacji:

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

- `selector.app: demo-api` — Service znajduje wszystkie Pody z tą labelką (te z naszego Deploymentu)
- `port: 8080` — port, na którym Service będzie dostępny
- `targetPort: 8082` — port w kontenerze, na który Service przekieruje ruch (nasz REST API nasłuchuje na 8082)
- `type: LoadBalancer` — w środowisku chmurowym utworzyłby zewnętrzny load balancer. Rancher Desktop symuluje to
  lokalnie i automatycznie mapuje Service na localhost, dzięki czemu nie musimy używać wewnętrznych IP. Pod spodem
  tworzy również NodePort jako backup.

Wdrażamy Service:

```
PS C:\blog\k8s> kubectl apply -f service.yaml
service/demo-api created
PS C:\blog\k8s> kubectl get services
NAME         TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)          AGE
demo-api     LoadBalancer   10.43.28.41   192.168.127.2   8080:32026/TCP   6s
```

Przyjrzyjmy się, co oznaczają poszczególne IP:

- `CLUSTER-IP: 10.43.28.41` — wewnętrzny adres Service w clustrze, używany przez inne Pody do komunikacji
- `EXTERNAL-IP: 192.168.127.2` — IP Node'a w Rancher Desktop (wirtualna maszyna z K8s). W k3s typ LoadBalancer obsługuje
  wbudowany ServiceLB (Klipper), który otwiera port na hoście VM, a Rancher Desktop mapuje go dodatkowo na localhost.
- `8080` — port, na którym Service jest dostępny
- `32026` — automatycznie przydzielony NodePort (backup dostępu przez `<NodeIP>:32026`)

**Dlaczego nie NodePort?**

W prawdziwym clustrze chmurowym (AWS/GCP) `EXTERNAL-IP` byłby publicznym adresem w internecie. Rancher Desktop symuluje
to lokalnie i dodatkowo mapuje `192.168.127.2:8080` na `localhost:8080` dla wygody.

Teraz możemy przetestować naszą aplikację:

```
PS C:\blog\k8s> curl -s http://localhost:8080/api/hello
{"message":"Hello World"}
```

Działa! A przynajmniej musisz uwierzyć mi na słowo, bo ten curl niczym się nie różni od przykładu, który umieściłem
wcześniej. Tym razem różnica jest taka, że wysyłamy żądanie nie prosto do webservera aplikacji, lecz do Service, który
automatycznie rozdziela ruch między wszystkie 3 Pody. Dla nas to niewidoczne — zawsze łączymy się przez
`localhost:8080`, a Kubernetes decyduje, który Pod obsłuży żądanie.

### 2.3. ConfigMap
Na obecną chwilę aplikacja działa na sztywno, po zbudowaniu obrazu nie możemy nic w niej zmienić. Aby to naprawić, dodam ConfigMap. Załóżmy że aplikacja obsługuje następujące zmienne środowiskowe:
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

Po stworzeniu ConfigMap zmieniam jeszcze deployment aby z niej korzystał:

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


Wdrażamy nowy deployment oraz ConfigMap do klastra:

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

* Deploymentem zarządzającym replikami Podsów
* Service typu LoadBalancer
* ConfigMap jako zewnętrznym źródłem konfiguracji aplikacji
* Automatycznym self-healingiem 

Dzięki ConfigMap:

* nie trzeba rebuildować obrazu przy zmianie konfiguracji,
* łatwo wspierać różne środowiska (dev/stage/prod),
* konfiguracja znajduje się w jednym, kontrolowanym miejscu.

## EN