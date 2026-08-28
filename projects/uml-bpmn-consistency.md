---
title_pl: "Narzędzie do weryfikacji zgodności między przypadkami użycia UML a procesami biznesowymi BPMN"
title_en: "UML Use Case and BPMN Business Process Consistency Verification Tool"
date: 2024-01-01
author: "Marcin Piotrowski"
tags: ["UML", "BPMN", "graph theory", "software engineering", "Python", "compliance testing"]
description_pl: "Narzędzie przekształcające diagramy UML i BPMN w struktury grafowe, a następnie weryfikujące ich zgodność za pomocą autorskiego algorytmu opartego na teorii grafów."
description_en: "A tool that transforms UML and BPMN diagrams into graph structures and verifies their consistency using a custom graph-based algorithm."
image: /static/images/projects/uml-bpmn/Wyplata.png
---

## PL

## BPMN vs UML

W procesie wytwarzania oprogramowania analitycy biznesowi modelują procesy w notacji BPMN, a architekci systemu definiują wymagania funkcjonalne za pomocą przypadków użycia UML. Problem polega na tym, że oba modele operują na różnych poziomach abstrakcji i nie da się ich ze sobą bezpośrednio porównać. Ręczna weryfikacja, czy proces biznesowy faktycznie realizuje to, co opisuje przypadek użycia, jest czasochłonna i podatna na błędy.

Przegląd literatury pokazał, że choć istnieją próby konwersji między tymi notacjami (np. Lubke et al. proponowali wizualizację przypadków użycia jako procesów BPMN, Bouzidi et al. badali odwrotny kierunek), nikt dotąd nie zaproponował narzędzia do **weryfikacji zgodności** między istniejącymi diagramami obu typów.

Stworzyłem narzędzie, które automatyzuje ten proces — przekształca oba typy diagramów w struktury grafowe, a następnie porównuje je za pomocą autorskiego algorytmu, generując raport zgodności.

### Przypadek użycia vs diagram przypadków użycia

Warto rozróżnić dwie rzeczy, bo łatwo je pomylić. **Przypadek użycia** (use case) to tekstowy opis interakcji aktora z systemem — lista kroków pogrupowana w scenariusz główny i scenariusze alternatywne. Przykładowo dla bankomatu:

- **Scenariusz podstawowy:** wypłata gotówki
    1. Klient umieszcza kartę w bankomacie
    2. Bankomat wyświetla menu główne
    3. Klient wybiera opcję wypłaty
    4. Bankomat prosi o wprowadzenie kwoty
    5. ...
- **Scenariusz alternatywny:** Brak środków (początek: krok 5, złączenie: krok 8)
    1. Bank odmawia autoryzacji wypłaty

**Diagram przypadków użycia** to graficzna reprezentacja — owale (przypadki użycia), aktorzy i relacje między nimi (asocjacja, `<<include>>`, `<<extend>>`). Jeden diagram może zawierać wiele przypadków użycia, ale sam nie opisuje kroków — jest mapą funkcjonalności systemu, nie instrukcją.

Moje narzędzie pracuje na **przypadkach użycia** (konkretnych krokach i scenariuszach), nie na diagramach przypadków użycia.

## Jak to działa?

Cały pipeline składa się z trzech etapów: konwersja diagramów na grafy, algorytm zgodności i generowanie raportu.

### 1. Konwersja diagramów na grafy

Pliki źródłowe BPMN (XML) oraz UML/XMI są parsowane i zamieniane na grafy skierowane.

**BPMN → Graf:** Każde zdarzenie i zadanie staje się wierzchołkiem, przepływy sekwencyjne stają się krawędziami. Poniżej przykład prostego diagramu BPMN i wynikowego grafu:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Przykładowy diagram BPMN przed parsowaniem" src="/static/images/projects/uml-bpmn/simple_bpmn.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Graf skierowany utworzony na podstawie diagramu BPMN" src="/static/images/projects/uml-bpmn/simple_graph.png" style="width: 30%; min-width: 280px;"/>
</div>

Informacje potrzebne do zbudowania grafu znajdują się w pliku XML wewnątrz elementu `bpmn:process`. Każdy element posiada unikalne `id` oraz elementy `bpmn:incoming` i `bpmn:outgoing` zawierające identyfikatory przepływów — to wystarczy, żeby odtworzyć strukturę grafu.

