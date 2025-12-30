---
title_pl: "Mechanizm Attention krok po kroku - przykład obliczeniowy"
title_en: "Attention Mechanism Step by Step - A Computational Example"
date: 2025-12-29
author: "Marcin Piotrowski"
tags: ["NLP", "transformers", "attention", "deep learning", "LLM"]
description_pl: "Szczegółowy przykład obliczeniowy mechanizmu attention z artykułu 'Attention is All You Need'. Krok po kroku przez embeddingi, macierze Q, K, V aż po finalne wagi attention."
description_en: "Detailed computational example of the attention mechanism from 'Attention is All You Need'. Step by step through embeddings, Q, K, V matrices to final attention weights."
---

## PL

## Wstęp

Mechanizm attention jest sercem architektury Transformer i podstawą działania wszystkich nowoczesnych dużych modeli językowych (LLM). Chociaż teoria stojąca za attention może wydawać się abstrakcyjna, najlepszym sposobem na jej zrozumienie jest przejście przez konkretny przykład obliczeniowy krok po kroku.

W tym wpisie przeprowadzimy kompletny przykład obliczeniowy mechanizmu attention na prostym zdaniu, pokazując wszystkie macierze i obliczenia numeryczne.

## Przykład: "cat chases mouse"

Rozważmy proste zdanie składające się z trzech słów (tokenów):

**Słownik (vocabulary size = 3):**
- token 0: "cat"
- token 1: "chases"
- token 2: "mouse"

### Krok 1: Embeddingi tokenów

Każdy token reprezentujemy jako wektor embeddingów o długości $d = 2$ (w rzeczywistych modelach to zazwyczaj 512, 768 lub więcej).

**Embeddingi:**

$$E = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

gdzie:
- $E[0] = [1.0, 0.0]$ - embedding dla "cat"
- $E[1] = [0.2, 1.0]$ - embedding dla "chases"
- $E[2] = [0.8, 0.0]$ - embedding dla "mouse"

W rzeczywistości embeddingi są uczone podczas treningu modelu tak, aby słowa o podobnym znaczeniu miały podobne reprezentacje.

### Krok 2: Macierze wag - Query, Key, Value

Następnie definiujemy trzy macierze wag, które transformują embeddingi na reprezentacje Query, Key i Value:

**Macierz wag Query:**

$$W_Q = \begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}$$

**Macierz wag Key:**

$$W_K = \begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}$$

**Macierz wag Value:**

$$W_V = \begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}$$

W tym prostym przykładzie używamy macierzy jednostkowych, ale w prawdziwych modelach są to wyuczone parametry.

### Krok 3: Obliczenie Q, K, V

Mnożymy embeddingi przez odpowiednie macierze wag:

**Query:**

$$Q = E \cdot W_Q = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

**Key:**

$$K = E \cdot W_K = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

**Value:**

$$V = E \cdot W_V = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

### Krok 4: Attention Scores

Teraz obliczamy attention scores używając wzoru:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

gdzie $d_k = 2$ (wymiar klucza).

**Obliczenie $QK^T$:**

$$QK^T = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix} \cdot \begin{bmatrix}
1.0 & 0.2 & 0.8 \\
0.0 & 1.0 & 0.0
\end{bmatrix} = \begin{bmatrix}
1.0 & 0.2 & 0.8 \\
0.2 & 1.04 & 0.16 \\
0.8 & 0.16 & 0.64
\end{bmatrix}$$

**Skalowanie przez $\sqrt{d_k} = \sqrt{2} \approx 1.414$:**

$$\frac{QK^T}{\sqrt{2}} = \begin{bmatrix}
0.71 & 0.14 & 0.57 \\
0.14 & 0.74 & 0.11 \\
0.57 & 0.11 & 0.45
\end{bmatrix}$$

### Krok 5: Softmax

Aplikujemy funkcję softmax do każdego wiersza:

$$\text{Attention Weights} = \text{softmax}\left(\frac{QK^T}{\sqrt{2}}\right) = \begin{bmatrix}
0.35 & 0.25 & 0.35 \\
0.24 & 0.25 & 0.35 \\
0.37 & 0.25 & 0.37
\end{bmatrix}$$

