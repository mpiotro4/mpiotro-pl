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

> **Uwaga:** Dla przejrzystości pomijamy w tym przykładzie positional encoding oraz końcową projekcję wyjściową $W_O$. W rzeczywistych Transformerach oba te elementy są niezbędne – positional encoding koduje kolejność tokenów, a $W_O$ projektuje sklejone wyjścia z wielu głowic do przestrzeni modelu.

## Przykład: "cat chases mouse"

Rozważmy proste zdanie składające się z trzech słów (tokenów): `cat chases mouse`
I następujący słownik o rozmiarze 5:
- token 0: "cat"
- token 1: "chases"
- token 2: "mouse"
- token 3: "quickly"
- token 4: "sleeping"

### Krok 1: Embeddingi tokenów

Każdy token reprezentujemy jako wektor embeddingów o wymiarze $d_{model} = 2$ (w rzeczywistych modelach to zazwyczaj 512, 768 lub więcej).

Każdy z tokenów posiada następujące embeddingi:

$$W_{vocab} = \begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}$$

gdzie kolumny odpowiadają kolejnym tokenom ze słownika.

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

#### Interpretacja wymiarów:
Choć nie kontrolujemy bezpośrednio, co oznacza każdy wymiar, możemy próbować to odkryć post hoc. W sieci można znaleźć wiele przykładów, gdzie np. embeddingi tokenów `wujek` i `ciocia` są przesunięte o pewną stałą wartość tak samo jak tokeny `król` i `królowa`. Oznacza to, że model zakodował informację o płci w konkretnym kierunku przestrzeni.
W naszym przykładzie można spekulować:
- Pierwszy wymiar — "zwierzęcość" (cat=1.0, mouse=0.8, chases=0.2)
- Drugi wymiar — "akcja/ruch" (chases=1.0, reszta=0.0)
Aczkolwiek to tylko przykład zrobiony pod tezę, w prawdziwych modelach o setkach wymiarów interpretacja jest znacznie trudniejsza i rzadko jednoznaczna.
### Krok 2: Macierze wag — Query, Key, Value

Następnie definiujemy trzy macierze wag, które transformują embeddingi na reprezentacje Query, Key i Value.
W standardowej notacji wymiar klucza i wartości oznaczamy jako $d_k$ i $d_v$. Przy pojedynczej głowicy (single-head attention) mamy $d_k = d_v = d_{model}$. W multi-head attention każda głowica operuje na $d_k = d_v = d_{model} / h$, gdzie $h$ to liczba głowic.

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

### Krok 5: Maskowanie i Softmax

W architekturze **decoder-only** (np. GPT, Claude) stosujemy maskę przyczynową (causal mask), która sprawia, że tokeny nie widzą tokenów z **przyszłości** — mogą patrzeć tylko na siebie i na wcześniejsze pozycje. Dzięki temu model może być używany do autoregresyjnej generacji tekstu.
Dla porównania, architektura **encoder-only** (np. BERT) nie stosuje maski — każdy token widzi całą sekwencję (bidirectional attention).

**Po maskowaniu (przed softmax):**

$$\frac{QK^T}{\sqrt{2}} + \text{Mask} = \begin{bmatrix}
0.71 & -\infty & -\infty \\
0.14 & 0.74 & -\infty \\
0.57 & 0.11 & 0.45
\end{bmatrix} +
\begin{bmatrix}
0 & -\infty & -\infty \\
0 & 0 & -\infty \\
0 & 0 & 0
\end{bmatrix} = \begin{bmatrix}
0.71 & -\infty & -\infty \\
0.14 & 0.74 & -\infty \\
0.57 & 0.11 & 0.45
\end{bmatrix}
$$

> **Uwaga:** Zapis $a + (-\infty)$ jest matematycznie nieformalny, ale stanowi standardową konwencję w programowaniu. W arytmetyce zmiennoprzecinkowej `-inf` to konkretna wartość, dla której $\exp(-\infty) = 0$, co skutecznie zeruje zamaskowane pozycje po softmax.

Aplikujemy funkcję softmax do każdego wiersza (wartości $-\infty$ dają 0 po softmax):

$$\text{Attention Weights} = \text{softmax}\left(\frac{QK^T}{\sqrt{2}} + \text{Mask}\right) = \begin{bmatrix}
1.0 & 0.0 & 0.0 \\
0.35 & 0.65 & 0.0 \\
0.40 & 0.25 & 0.35
\end{bmatrix}$$

