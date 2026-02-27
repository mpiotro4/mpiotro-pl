---
title_pl: "Embeddingi i Similarity — jak maszyny rozumieją podobieństwo tekstu"
title_en: "Embeddings and Similarity — How Machines Understand Text Similarity"
date: 2026-02-26
author: "Marcin Piotrowski"
tags: ["NLP", "embeddings", "cosine similarity", "sentence-transformers", "Word2Vec"]
description_pl: "Od Word2Vec do sentence-transformers — czym są embeddingi, jak działa cosine similarity i dlaczego podobieństwo semantyczne to nie to samo co dopasowanie słów kluczowych."
description_en: "From Word2Vec to sentence-transformers — what embeddings are, how cosine similarity works, and why semantic similarity is not the same as keyword matching."
---

## PL

## Wstęp

[Krótkie intro: czemu to ważne, gdzie się to stosuje (search, RAG, rekomendacje). Nawiązanie do poprzedniego wpisu o attention — embeddingi tam były, ale potraktowane skrótowo. Teraz rozwijamy.]

## Co to embedding?

[Intuicja: słowo/zdanie jako punkt w przestrzeni wielowymiarowej. Podobne znaczenie = bliskie punkty.]

### Przykład 2D

[Prosty przykład jak w wpisie o attention — kilka słów, 2 wymiary, wizualna interpretacja. Np. "kot", "pies", "samochód", "rower" — pokazać że zwierzęta lądują blisko siebie.]

> **Uwaga:** W prawdziwych modelach wymiarów jest 384-4096, nie 2. Redukcja do 2D to uproszczenie dla wizualizacji.

## Skąd się biorą embeddingi?

### Word2Vec (kontekst historyczny)

[Krótko: idea "powiedz mi z jakimi słowami występujesz, a powiem ci kim jesteś". Skip-gram/CBOW — jedno zdanie wystarczy, bez wchodzenia w szczegóły treningu. Słynny przykład: król - mężczyzna + kobieta ≈ królowa.]

### Od słów do zdań — Sentence Transformers

[Problem: embedding słowa ≠ embedding zdania. Uśrednianie wektorów słów gubi kolejność i kontekst ("pies goni kota" vs "kot goni psa" → ten sam średni wektor). Sentence-transformers (SBERT) rozwiązują to używając architektury Transformer do generowania embeddingu całego zdania.]

## Cosine Similarity

### Intuicja geometryczna

[Kąt między wektorami. Kąt mały = podobne, kąt duży = różne. Długość wektora nie ma znaczenia.]

### Wzór

$$\text{cosine\_similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$

[Rozpisać na przykładzie numerycznym krok po kroku — iloczyn skalarny, normy, wynik. Styl jak w wpisie o attention.]

### Interpretacja wartości

[Tabela/opis: 1.0 = identyczne, 0 = ortogonalne (brak związku), -1 = przeciwne. W praktyce embeddingi tekstowe rzadko dają wartości ujemne.]

### A inne metryki?

[Krótka wzmianka: dot product — to samo co cosine dla znormalizowanych wektorów (a sentence-transformers normalizują). Euclidean distance — też daje ten sam ranking. W praktyce cosine to standard, reszta to ciekawostka.]

## Praktyczny przykład: similarity między zdaniami

### Dane

[Kilka zdań o różnym stopniu podobieństwa, np.:
- "Kot śpi na kanapie"
- "Rudy kocur drzemie na sofie"
- "Pies bawi się w ogrodzie"
- "Giełda zamknęła się na plusie"
]

### Embeddingi

[Wektory (uproszczone do 2-3D) + krótki komentarz że w rzeczywistości sentence-transformers daje 384/768 wymiarów.]

### Macierz similarity

[Macierz cosine similarity między wszystkimi parami — przykład numeryczny. Pokazać że zdania 1 i 2 mają wysoki score mimo zupełnie innych słów → to jest siła embeddingów vs keyword search.]

### Mini-heatmapa

[Wizualizacja macierzy jako heatmapa — kolorami. Nawiązanie: "ten sam mechanizm można zastosować do szukania fragmentów w dużym dokumencie — ale o tym w kolejnym wpisie."]

## Gdzie similarity zawodzi?

[Uczciwa sekcja o ograniczeniach:]

### Negacja

["Lubię koty" vs "Nie lubię kotów" — wysoki similarity mimo przeciwnego znaczenia. Embeddingi słabo łapią negację.]

### Kontekst i wieloznaczność

["Zamek na drzwiach" vs "Zamek na wzgórzu" — ten sam token, różne znaczenia. Sentence embeddingi radzą sobie lepiej niż word embeddingi, ale nie idealnie.]

### Krótkie vs długie teksty

[Embedding całego akapitu vs embedding jednego słowa — porównanie nie zawsze ma sens, bo "gęstość informacji" jest inna.]

## Podsumowanie

[Kluczowe takeaways:
1. Embeddingi to numeryczna reprezentacja znaczenia
2. Cosine similarity mierzy podobieństwo kierunku, nie długości
3. Sentence embeddingi > word embeddingi do porównywania zdań
4. Similarity to potężne narzędzie, ale ma ograniczenia (negacja, wieloznaczność)
]

## Przydatne linki

- [Sentence-Transformers (dokumentacja)](https://www.sbert.net/)
- [Word2Vec (oryginalny artykuł)](https://arxiv.org/abs/1301.3781)
- [The Illustrated Word2Vec](https://jalammar.github.io/illustrated-word2vec/)
- [Poprzedni wpis: Mechanizm Attention krok po kroku](#)

## EN