**UML (przypadki użycia) → Graf:** Kroki scenariusza podstawowego tworzą ścieżkę główną (kolejne wierzchołki połączone krawędziami). Scenariusze alternatywne są dołączane jako rozgałęzienia — początek i koniec alternatywnej ścieżki łączy się z odpowiednimi krokami w scenariuszu głównym, zgodnie z definicją w pliku XMI (elementy `extension` z atrybutami `guid` i `join`).

<img alt="Graf utworzony na podstawie przykładowego przypadku użycia" src="/static/images/projects/uml-bpmn/use_case_graph_example.png" width="400"/>

### 2. Algorytm zgodności

Zgodność jest mierzona dwoma niezależnymi metrykami.

**Zgodność kroków** — czy każdy krok z przypadku użycia ma swoje odzwierciedlenie jako zadanie w BPMN:

$$C_n(A,B) = \frac{|V_A \cap V_B|}{|V_A|} \cdot 100\%$$

gdzie $V_A$ to zbiór wierzchołków grafu przypadku użycia, a $V_B$ grafu BPMN. Krok i zadanie uznaje się za zgodne, jeśli ich nazwy są identyczne. BPMN jako bardziej szczegółowy opis może zawierać nadmiarowe zadania — to jest dopuszczalne, ważne, żeby wszystkie kroki z przypadku użycia były pokryte.

**Zgodność ścieżek** — czy każda ścieżka (scenariusz) z przypadku użycia występuje również w procesie biznesowym:

$$C_p(A,B) = \frac{|I|}{|A|} \cdot 100\%$$

Algorytm znajduje wszystkie ścieżki w grafie BPMN (od startu do końca), usuwa z nich wierzchołki nadmiarowe (te które nie występują w grafie przypadku użycia), a następnie sprawdza izomorfizm między tak uproszczonymi ścieżkami BPMN a ścieżkami przypadku użycia.

**Wynikowy współczynnik** to średnia arytmetyczna obu metryk:

$$C(A,B) = \frac{C_p(A,B) + C_n(A,B)}{2}$$

### 3. Raport

Narzędzie generuje raport w formacie Markdown zawierający metryki zgodności, listę brakujących wierzchołków i listę brakujących ścieżek.

## Przykład krok po kroku

Weźmy przypadek użycia z pięcioma krokami w scenariuszu głównym i dwoma scenariuszami alternatywnymi:

- **Scenariusz podstawowy:**
    1. A
    2. B
    3. C
    4. E
    5. F
- **Scenariusz alternatywny 1** (początek: krok 3, złączenie: krok 4):
    1. G
- **Scenariusz alternatywny 2** (początek: krok 3, złączenie: krok 4):
    1. D

Oraz odpowiadający mu proces biznesowy:

<img alt="Przykładowy proces biznesowy BPMN" src="/static/images/projects/uml-bpmn/sample_bpmn_2.png" width="800"/>

Po konwersji otrzymujemy dwa grafy:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Przykładowy diagram BPMN przed parsowaniem" src="/static/images/projects/uml-bpmn/A.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Graf skierowany utworzony na podstawie diagramu BPMN" src="/static/images/projects/uml-bpmn/B.png" style="width: 30%; min-width: 280px;"/>
</div>

#### Zgodność kroków

Szukamy wierzchołków wspólnych. Na grafie A kolorem czerwonym zaznaczony jest wierzchołek "G", który nie ma pokrycia w grafie B:

<img alt="Graf A z zaznaczonym brakującym wierzchołkiem" src="/static/images/projects/uml-bpmn/A_highlighted.png" width="400"/>

Na grafie B pomarańczowym kolorem zaznaczono wierzchołki wspólne z grafem A:

<img alt="Graf B z zaznaczonymi wspólnymi wierzchołkami" src="/static/images/projects/uml-bpmn/B_highlighted.png" width="400"/>

$$C_n(A,B) = \frac{|V_A \cap V_B|}{|V_A|} = \frac{6}{7}$$

#### Zgodność ścieżek

Algorytm znajduje wszystkie ścieżki w grafie B i zaznacza na nich wierzchołki wspólne z grafem A:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Przykładowy diagram BPMN przed parsowaniem" src="/static/images/projects/uml-bpmn/path1B.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Graf skierowany utworzony na podstawie diagramu BPMN" src="/static/images/projects/uml-bpmn/path2B.png" style="width: 30%; min-width: 280px;"/>
</div>