Każdy wiersz pokazuje, jak bardzo dany token "zwraca uwagę" (attends) na dostępne tokeny:
- **Wiersz 0 (cat):** widzi tylko siebie (jedyny dostępny token), więc waga = 1.0
- **Wiersz 1 (chases):** widzi "cat" i siebie; większa uwaga na siebie (0.65) niż na "cat" (0.35)
- **Wiersz 2 (mouse):** widzi wszystkie trzy tokeny; największa uwaga na "cat" (0.40), następnie na siebie (0.35), najmniejsza na "chases" (0.25)

### Krok 6: Output (reprezentacje kontekstowe)

Ostatnim krokiem jest pomnożenie wag attention przez macierz Value:

$$\text{Attention Out} = \text{Attention Weights} \cdot V$$

$$\text{Attention Out} = 
\begin{bmatrix}
1.0 & 0.0 & 0.0 \\
0.35 & 0.65 & 0.0 \\
0.40 & 0.25 & 0.35
\end{bmatrix}
\begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}
=
\begin{bmatrix}
1.0 & 0.0 \\
0.48 & 0.65 \\
0.73 & 0.25
\end{bmatrix}
$$

Ostateczna macierz wyjściowa zawiera **kontekstowe reprezentacje** (contextualized representations) dla każdego tokenu — każdy wektor jest ważoną kombinacją wektorów Value, gdzie wagi zależą od attention scores.

**Co się zmieniło?**

- **"cat"** — pozostał bez zmian $[1.0, 0.0]$, bo przez maskowanie widzi tylko siebie
- **"chases"** — zmiana z $[0.2, 1.0]$ na $[0.48, 0.65]$: wzrosła "zwierzęcość" (wpływ "cat"), spadła "akcja"
- **"mouse"** — zmiana z $[0.8, 0.0]$ na $[0.73, 0.25]$: pojawiła się składowa "akcji" (wpływ "chases")

Każdy token wchłonął informację o swoim kontekście. "Mouse" wie teraz, że jest goniona – informacja zakodowana w wymiarze "akcji" będzie kluczowa przy predykcji następnego tokenu.

To uproszczony przykład, ale dokładnie ten sam mechanizm agregacji kontekstu przez ważone sumy zachodzi w powszechnie używanych modelach.

> **Uwaga:** W pełnej architekturze Transformer wyjście jest następnie mnożone przez macierz projekcji $W_O \in \mathbb{R}^{d_v \times d_{model}}$, co tutaj pomijamy.

### Krok 7: Feed-Forward Network (FFN)
Po bloku attention następuje sieć feed-forward (FFN), stosowana niezależnie do każdej pozycji. W oryginalnej architekturze Transformera ([Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)) składa się z dwóch warstw liniowych z aktywacją ReLU:

$$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

Dla uproszczenia użyjemy minimalnego FFN z jedną warstwą liniową, bez aktywacji i bez biasu:

$$\text{FFN}(x) = xW_{FFN}$$

$$W_{FFN} = \begin{bmatrix}
0.5 & 1.0 \\
1.0 & 0.5
\end{bmatrix}$$

$$\text{FFN Out} = \text{Output} \cdot W_{FFN} =
\begin{bmatrix}
1.0 & 0.0 \\
0.48 & 0.65 \\
0.73 & 0.25
\end{bmatrix}
\begin{bmatrix}
0.5 & 1.0 \\
1.0 & 0.5
\end{bmatrix}
=
\begin{bmatrix}
0.50 & 1.00 \\
0.89 & 0.81 \\
0.62 & 0.86
\end{bmatrix}
$$

> **Uwaga:** Pomijamy tu LayerNorm i residual connections, które w prawdziwym Transformerze stabilizują uczenie.

### Krok 8: Predykcja następnego tokenu

Aby przewidzieć następny token, potrzebna jest reprezentacja ostatniego tokenu:

$$\text{h_mouse} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix} $$

Warto zauważyć, że na tym etapie wszystkie pozostałe tokeny nie są nam potrzebne. Po etapie attention wszystkie informacje, które niosą, powinny być już zawarte w ostatnim tokenie.

#### Predykcja na logity (unembedding)

