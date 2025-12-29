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

## Introduction

The attention mechanism is at the heart of the Transformer architecture and the foundation of all modern Large Language Models (LLMs). While the theory behind attention might seem abstract, the best way to understand it is to walk through a concrete computational example step by step.

In this post, we'll work through a complete computational example of the attention mechanism on a simple sentence, showing all matrices and numerical calculations.

## Example: "cat chases mouse"

Let's consider a simple sentence with three words (tokens):

**Vocabulary (vocabulary size = 3):**
- token 0: "cat"
- token 1: "chases"
- token 2: "mouse"

### Step 1: Token Embeddings

We represent each token as an embedding vector of length $d = 2$ (in real models, this is typically 512, 768, or more).

**Embeddings:**

$$E = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

where:
- $E[0] = [1.0, 0.0]$ - embedding for "cat"
- $E[1] = [0.2, 1.0]$ - embedding for "chases"
- $E[2] = [0.8, 0.0]$ - embedding for "mouse"

In practice, embeddings are learned during model training so that words with similar meanings have similar representations.

### Step 2: Weight Matrices - Query, Key, Value

Next, we define three weight matrices that transform embeddings into Query, Key, and Value representations:

**Query weight matrix:**

$$W_Q = \begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}$$

**Key weight matrix:**

$$W_K = \begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}$$

**Value weight matrix:**

$$W_V = \begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}$$

In this simple example, we use identity matrices, but in real models, these are learned parameters.

### Step 3: Computing Q, K, V

We multiply embeddings by the respective weight matrices:

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

### Step 4: Attention Scores

Now we calculate attention scores using the formula:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

where $d_k = 2$ (dimension of the key).

**Computing $QK^T$:**

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

**Scaling by $\sqrt{d_k} = \sqrt{2} \approx 1.414$:**

$$\frac{QK^T}{\sqrt{2}} = \begin{bmatrix}
0.71 & 0.14 & 0.57 \\
0.14 & 0.74 & 0.11 \\
0.57 & 0.11 & 0.45
\end{bmatrix}$$

### Step 5: Softmax

We apply the softmax function to each row:

$$\text{Attention Weights} = \text{softmax}\left(\frac{QK^T}{\sqrt{2}}\right) = \begin{bmatrix}
0.35 & 0.25 & 0.35 \\
0.24 & 0.25 & 0.35 \\
0.37 & 0.25 & 0.37
\end{bmatrix}$$

Each row shows how much a given token "attends to" all tokens in the sequence:
- Row 0 (cat): attends mainly to itself (0.35) and "mouse" (0.35)
- Row 1 (chases): distributes attention evenly
- Row 2 (mouse): attends mainly to "cat" (0.37) and itself (0.37)

### Step 6: Output Weights (Final Output)

The last step is to multiply attention weights by the Value matrix:

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

Detailed values (approximate):
- For token 0 (cat): $[0.35 \times 1.0 + 0.25 \times 0.2 + 0.35 \times 0.8, 0.35 \times 0.0 + 0.25 \times 1.0 + 0.35 \times 0.0] \approx [0.68, 0.25]$
- For token 1 (chases): $[0.66, 0.25]$
- For token 2 (mouse): $[0.71, 0.25]$

The final output matrix contains new representations for each token that incorporate context from other tokens in the sequence.

## Why Does This Work?

The attention mechanism allows each token to "look at" all other tokens and decide which ones are most important for its representation. In our example:

1. **"cat"** attends to "mouse" - the model learns the relationship between subject and object
2. **"chases"** as a verb connects both sides evenly
3. **"mouse"** attends to "cat" - again, the subject-object relationship

This allows the model to understand the structure and semantics of the sentence without the need to define grammatical rules.

## Key Properties

### Scaling by $\sqrt{d_k}$

Dividing by $\sqrt{d_k}$ prevents dot products from growing too large as dimensionality increases. Without this scaling, softmax could produce very extreme values (close to 0 or 1), making learning difficult.

### Softmax

The softmax function normalizes results so that the sum of attention weights for each token equals 1.0. Additionally, it amplifies differences between values - larger values become even larger after softmax.

### Q, K, V Matrices

Separating into Query, Key, and Value gives the model flexibility:
- **Query**: "what am I looking for?"
- **Key**: "what do I offer?"
- **Value**: "what do I return?"

A token can search for certain features (Q), be searched by others (K), and pass on yet other information (V).

## Multi-Head Attention

In practice, modern Transformers use **multi-head attention**, where the attention process is performed in parallel with different weight matrices, and the results are concatenated. This allows the model to learn different types of relationships simultaneously.

## Summary

The attention mechanism is a mathematically elegant way to model dependencies between elements in a sequence. The key steps are:

1. **Embeddings** - representing tokens as vectors
2. **Q, K, V transformations** - projections into different spaces
3. **Attention scores** - computing $QK^T/\sqrt{d_k}$
4. **Softmax** - normalization to probabilities
5. **Weighted sum of Value** - final output

This mechanism, repeated many times across many layers and heads, creates the powerful Transformer architecture that is revolutionizing natural language processing.

## Useful Links

- [Attention is All You Need (original paper)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Visualizing Attention in Transformer Models](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)
