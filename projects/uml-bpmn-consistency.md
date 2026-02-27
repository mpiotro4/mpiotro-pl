---
title_pl: "Narzędzie do weryfikacji zgodności między przypadkami użycia UML a procesami biznesowymi BPMN"
title_en: "UML Use Case and BPMN Business Process Consistency Verification Tool"
date: 2024-10
author: "Marcin Piotrowski"
tags: ["UML", "BPMN", "graph theory", "software engineering", "Python", "compliance testing"]
description_pl: "Narzędzie przekształcające diagramy UML i BPMN w struktury grafowe, a następnie weryfikujące ich zgodność za pomocą autorskiego algorytmu opartego na teorii grafów."
description_en: "A tool that transforms UML and BPMN diagrams into graph structures and verifies their consistency using a custom graph-based algorithm."
---

## PL

## UML vs BPMN

W procesie wytwarzania oprogramowania analitycy biznesowi modelują procesy w notacji BPMN, a architekci systemu definiują wymagania funkcjonalne za pomocą przypadków użycia UML. Problem polega na tym, że oba modele operują na różnych poziomach abstrakcji i nie da się ich ze sobą bezpośrednio porównać. Ręczna weryfikacja czy proces biznesowy faktycznie realizuje to, co opisuje przypadek użycia, jest czasochłonna i podatna na błędy.

Stworzyłem narzędzie, które automatyzuje ten proces — przekształca oba typy diagramów w struktury grafowe, a następnie porównuje je za pomocą autorskiego algorytmu, generując raport zgodności.

## Jak to działa?

Cały pipeline składa się z trzech etapów:

### 1. Konwersja diagramów na grafy

Pliki źródłowe BPMN (XML) oraz UML/XMI są parsowane i zamieniane na grafy skierowane:
- **BPMN** — każde zdarzenie i zadanie staje się wierzchołkiem, przepływy sekwencyjne stają się krawędziami
- **UML (przypadki użycia)** — kroki scenariusza podstawowego tworzą ścieżkę główną, scenariusze alternatywne są dołączane jako rozgałęzienia zgodnie z ich definicją (punkt początkowy i złączenie)

### 2. Algorytm zgodności

Zgodność jest mierzona dwoma niezależnymi metrykami:

**Zgodność kroków** — czy każdy krok z przypadku użycia ma swoje odzwierciedlenie jako zadanie w BPMN:

$$C_n(A,B) = \frac{|V_A \cap V_B|}{|V_A|} \cdot 100\%$$

**Zgodność ścieżek** — czy każda ścieżka (scenariusz) z przypadku użycia występuje również w procesie biznesowym:

$$C_p(A,B) = \frac{|I|}{|A|} \cdot 100\%$$

Wynikowy współczynnik to średnia arytmetyczna obu metryk. Algorytm dopuszcza nadmiarowe zadania w BPMN (wynikające z większego stopnia szczegółowości) — ważne jest, żeby kluczowe kroki były obecne i we właściwej kolejności.

### 3. Raport

Narzędzie generuje raport w formacie Markdown zawierający:
- Metryki zgodności (kroków, ścieżek, sumaryczna)
- Listę brakujących wierzchołków (kroków nieodzwierciedlonych w BPMN)
- Listę brakujących ścieżek (scenariuszy, których nie da się odtworzyć w procesie biznesowym)

## Przykład

Dla przypadku użycia z 7 krokami (scenariusz główny + 2 alternatywne) i procesu biznesowego z 11 zadaniami narzędzie wykryło:
- 1 brakujący krok (wierzchołek "G" nieobecny w BPMN)
- 1 brakującą ścieżkę (scenariusz alternatywny niemożliwy do odtworzenia)
- Wynikowy współczynnik zgodności: **76%**

## Studium przypadku: system bankomatu

Aby zweryfikować praktyczną użyteczność, przetestowałem narzędzie na systemie bankomatu z czterema funkcjami: autoryzacja użytkownika, wpłata, wypłata i sprawdzenie salda.

Przeprowadzono cztery scenariusze testowe:

| Scenariusz | Kroków | Ścieżek | Wynik |
|---|---|---|---|
| Pełna zgodność | 100% | 100% | **100%** |
| Brak zgodności ścieżek | 100% | 50% | **75%** |
| Brak zgodności kroków | 91% | 50% | **70%** |
| Całkowity brak zgodności | 11% | 0% | **6%** |

We wszystkich przypadkach narzędzie poprawnie zidentyfikowało braki i wskazało konkretne brakujące elementy.

## Stack technologiczny

- **Python 3** — implementacja algorytmów i parsowanie plików
- **ElementTree** — przetwarzanie plików XML (BPMN i XMI)
- **NetworkX** — reprezentacja i analiza struktur grafowych

## Ograniczenia

Narzędzie w obecnej wersji ma kilka uproszczeń:
- Obsługuje tylko podstawowe elementy BPMN (zdarzenie startowe/końcowe, bramka XOR, przepływ sekwencyjny)
- Procesy wejściowe nie mogą zawierać podziału na baseny i tory
- Zgodność kroków opiera się na identyczności nazw
- Jeden przypadek użycia jest porównywany z jednym procesem biznesowym

## Źródła

- [Repozytorium projektu](TODO_LINK)
- [BPMN Specification](https://www.bpmn.org)
- [UML Specification](https://www.omg.org/spec/UML/2.5.1/PDF)