$$\text{logits}=\text{h_mouse}\cdot\text{W_vocab}= \begin{bmatrix} 0.62 & 0.86 \end{bmatrix} 
\begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}=
\begin{bmatrix}
0.62 & 0.984 & 0.496 & 0.43 & 0.0
\end{bmatrix}
$$

Mając logity możemy obliczyć prawdopodobieństwa:

$$ P = softmax(logits) = softmax(\begin{bmatrix}0.62 & 0.984 & 0.496 & 0.43 & 0.0\end{bmatrix})=\begin{bmatrix} 0.21 & 0.30 & 0.19 & 0.18 & 0.11 \end{bmatrix} $$

**Wyniki:**

| Token | Prawdopodobieństwo |
|-------|--------------------|
| cat | 21%                |
| chases | 30%                |
| mouse | 19%                |
| quickly | 18%                |
| sleeping | 11%                |

Wychodzi na to, że wg. naszego prostego modelu kolejny najbardziej prawdopodobny token to "chases", czyli zdanie brzmi:

    Cat chases mouse chases

Co jest totalnie bez sensu? 

## Dlaczego to (nie) działa?

Bo wagi zostały dobrane nie na drodze treningu, lecz arbitralnie. Początkowo chciałem dobrać wagi tak, aby uzyskać sensowny wynik, po czym stwierdziłem, że większą wartość będzie miało, jeśli znowu przypomnę, że w prawdziwych modelach tych wag są miliony, więc ten prosty przykład nie ma prawa działać poprawnie (tak naprawdę w pierwszej kolejności było to motywowane lenistwem, dopiero potem dorobiłem tę opowieść o większej wartości edukacyjnej).

Gdy jednak uwierzymy, że to wszystko działa, to warto wspomnieć, że jest to zasługa mechanizmu attention, który pozwala każdemu tokenowi "spojrzeć" na dostępne tokeny i zadecydować, które z nich są najważniejsze dla jego reprezentacji. 

W architekturze **decoder-only** z maską przyczynową (jak w naszym przykładzie):
- Każdy token buduje swoją reprezentację tylko na podstawie siebie i poprzednich tokenów
- "mouse" może uwzględnić kontekst z "cat" i "chases", ale nie odwrotnie
- To umożliwia autoregresyjną generację: model przewiduje następny token znając tylko poprzednie

W architekturze **encoder-only** (bez maski):
- Każdy token widzi całą sekwencję
- "cat" może zwracać uwagę na "mouse" i odwrotnie
- Model uczy się dwukierunkowych relacji między tokenami

Ta elastyczność pozwala Transformerom rozumieć strukturę i semantykę tekstu bez konieczności definiowania reguł gramatycznych.

## Kluczowe właściwości

### Skalowanie przez $\sqrt{d_k}$

Dzielenie przez $\sqrt{d_k}$ zapobiega temu, aby iloczyny skalarne nie rosły zbyt mocno wraz z wzrostem wymiarowości. Bez tego skalowania softmax mógłby dawać bardzo ekstremalne wartości (bliskie 0 lub 1), co utrudniłoby uczenie poprzez znikające gradienty.

### Softmax

Funkcja softmax normalizuje wyniki tak, aby suma wag attention dla każdego tokenu wynosiła 1.0. Dodatkowo wyostrza różnice między wartościami — większe wartości stają się jeszcze bardziej dominujące po softmax.

### Macierze Q, K, V

Rozdzielenie na Query, Key i Value daje modelowi elastyczność:
- **Query**: "czego szukam?"
- **Key**: "co oferuję jako klucz do dopasowania?"
- **Value**: "jaką informację przekazuję?"

Token może szukać określonych cech (Q), być wyszukiwany po innych cechach (K) i przekazywać jeszcze inne informacje (V). Ta separacja pozwala na asymetryczne relacje między tokenami.

## Multi-Head Attention

W praktyce nowoczesne Transformery używają **multi-head attention**, gdzie:

1. Embeddingi są projektowane do $h$ różnych podprzestrzeni (głowic)
2. Każda głowica ma własne macierze $W_Q^{(i)}, W_K^{(i)}, W_V^{(i)}$ o wymiarach prowadzących do $d_k = d_v = d_{model} / h$
3. Attention jest obliczany równolegle w każdej głowicy
4. Wyniki są konkatenowane i projektowane przez $W_O$

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W_O$$

gdzie:

$$\text{head}_i = \text{Attention}(QW_Q^{(i)}, KW_K^{(i)}, VW_V^{(i)})$$