Każdy wiersz pokazuje, jak bardzo dany token "zwraca uwagę" (attends) na wszystkie tokeny w sekwencji:
- Wiersz 0 (cat): zwraca uwagę głównie na siebie (0.35) i "mouse" (0.35)
- Wiersz 1 (chases): rozkłada uwagę równomiernie
- Wiersz 2 (mouse): zwraca uwagę głównie na "cat" (0.37) i siebie (0.37)

### Krok 6: Output weights (finalne wyjście)

Ostatnim krokiem jest pomnożenie wag attention przez macierz Value:

$$\text{Output} = \text{Attention Weights} \times V$$

$$\text{Output} = \begin{bmatrix}
0.35 & 0.25 & 0.35 \\
0.24 & 0.25 & 0.35 \\
0.37 & 0.25 & 0.37
\end{bmatrix} \times \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

Wartości szczegółowe (przybliżone):
- Dla tokenu 0 (cat): $[0.35 \times 1.0 + 0.25 \times 0.2 + 0.35 \times 0.8, 0.35 \times 0.0 + 0.25 \times 1.0 + 0.35 \times 0.0] \approx [0.68, 0.25]$
- Dla tokenu 1 (chases): $[0.66, 0.25]$
- Dla tokenu 2 (mouse): $[0.71, 0.25]$

Ostateczna macierz wyjściowa zawiera nowe reprezentacje dla każdego tokenu, które uwzględniają kontekst z innych tokenów w sekwencji.

## Dlaczego to działa?

Mechanizm attention pozwala każdemu tokenowi "spojrzeć" na wszystkie inne tokeny i zadecydować, które z nich są najważniejsze dla jego reprezentacji. W naszym przykładzie:

1. **"cat"** zwraca uwagę na "mouse" - model uczy się relacji między podmiotem a dopełnieniem
2. **"chases"** jako czasownik łączy obie strony równomiernie
3. **"mouse"** zwraca uwagę na "cat" - ponownie relacja podmiot-dopełnienie

To pozwala modelowi rozumieć strukturę i semantykę zdania bez konieczności definiowania reguł gramatycznych.

## Kluczowe właściwości

### Skalowanie przez $\sqrt{d_k}$

Dzielenie przez $\sqrt{d_k}$ zapobiega temu, aby iloczyny skalarne nie rosły zbyt mocno wraz z wzrostem wymiarowości. Bez tego skalowania softmax mógłby dawać bardzo ekstremalne wartości (bliskie 0 lub 1), co utrudniłoby uczenie.

### Softmax

Funkcja softmax normalizuje wyniki tak, aby suma wag attention dla każdego tokenu wynosiła 1.0. Dodatkowo potęguje różnice między wartościami - większe wartości stają się jeszcze większe po softmax.

### Macierze Q, K, V

Rozdzielenie na Query, Key i Value daje modelowi elastyczność:
- **Query**: "czego szukam?"
- **Key**: "co oferuję?"
- **Value**: "co zwracam?"

Token może szukać jednych cech (Q), być wyszukiwany po innych (K), i przekazywać jeszcze inne informacje (V).

## Multi-Head Attention

W praktyce nowoczesne Transformery używają **multi-head attention**, gdzie proces attention jest wykonywany równolegle z różnymi macierzami wag, a wyniki są konkatenowane. To pozwala modelowi uczyć się różnych typów relacji równocześnie.

## Podsumowanie

Mechanizm attention to matematycznie elegancki sposób na modelowanie zależności między elementami sekwencji. Kluczowe kroki to:

1. **Embeddingi** - reprezentacja tokenów jako wektorów
2. **Transformacje Q, K, V** - projekcje do różnych przestrzeni
3. **Attention scores** - obliczenie $QK^T/\sqrt{d_k}$
4. **Softmax** - normalizacja do prawdopodobieństw
5. **Ważona suma Value** - finalne wyjście

Ten mechanizm, powtórzony wiele razy w wielu warstwach i głowicach, tworzy potężną architekturę Transformer, która rewolucjonizuje przetwarzanie języka naturalnego.

## Przydatne linki

- [Attention is All You Need (oryginalny artykuł)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Visualizing Attention in Transformer Models](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)

---

## EN