Po usunięciu nadmiarowych wierzchołków (niebieskich) porównujemy z trzema ścieżkami grafu A:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Przykładowy diagram BPMN przed parsowaniem" src="/static/images/projects/uml-bpmn/path1A.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Graf skierowany utworzony na podstawie diagramu BPMN" src="/static/images/projects/uml-bpmn/path2A.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Graf skierowany utworzony na podstawie diagramu BPMN" src="/static/images/projects/uml-bpmn/path3A.png" style="width: 30%; min-width: 280px;"/>
</div>

Dla ścieżki nr 3 (A → B → G → E → F) nie istnieje izomorficzna ścieżka w grafie B, bo wierzchołek "G" nie występuje w procesie biznesowym. Zatem:

$$C_p(A,B) = \frac{2}{3}$$

#### Wynik

$$C(A,B) = \frac{\frac{6}{7} + \frac{2}{3}}{2} \approx 0.76$$

Wygenerowany raport:

<img alt="Wygenerowany raport zgodności" src="/static/images/projects/uml-bpmn/raport.png" width="600"/>

Narzędzie poprawnie wskazało brakujący wierzchołek "G" oraz ścieżkę, której nie da się odtworzyć.

## Studium przypadku: system bankomatu

Aby zweryfikować praktyczną użyteczność narzędzia, zaprojektowałem kompletny system bankomatu z czterema funkcjami: autoryzacja użytkownika, wpłata gotówki, wypłata gotówki i sprawdzenie salda. Dla każdej funkcji stworzyłem przypadki użycia UML i odpowiadające im procesy biznesowe BPMN, a następnie celowo wprowadzałem niespójności, żeby sprawdzić, czy narzędzie je wykryje.

<img alt="Diagram przypadków użycia bankomatu" src="/static/images/projects/uml-bpmn/bakomat_use_case.png" width="600"/>

Bankomat wymaga autoryzacji przed każdą operacją, dlatego "Sprawdzenie PIN" jest osobnym przypadkiem użycia połączonym z pozostałymi relacją zawierania (`<<include>>`). Każdy przypadek użycia ma osobną definicję dla klienta i dla banku — wynika to z założenia, że jeden przypadek użycia jest porównywany z jednym procesem BPMN, który nie dzieli się na baseny.

Przeprowadziłem cztery scenariusze testowe.

### Pełna zgodność

Przypadek użycia "Sprawdzenie PIN" porównany z procesem biznesowym, który go w pełni realizuje — ale zawiera też nadmiarowe zadania i ścieżki (np. obsługę błędu odczytu karty i błędu nawiązywania połączenia).

- **Scenariusz podstawowy:** Sprawdzenie PIN
    1. Karta zostaje umieszczona w bankomacie
    2. Bankomat prosi o podanie PIN
    3. Bankomat wysyła zapytanie do banku, czy PIN poprawny
    4. Bank weryfikuje poprawność PIN
    5. Bank potwierdza poprawność PIN
    6. Bankomat informuje o autoryzacji zakończonej pomyślnie
- **Scenariusz alternatywny:** Zły PIN (początek: krok 5, złączenie: koniec)
    1. Bank informuje o błędnym PIN
    2. Bankomat pokazuje komunikat o niepoprawnym PIN
    3. Bankomat oddaje kartę

Proces biznesowy:

<img alt="Proces biznesowy sprawdzenia PIN" src="/static/images/projects/uml-bpmn/sprawdzenie_pin.png" width="800"/>

Narzędzie poprawnie rozpoznało 100% zgodność mimo nadmiarowych elementów w BPMN:

<img alt="Raport zgodności dla sprawdzenia PIN" src="/static/images/projects/uml-bpmn/raport_sprawdzenie_pin.png" width="400"/>

| Metryka | Wynik |
|---|---|
| Zgodność kroków | 100% |
| Zgodność ścieżek | 100% |
| **Wynikowy współczynnik** | **100%** |
| Wierzchołki (use case / BPMN / wspólne) | 9 / 17 / 9 |
| Ścieżki (use case / BPMN / wspólne) | 2 / 4 / 2 |

### Brak zgodności ścieżek

Przypadek użycia "Obsługa wypłaty" porównany z procesem BPMN, w którym jedno zadanie jest na niewłaściwym miejscu — przez co jedna ze ścieżek nie ma pokrycia.