To pozwala modelowi uczyć się różnych typów relacji równocześnie - jedna głowica może śledzić relacje składniowe, inna semantyczne, jeszcze inna pozycyjne.

## Podsumowanie

Mechanizm attention to matematycznie elegancki sposób na modelowanie zależności między elementami sekwencji. Kluczowe kroki to:

1. **Embeddingi** — reprezentacja tokenów jako wektorów (+ positional encoding w pełnej architekturze)
2. **Transformacje Q, K, V** — projekcje do przestrzeni query, key i value
3. **Attention scores** — obliczenie $QK^T/\sqrt{d_k}$
4. **Maskowanie** — opcjonalna maska przyczynowa (decoder) lub brak maski (encoder)
5. **Softmax** — normalizacja do prawdopodobieństw
6. **Ważona suma Value** — kontekstowe reprezentacje
7. **Projekcja wyjściowa** — mnożenie przez $W_O$ (w pełnej architekturze)

Ten mechanizm, powtórzony wiele razy w wielu warstwach i głowicach, tworzy potężną architekturę Transformer, która zrewolucjonizowała przetwarzanie języka naturalnego.

## Przydatne linki

- [Attention is All You Need (oryginalny artykuł)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Visualizing Attention in Transformer Models](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)

---

## EN

## Introduction

The attention mechanism is the heart of the Transformer architecture and the foundation of all modern large language models (LLMs). Although the theory behind attention can seem abstract, the best way to understand it is to walk through a concrete computational example step by step.

In this post, we'll go through a complete computational example of the attention mechanism on a simple sentence, showing all matrices and numerical calculations.

> **Note:** For clarity, we omit positional encoding and the final output projection $W_O$ in this example. In real Transformers, both are essential — positional encoding encodes token order, and $W_O$ projects the concatenated outputs from multiple heads into the model's embedding space.

## Example: "cat chases mouse"

Consider a simple sentence consisting of three words (tokens): `cat chases mouse`

And the following vocabulary of size 5:
- token 0: "cat"
- token 1: "chases"
- token 2: "mouse"
- token 3: "quickly"
- token 4: "sleeping"

### Step 1: Token Embeddings

We represent each token as an embedding vector of dimension $d_{model} = 2$ (in real models this is typically 512, 768 or more).

Each token has the following embeddings:

$$W_{vocab} = \begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}$$

where columns correspond to successive tokens in the vocabulary.

**Embeddings:**

$$E = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

where:
- $E[0] = [1.0, 0.0]$ — embedding for "cat"
- $E[1] = [0.2, 1.0]$ — embedding for "chases"
- $E[2] = [0.8, 0.0]$ — embedding for "mouse"

#### Interpreting the dimensions:
Although we don't directly control what each dimension means, we can try to discover it post hoc. Online you can find many examples where embeddings for tokens like `uncle` and `aunt` are shifted by the same constant as `king` and `queen`, meaning the model encoded gender information in a specific direction in the embedding space.

In our example, one might speculate:
- First dimension — "animality" (cat=1.0, mouse=0.8, chases=0.2)
- Second dimension — "action/movement" (chases=1.0, rest=0.0)

That said, this is just an example constructed to fit the narrative. In real models with hundreds of dimensions, interpretation is much harder and rarely unambiguous.

### Step 2: Weight Matrices — Query, Key, Value

We define three weight matrices that transform embeddings into Query, Key, and Value representations.

In standard notation, the key and value dimensions are denoted $d_k$ and $d_v$. With a single head (single-head attention), we have $d_k = d_v = d_{model}$. In multi-head attention, each head operates on $d_k = d_v = d_{model} / h$, where $h$ is the number of heads.

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

In this simple example we use identity matrices, but in real models these are learned parameters.

### Step 3: Computing Q, K, V

We multiply the embeddings by the respective weight matrices:

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

We compute attention scores using the formula:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

where $d_k = 2$ (key dimension).

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

### Step 5: Masking and Softmax

In a **decoder-only** architecture (e.g. GPT, Claude) we apply a causal mask, which prevents tokens from attending to **future** tokens — they can only attend to themselves and earlier positions. This enables autoregressive text generation.

In contrast, an **encoder-only** architecture (e.g. BERT) applies no mask — every token sees the entire sequence (bidirectional attention).

