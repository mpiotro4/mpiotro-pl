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

Każdy z tokenów posiada następujące embedingi:

$$W_{vocab} = \begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}$$

gdzie kolumny oodpowiadają kolejnym tokenom ze słownika.

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
Choć nie kontrolujemy bezpośrednio, co oznacza każdy wymiar, możemy próbować to odkryć post hoc. W sieci można znaleźć wiele przykładów gdzie np. embedingi tokenów `wujek` i `ciocia` są przesuniętę o pewną stałą wartość tak samo jak tokeny `król` i `królowa`. Oznacza to, że model zakodował informację o płci w konkretnym kierunku przestrzeni.
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

Każdy token wchłonął informację o swoim kontekście. "Mouse" wie teraz, że jest goniona, informacja, zakodowana w wymiarze "akcji", będzie kluczowa przy predykcji następnego tokenu.

To uproszczony przykład, ale dokładnie ten sam mechanizm agregacji kontekstu przez ważone sumy zachodzi w powszechnie używanych modelach.

> **Uwaga:** W pełnej architekturze Transformer wyjście jest następnie mnożone przez macierz projekcji $W_O \in \mathbb{R}^{d_v \times d_{model}}$, co tutaj pomijamy.

### Krok 7: Feed-Forward Network (FFN)
Po bloku attention następuje sieć feed-forward (FFN), stosowana niezależnie do każdej pozycji. W oryginalnej architekturze Transformera ([Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)) składa się z dwóch warstw liniowych z aktywacją ReLU:

$$\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$$

Dla uproszczenia użyjemy minimalnego FFN z jedną warstwą liniową bez aktywacji bez bias:

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

>Uwaga: Pomijamy tu LayerNorm i residual connections, które w prawdziwym Transformerze stabilizują uczenie.

### Krok 8: Predykcja następnego tokena

Aby przewidzieć następny token, potrzebna jest reprezentacja ostatniego tokena:

$$\text{h_mouse} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix} $$

Warto zauważyć, że na tym etapie wszystkie pozostałe tokeny nie są nam potrzebne. Po etapie attention wszystkie informacje, które niosą powinny być już zawarte w ostatnim tokenie.

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

Wychodzi na to że wg. naszego prostego modelu kolejny najbardziej prawdopodobny token to "chases" czyli zdanie brzmi:

    Cat chases mouse chases

Co jest totalnie bez sensu? 

## Dlaczego to (nie) działa?

Mechanizm attention pozwala każdemu tokenowi "spojrzeć" na dostępne tokeny i zadecydować, które z nich są najważniejsze dla jego reprezentacji. 

W architekturze **decoder-only** z maską przyczynową (jak w naszym przykładzie):
- Każdy token buduje swoją reprezentację tylko na podstawie siebie i poprzednich tokenów
- "mouse" może uwzględnić kontekst z "cat" i "chases", ale nie odwrotnie
- To umożliwia autoregresyjną generację: model przewiduje następny token znając tylko poprzednie

W architekturze **encoder-only** (bez maski):
- Każdy token widzi całą sekwencję
- "cat" może zwracać uwagę na "mouse" i odwrotnie
- Model uczy się dwukierunkowych relacji między tokenami

Ta elastyczność pozwala Transformerom rozumieć strukturę i semantykę tekstu bez konieczności definiowania reguł gramatycznych.

Ale wracając, uzyskany wynik nie ma sensu, bo wagi zostały dobrane nie na drodze treningu, lecz arbitralnie. Początkowo chciałem dobrać wagi tak, aby uzyskać sensowny wynik, po czym stwierdziłem, że większą wartość będzie miało, jeśli znowu przypomnę, że w prawdziwych modelach tych wag są miliony, więc ten prosty przykład nie ma prawa działać poprawnie.

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

To pozwala modelowi uczyć się różnych typów relacji równocześnie - Jedna głowica może śledzić relacje składniowe, inna semantyczne, jeszcze inna pozycyjne.

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