- **Scenariusz podstawowy:** Obsługa wypłaty
    1. Bankomat wyświetla menu główne
    2. Klient wybiera opcję wypłaty gotówki
    3. Bankomat prosi o wprowadzenie kwoty
    4. Bankomat prosi bank o weryfikację dostępności środków
    5. Bank autoryzuje wypłatę
    6. Bank aktualizuje stan konta użytkownika
    7. Bankomat wydaje banknoty
    8. Bankomat drukuje potwierdzenie
    9. Bankomat oddaje kartę
- **Scenariusz alternatywny:** Brak środków (początek: krok 5, złączenie: krok 8)
    1. Bank odmawia autoryzacji wypłaty

Proces biznesowy:

<img alt="Proces biznesowy obsługi wypłaty z błędem w ścieżce" src="/static/images/projects/uml-bpmn/Obsluga_wyplaty.png" width="800"/>

| Metryka | Wynik |
|---|---|
| Zgodność kroków | 100% |
| Zgodność ścieżek | 50% |
| **Wynikowy współczynnik** | **75%** |
| Brakujące ścieżki | 1 |

Narzędzie wskazało dokładnie, którą ścieżkę (scenariusz alternatywny "Brak środków") nie da się odtworzyć w procesie biznesowym.

### Brak zgodności kroków

Przypadek użycia "Wypłata" porównany z procesem BPMN, w którym celowo pominięto zadanie "Klient odbiera gotówkę i potwierdzenie".

- **Scenariusz podstawowy:** Wypłata
    1. Klient wybiera opcję wypłaty
    2. Bankomat prosi o podanie kwoty
    3. Klient wprowadza kwotę
    4. Bankomat wysyła żądanie wypłaty do banku
    5. Bankomat odbiera pozytywną decyzję
    6. Bankomat drukuje potwierdzenie transakcji
    7. Klient odbiera gotówkę i potwierdzenie
    8. Bankomat zwraca kartę
    9. Klient odbiera kartę
- **Scenariusz alternatywny:** Brak środków (początek: krok 5, złączenie: krok 8)
    1. Bankomat odbiera negatywną decyzję
    2. Bankomat wyświetla komunikat o braku środków

Proces biznesowy:

<img alt="Proces biznesowy wypłaty z brakującym krokiem" src="/static/images/projects/uml-bpmn/Wyplata.png" width="800"/>

| Metryka | Wynik |
|---|---|
| Zgodność kroków | 91% |
| Zgodność ścieżek | 50% |
| **Wynikowy współczynnik** | **70%** |
| Brakujące wierzchołki | 1 |
| Brakujące ścieżki | 1 |

Brak jednego kroku pociągnął za sobą brak jednej ścieżki — scenariusz główny przechodzący przez ten krok nie mógł być odtworzony. Narzędzie poprawnie wskazało zarówno brakujący wierzchołek, jak i ścieżkę.

### Całkowity brak zgodności

Przypadek użycia "Sprawdzenie PIN" porównany z procesem BPMN odpowiadającym obsłudze wypłaty — czyli dwa zupełnie różne procesy. Jedynym wspólnym wierzchołkiem okazało się "Bankomat oddaje kartę" (występuje w obu).

| Metryka | Wynik |
|---|---|
| Zgodność kroków | 11% |
| Zgodność ścieżek | 0% |
| **Wynikowy współczynnik** | **6%** |
| Brakujące wierzchołki | 8 |
| Brakujące ścieżki | 2 |

### Wnioski z case study

We wszystkich czterech scenariuszach narzędzie poprawnie zidentyfikowało braki i wskazało konkretne brakujące elementy. Co ważne, radzi sobie zarówno z nadmiarowością w BPMN (pełna zgodność mimo dodatkowych zadań i ścieżek), jak i z wykrywaniem kaskadowych efektów — brak jednego kroku automatycznie powoduje brak ścieżki, która przez niego przechodzi.

## Stack technologiczny

- **Python 3** — implementacja algorytmów i parsowanie plików
- **ElementTree** — przetwarzanie plików XML (BPMN i XMI)
- **NetworkX** — reprezentacja i analiza struktur grafowych (przeszukiwanie ścieżek, izomorfizm)

## Ograniczenia

Narzędzie w obecnej wersji ma kilka uproszczeń:
- Obsługuje tylko podstawowe elementy BPMN (zdarzenie startowe/końcowe, bramka XOR, przepływ sekwencyjny)
- Procesy wejściowe nie mogą zawierać podziału na baseny i tory — nie rozróżnia też typów zadań
- Zgodność kroków opiera się na identyczności nazw (bez analizy semantycznej)
- Jeden przypadek użycia jest porównywany z jednym procesem biznesowym