**After masking (before softmax):**

$$\frac{QK^T}{\sqrt{2}} + \text{Mask} = \begin{bmatrix}
0.71 & -\infty & -\infty \\
0.14 & 0.74 & -\infty \\
0.57 & 0.11 & 0.45
\end{bmatrix} +
\begin{bmatrix}
0 & -\infty & -\infty \\
0 & 0 & -\infty \\
0 & 0 & 0
\end{bmatrix} = \begin{bmatrix}
0.71 & -\infty & -\infty \\
0.14 & 0.74 & -\infty \\
0.57 & 0.11 & 0.45
\end{bmatrix}
$$

> **Note:** The notation $a + (-\infty)$ is mathematically informal, but is standard convention in programming. In floating-point arithmetic, `-inf` is a concrete value for which $\exp(-\infty) = 0$, effectively zeroing out masked positions after softmax.

Applying softmax row-wise ($-\infty$ values become 0):

$$\text{Attention Weights} = \text{softmax}\left(\frac{QK^T}{\sqrt{2}} + \text{Mask}\right) = \begin{bmatrix}
1.0 & 0.0 & 0.0 \\
0.35 & 0.65 & 0.0 \\
0.40 & 0.25 & 0.35
\end{bmatrix}$$

Each row shows how much that token "attends" to the available tokens:
- **Row 0 (cat):** sees only itself (the only available token), so weight = 1.0
- **Row 1 (chases):** sees "cat" and itself; attends more to itself (0.65) than to "cat" (0.35)
- **Row 2 (mouse):** sees all three tokens; attends most to "cat" (0.40), then to itself (0.35), least to "chases" (0.25)

### Step 6: Output (Contextual Representations)

The final step is multiplying the attention weights by the Value matrix:

$$\text{Attention Out} = \text{Attention Weights} \cdot V$$

$$\text{Attention Out} = 
\begin{bmatrix}
1.0 & 0.0 & 0.0 \\
0.35 & 0.65 & 0.0 \\
0.40 & 0.25 & 0.35
\end{bmatrix}
\begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}
=
\begin{bmatrix}
1.0 & 0.0 \\
0.48 & 0.65 \\
0.73 & 0.25
\end{bmatrix}
$$

The final output matrix contains **contextual representations** for each token — each vector is a weighted combination of Value vectors, where the weights depend on attention scores.

**What changed?**

- **"cat"** — unchanged $[1.0, 0.0]$, because masking means it only sees itself
- **"chases"** — changed from $[0.2, 1.0]$ to $[0.48, 0.65]$: "animality" increased (influence of "cat"), "action" decreased
- **"mouse"** — changed from $[0.8, 0.0]$ to $[0.73, 0.25]$: an "action" component appeared (influence of "chases")

Each token has absorbed information about its context. "Mouse" now knows it is being chased — the information encoded in the "action" dimension will be crucial for predicting the next token.

This is a simplified example, but exactly the same mechanism of context aggregation through weighted sums operates in widely used models.

> **Note:** In the full Transformer architecture, the output is then multiplied by a projection matrix $W_O \in \mathbb{R}^{d_v \times d_{model}}$, which we omit here.

### Step 7: Feed-Forward Network (FFN)

After the attention block comes a feed-forward network (FFN), applied independently to each position. In the original Transformer architecture ([Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)) it consists of two linear layers with a ReLU activation:

$$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

For simplicity, we use a minimal FFN with a single linear layer, no activation, and no bias:

$$\text{FFN}(x) = xW_{FFN}$$

$$W_{FFN} = \begin{bmatrix}
0.5 & 1.0 \\
1.0 & 0.5
\end{bmatrix}$$

$$\text{FFN Out} = \text{Output} \cdot W_{FFN} =
\begin{bmatrix}
1.0 & 0.0 \\
0.48 & 0.65 \\
0.73 & 0.25
\end{bmatrix}
\begin{bmatrix}
0.5 & 1.0 \\
1.0 & 0.5
\end{bmatrix}
=
\begin{bmatrix}
0.50 & 1.00 \\
0.89 & 0.81 \\
0.62 & 0.86
\end{bmatrix}
$$

> **Note:** We omit LayerNorm and residual connections, which in a real Transformer stabilize training.

### Step 8: Predicting the Next Token

To predict the next token, we need the representation of the last token:

$$\text{h\_mouse} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix}$$