Gdybym miał to rozwijać dalej, skupiłbym się na wsparciu pełnego zestawu symboli BPMN, analizie semantycznej nazw kroków (np. z użyciem embeddingów) oraz możliwości pracy z wieloma przypadkami użycia jednocześnie.

## Źródła

- [Repozytorium projektu](https://github.com/mpiotro4/bpmn_test_tool)
- [BPMN Specification](https://www.bpmn.org)
- [UML Specification](https://www.omg.org/spec/UML/2.5.1/PDF)
- [NetworkX — Python graph library](https://networkx.org)

## EN

## BPMN vs UML

In software development, business analysts model processes in BPMN while system architects define functional requirements through UML use cases. The catch is that these two models operate at different levels of abstraction — they can't be directly compared. Verifying by hand whether a business process actually delivers what a use case describes is tedious and error-prone.

A literature review revealed that while there have been attempts to convert between the two notations (Lubke et al. proposed visualizing use cases as BPMN processes; Bouzidi et al. explored the reverse direction), nobody has offered a tool for **consistency verification** between existing diagrams of both types.

I built a tool that automates this process: it transforms both diagram types into graph structures and compares them using a custom algorithm, producing a consistency report.

### Use Case vs. Use Case Diagram

These two things are easy to confuse, so it's worth clarifying. A **use case** is a textual description of an actor's interaction with a system — a sequence of steps organized into a main scenario and alternative scenarios. For an ATM, for example:

- **Main scenario:** cash withdrawal
    1. Customer inserts card into the ATM
    2. ATM displays the main menu
    3. Customer selects withdrawal
    4. ATM prompts for the amount
    5. ...
- **Alternative scenario:** Insufficient funds (starts at step 5, rejoins at step 8)
    1. Bank refuses authorization

A **use case diagram** is the graphical counterpart — ovals (use cases), actors, and relationships between them (association, `<<include>>`, `<<extend>>`). A single diagram may contain many use cases, but it doesn't describe steps — it's a map of system functionality, not a procedure.

This tool works with **use cases** (concrete steps and scenarios), not with use case diagrams.

## How It Works

The pipeline has three stages: converting diagrams to graphs, running the consistency algorithm, and generating the report.

### 1. Converting Diagrams to Graphs

Source BPMN (XML) and UML/XMI files are parsed and converted into directed graphs.

**BPMN → Graph:** Every event and task becomes a node; sequence flows become edges. Below is an example BPMN diagram and the resulting graph:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Sample BPMN diagram before parsing" src="/static/images/projects/uml-bpmn/simple_bpmn.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Directed graph built from the BPMN diagram" src="/static/images/projects/uml-bpmn/simple_graph.png" style="width: 30%; min-width: 280px;"/>
</div>

The information needed to reconstruct the graph lives inside the `bpmn:process` element in the XML. Each element has a unique `id` and `bpmn:incoming`/`bpmn:outgoing` children that hold flow identifiers — enough to rebuild the full structure.

**UML (use cases) → Graph:** Steps in the main scenario form the main path (nodes connected in sequence). Alternative scenarios are attached as branches — their start and end points connect back to the appropriate steps in the main scenario, as specified by `extension` elements with `guid` and `join` attributes in the XMI file.

<img alt="Graph built from a sample use case" src="/static/images/projects/uml-bpmn/use_case_graph_example.png" width="400"/>

### 2. Consistency Algorithm

Consistency is measured by two independent metrics.

**Step consistency** — does every step in the use case have a corresponding task in BPMN?

$$C_n(A,B) = \frac{|V_A \cap V_B|}{|V_A|} \cdot 100\%$$

where $V_A$ is the set of nodes in the use case graph and $V_B$ in the BPMN graph. A step and a task are considered matching if their names are identical. BPMN, being a more detailed description, may contain extra tasks — that's fine, as long as every use case step is covered.

**Path consistency** — does every path (scenario) in the use case also appear in the business process?

$$C_p(A,B) = \frac{|I|}{|A|} \cdot 100\%$$

The algorithm finds all paths in the BPMN graph (from start to end), removes nodes not present in the use case graph, and checks for isomorphism between the simplified BPMN paths and the use case paths.

**The final score** is the arithmetic mean of both metrics:

$$C(A,B) = \frac{C_p(A,B) + C_n(A,B)}{2}$$

### 3. Report

The tool generates a Markdown report containing the consistency metrics, a list of missing nodes, and a list of missing paths.

## Step-by-Step Example

Consider a use case with five steps in the main scenario and two alternative scenarios:

- **Main scenario:**
    1. A
    2. B
    3. C
    4. E
    5. F
- **Alternative scenario 1** (starts at step 3, rejoins at step 4):
    1. G
- **Alternative scenario 2** (starts at step 3, rejoins at step 4):
    1. D

And the corresponding business process:

<img alt="Sample BPMN business process" src="/static/images/projects/uml-bpmn/sample_bpmn_2.png" width="800"/>

After conversion we get two graphs:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Use case graph (A)" src="/static/images/projects/uml-bpmn/A.png" style="width: 30%; min-width: 280px;"/>
  <img alt="BPMN graph (B)" src="/static/images/projects/uml-bpmn/B.png" style="width: 30%; min-width: 280px;"/>
</div>

#### Step Consistency

We look for shared nodes. In graph A, node "G" is highlighted in red — it has no counterpart in graph B:

<img alt="Graph A with the missing node highlighted" src="/static/images/projects/uml-bpmn/A_highlighted.png" width="400"/>

In graph B, nodes shared with graph A are highlighted in orange:

<img alt="Graph B with shared nodes highlighted" src="/static/images/projects/uml-bpmn/B_highlighted.png" width="400"/>

$$C_n(A,B) = \frac{|V_A \cap V_B|}{|V_A|} = \frac{6}{7}$$

#### Path Consistency

The algorithm finds all paths in graph B and marks the nodes they share with graph A:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Path 1 in graph B" src="/static/images/projects/uml-bpmn/path1B.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Path 2 in graph B" src="/static/images/projects/uml-bpmn/path2B.png" style="width: 30%; min-width: 280px;"/>
</div>

After removing the extra nodes (shown in blue), we compare with the three paths in graph A:

<div style="display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap;">
  <img alt="Path 1 in graph A" src="/static/images/projects/uml-bpmn/path1A.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Path 2 in graph A" src="/static/images/projects/uml-bpmn/path2A.png" style="width: 30%; min-width: 280px;"/>
  <img alt="Path 3 in graph A" src="/static/images/projects/uml-bpmn/path3A.png" style="width: 30%; min-width: 280px;"/>
</div>

Path 3 (A → B → G → E → F) has no isomorphic counterpart in graph B, because node "G" doesn't exist in the business process. Therefore:

$$C_p(A,B) = \frac{2}{3}$$

#### Final Score

$$C(A,B) = \frac{\frac{6}{7} + \frac{2}{3}}{2} \approx 0.76$$

Generated report:

<img alt="Generated consistency report" src="/static/images/projects/uml-bpmn/raport.png" width="600"/>

The tool correctly identified the missing node "G" and the path that cannot be reproduced.

## Case Study: ATM System

To validate the tool's practical usefulness, I designed a complete ATM system with four functions: user authorization, cash deposit, cash withdrawal, and balance inquiry. For each function I created UML use cases and corresponding BPMN processes, then deliberately introduced inconsistencies to see whether the tool would catch them.

<img alt="ATM use case diagram" src="/static/images/projects/uml-bpmn/bakomat_use_case.png" width="600"/>

The ATM requires authorization before every operation, so "PIN Verification" is a separate use case linked to the others via an `<<include>>` relationship. Each use case has a separate definition for the customer and for the bank — this follows from the assumption that one use case is compared against one BPMN process, which doesn't split into pools.

I ran four test scenarios.

### Full Consistency

The "PIN Verification" use case compared against a business process that fully implements it — but also contains extra tasks and paths (e.g. handling a card read error and a connection failure).

- **Main scenario:** PIN Verification
    1. Card is inserted into the ATM
    2. ATM prompts for PIN
    3. ATM sends a PIN verification request to the bank
    4. Bank verifies the PIN
    5. Bank confirms the PIN is correct
    6. ATM notifies the customer of successful authorization
- **Alternative scenario:** Wrong PIN (starts at step 5, rejoins at end)
    1. Bank reports incorrect PIN
    2. ATM displays an incorrect PIN message
    3. ATM returns the card

Business process:

<img alt="PIN verification business process" src="/static/images/projects/uml-bpmn/sprawdzenie_pin.png" width="800"/>

The tool correctly recognized 100% consistency despite the extra elements in the BPMN:

<img alt="Consistency report for PIN verification" src="/static/images/projects/uml-bpmn/raport_sprawdzenie_pin.png" width="400"/>

| Metric | Result |
|---|---|
| Step consistency | 100% |
| Path consistency | 100% |
| **Final score** | **100%** |
| Nodes (use case / BPMN / shared) | 9 / 17 / 9 |
| Paths (use case / BPMN / shared) | 2 / 4 / 2 |

### Missing Path Consistency

The "Withdrawal Handling" use case compared against a BPMN process where one task is in the wrong place — causing one of the paths to have no coverage.

- **Main scenario:** Withdrawal Handling
    1. ATM displays the main menu
    2. Customer selects cash withdrawal
    3. ATM prompts for the amount
    4. ATM asks the bank to verify fund availability
    5. Bank authorizes the withdrawal
    6. Bank updates the customer's account balance
    7. ATM dispenses banknotes
    8. ATM prints a receipt
    9. ATM returns the card
- **Alternative scenario:** Insufficient funds (starts at step 5, rejoins at step 8)
    1. Bank refuses authorization

Business process:

<img alt="Withdrawal handling business process with a path error" src="/static/images/projects/uml-bpmn/Obsluga_wyplaty.png" width="800"/>

| Metric | Result |
|---|---|
| Step consistency | 100% |
| Path consistency | 50% |
| **Final score** | **75%** |
| Missing paths | 1 |

The tool pinpointed exactly which path (the "Insufficient funds" alternative scenario) cannot be reproduced in the business process.

### Missing Step Consistency

The "Withdrawal" use case compared against a BPMN process where the task "Customer collects cash and receipt" was deliberately omitted.

- **Main scenario:** Withdrawal
    1. Customer selects withdrawal
    2. ATM prompts for the amount
    3. Customer enters the amount
    4. ATM sends a withdrawal request to the bank
    5. ATM receives a positive decision
    6. ATM prints a transaction receipt
    7. Customer collects cash and receipt
    8. ATM returns the card
    9. Customer collects the card
- **Alternative scenario:** Insufficient funds (starts at step 5, rejoins at step 8)
    1. ATM receives a negative decision
    2. ATM displays an insufficient funds message

Business process:

<img alt="Withdrawal business process with a missing step" src="/static/images/projects/uml-bpmn/Wyplata.png" width="800"/>

| Metric | Result |
|---|---|
| Step consistency | 91% |
| Path consistency | 50% |
| **Final score** | **70%** |
| Missing nodes | 1 |
| Missing paths | 1 |

The absence of one step cascaded into a missing path — the main scenario passing through that step couldn't be reproduced. The tool correctly flagged both the missing node and the missing path.

### No Consistency

The "PIN Verification" use case compared against the BPMN process for withdrawal handling — two entirely different processes. The only shared node turned out to be "ATM returns the card" (which appears in both).

| Metric | Result |
|---|---|
| Step consistency | 11% |
| Path consistency | 0% |
| **Final score** | **6%** |
| Missing nodes | 8 |
| Missing paths | 2 |

### Case Study Conclusions

In all four scenarios the tool correctly identified gaps and pointed to the specific missing elements. Notably, it handles BPMN redundancy gracefully (full consistency despite extra tasks and paths) and detects cascade effects — a missing step automatically causes the path running through it to be flagged as missing too.

## Tech Stack

- **Python 3** — algorithm implementation and file parsing
- **ElementTree** — XML processing (BPMN and XMI)
- **NetworkX** — graph representation and analysis (path traversal, isomorphism)

## Limitations

The current version has a few simplifications: it only supports basic BPMN elements (start/end events, XOR gateways, sequence flows); input processes cannot use pools or swimlanes, and task types are not distinguished; step consistency relies on exact name matching with no semantic analysis; and one use case is compared against one business process at a time.

If I were to develop this further, I'd focus on full BPMN symbol support, semantic name matching (e.g. using embeddings), and the ability to handle multiple use cases simultaneously.

## References

- [Project repository](https://github.com/mpiotro4/bpmn_test_tool)
- [BPMN Specification](https://www.bpmn.org)
- [UML Specification](https://www.omg.org/spec/UML/2.5.1/PDF)
- [NetworkX — Python graph library](https://networkx.org)