It's worth noting that at this stage all other token representations are no longer needed. After the attention step, all information they carry should already be encoded in the last token.

#### Projecting to logits (unembedding)

$$\text{logits}=\text{h\_mouse}\cdot W_{vocab}= \begin{bmatrix} 0.62 & 0.86 \end{bmatrix} 
\begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}=
\begin{bmatrix}
0.62 & 0.984 & 0.496 & 0.43 & 0.0
\end{bmatrix}
$$

From the logits we can compute probabilities:

$$ P = \text{softmax}(\text{logits}) = \text{softmax}(\begin{bmatrix}0.62 & 0.984 & 0.496 & 0.43 & 0.0\end{bmatrix})=\begin{bmatrix} 0.21 & 0.30 & 0.19 & 0.18 & 0.11 \end{bmatrix} $$

**Results:**

| Token | Probability |
|-------|-------------|
| cat | 21% |
| chases | 30% |
| mouse | 19% |
| quickly | 18% |
| sleeping | 11% |

According to our simple model, the most probable next token is "chases", making the sentence:

    Cat chases mouse chases

Which is complete nonsense?

## Why This Does (Not) Work

Because the weights were chosen arbitrarily, not through training. I originally intended to pick weights that would give a sensible result, then decided it would be more valuable to remind you again that real models have millions of weights — so this simple example has no reason to work correctly. (Honestly, the first motivation was laziness; the educational narrative came after.)

If we do believe the mechanism works, it's worth noting that this is thanks to attention, which allows each token to "look at" the available tokens and decide which are most important for its representation.

In a **decoder-only** architecture with a causal mask (as in our example):
- Each token builds its representation only from itself and previous tokens
- "mouse" can incorporate context from "cat" and "chases", but not the reverse
- This enables autoregressive generation: the model predicts the next token knowing only the previous ones

In an **encoder-only** architecture (no mask):
- Each token sees the entire sequence
- "cat" can attend to "mouse" and vice versa
- The model learns bidirectional relationships between tokens

This flexibility allows Transformers to understand the structure and semantics of text without the need to define explicit grammatical rules.

## Key Properties

### Scaling by $\sqrt{d_k}$

Dividing by $\sqrt{d_k}$ prevents dot products from growing too large as dimensionality increases. Without this scaling, softmax could produce very extreme values (close to 0 or 1), which would hinder learning through vanishing gradients.

### Softmax

The softmax function normalizes scores so that the attention weights for each token sum to 1.0. It also sharpens differences between values — larger values become even more dominant after softmax.

### Q, K, V Matrices

Separating into Query, Key, and Value gives the model flexibility:
- **Query**: "what am I looking for?"
- **Key**: "what do I offer as a matching key?"
- **Value**: "what information do I pass on?"

A token can search for specific features (Q), be retrieved by different features (K), and transmit yet other information (V). This separation allows asymmetric relationships between tokens.

## Multi-Head Attention

In practice, modern Transformers use **multi-head attention**, where:

1. Embeddings are projected into $h$ different subspaces (heads)
2. Each head has its own matrices $W_Q^{(i)}, W_K^{(i)}, W_V^{(i)}$ with dimensions leading to $d_k = d_v = d_{model} / h$
3. Attention is computed in parallel for each head
4. Results are concatenated and projected through $W_O$

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W_O$$

where:

$$\text{head}_i = \text{Attention}(QW_Q^{(i)}, KW_K^{(i)}, VW_V^{(i)})$$

This allows the model to learn different types of relationships simultaneously — one head may track syntactic relations, another semantic ones, another positional ones.

## Summary

The attention mechanism is a mathematically elegant way to model dependencies between elements of a sequence. The key steps are:

1. **Embeddings** — representing tokens as vectors (+ positional encoding in the full architecture)
2. **Q, K, V transformations** — projections into query, key, and value spaces
3. **Attention scores** — computing $QK^T/\sqrt{d_k}$
4. **Masking** — optional causal mask (decoder) or no mask (encoder)
5. **Softmax** — normalization to probabilities
6. **Weighted sum of Values** — contextual representations
7. **Output projection** — multiplication by $W_O$ (in the full architecture)

This mechanism, repeated many times across many layers and heads, creates the powerful Transformer architecture that has revolutionized natural language processing.

## Useful Links

- [Attention is All You Need (original paper)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Visualizing Attention in Transformer Models](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)