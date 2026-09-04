---
title_pl: "Mechanizm attention krok po kroku — przykład obliczeniowy"
title_en: "The Attention Mechanism Step by Step — A Computational Example"
date: 2025-12-29
author: "Marcin Piotrowski"
tags: ["NLP", "transformers", "attention", "deep learning", "LLM"]
description_pl: "Kompletny przykład obliczeniowy mechanizmu attention z artykułu „Attention is All You Need” — od embeddingów, przez macierze Q, K, V i maskę przyczynową, po rozkład prawdopodobieństwa następnego tokenu."
description_en: "A complete computational example of the attention mechanism from 'Attention is All You Need' — from embeddings through Q, K, V and the causal mask to the next-token distribution."
---

## PL

## Wstęp

Mechanizm attention jest sercem architektury Transformer i podstawą działania wszystkich nowoczesnych dużych modeli językowych. Teoria stojąca za nim bywa abstrakcyjna, dlatego najlepszym sposobem na jej zrozumienie jest prześledzenie konkretnego przykładu obliczeniowego.

W tym wpisie przechodzimy przez pełny przebieg obliczeń na trzywyrazowym zdaniu — od embeddingów aż po rozkład prawdopodobieństwa następnego tokenu — pokazując wszystkie macierze po drodze.

> **Uwaga:** dla przejrzystości pomijamy positional encoding oraz końcową projekcję wyjściową $W_O$. W rzeczywistych Transformerach oba elementy są niezbędne: positional encoding koduje kolejność tokenów, a $W_O$ rzutuje sklejone wyjścia z wielu głowic z powrotem do przestrzeni modelu.

## Przykład: „cat chases mouse”

Rozważmy zdanie złożone z trzech tokenów: `cat chases mouse`, oraz słownik o rozmiarze 5:

- token 0: „cat”
- token 1: „chases”
- token 2: „mouse”
- token 3: „quickly”
- token 4: „sleeping”

### Krok 1: Embeddingi tokenów

Każdy token reprezentujemy wektorem o wymiarze $d_{model} = 2$ (w rzeczywistych modelach zazwyczaj 512, 768 lub więcej). Cały słownik mieści się więc w macierzy $2 \times 5$, której kolumny są embeddingami kolejnych tokenów:

$$W_{vocab} = \begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}$$

Nasze zdanie to tokeny 0, 1 i 2, więc jego macierz embeddingów $E$ powstaje przez wybranie trzech pierwszych kolumn $W_{vocab}$ i zapisanie ich jako wierszy:

$$E = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

gdzie:

- $E[0] = [1.0,\ 0.0]$ — embedding dla „cat”
- $E[1] = [0.2,\ 1.0]$ — embedding dla „chases”
- $E[2] = [0.8,\ 0.0]$ — embedding dla „mouse”

#### Interpretacja wymiarów

Nie kontrolujemy bezpośrednio tego, co oznacza pojedynczy wymiar, ale można próbować odczytać to post hoc. Klasyczna obserwacja mówi, że embeddingi par takich jak `król` i `królowa` czy `wujek` i `ciocia` są przesunięte o zbliżony wektor — model zakodował informację o płci wzdłuż konkretnego kierunku w przestrzeni.

W naszym przykładzie można by spekulować, że:

- pierwszy wymiar odpowiada „zwierzęcości” (cat = 1.0, mouse = 0.8, chases = 0.2),
- drugi wymiar odpowiada „akcji/ruchowi” (chases = 1.0, pozostałe = 0.0).

To jednak liczby dobrane pod tezę. W modelach o setkach wymiarów interpretacja jest znacznie trudniejsza i rzadko bywa jednoznaczna.

### Krok 2: Macierze wag — Query, Key, Value

Definiujemy trzy macierze wag, które przekształcają embeddingi w reprezentacje Query, Key i Value. Wymiar klucza i wartości oznaczamy standardowo jako $d_k$ i $d_v$. Przy pojedynczej głowicy zachodzi $d_k = d_v = d_{model}$; w multi-head attention każda głowica operuje na $d_k = d_v = d_{model} / h$, gdzie $h$ to liczba głowic.

$$W_Q = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix} \qquad
W_K = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix} \qquad
W_V = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}$$

Wybieramy macierze jednostkowe, żeby nie zaciemniać rachunków — w prawdziwych modelach są to wyuczone parametry, a to właśnie one decydują, czego każda głowica szuka w sekwencji.

### Krok 3: Obliczenie Q, K, V

Mnożymy embeddingi przez odpowiednie macierze wag. Przy macierzach jednostkowych wszystkie trzy reprezentacje są identyczne z $E$:

$$Q = E W_Q = K = E W_K = V = E W_V = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

### Krok 4: Attention scores

Attention obliczamy według wzoru, który można znaleźć w [oryginalnym artykule o attention](https://arxiv.org/abs/1706.03762):

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

gdzie $d_k = 2$.

**Iloczyn $QK^T$:**

$$QK^T = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix} \begin{bmatrix}
1.0 & 0.2 & 0.8 \\
0.0 & 1.0 & 0.0
\end{bmatrix} = \begin{bmatrix}
1.0 & 0.2 & 0.8 \\
0.2 & 1.04 & 0.16 \\
0.8 & 0.16 & 0.64
\end{bmatrix}$$

Element $(i, j)$ tej macierzy to iloczyn skalarny zapytania tokenu $i$ z kluczem tokenu $j$ — miara tego, jak dobrze do siebie pasują.

**Skalowanie przez $\sqrt{d_k} = \sqrt{2} \approx 1.414$:**

$$\frac{QK^T}{\sqrt{2}} = \begin{bmatrix}
0.71 & 0.14 & 0.57 \\
0.14 & 0.74 & 0.11 \\
0.57 & 0.11 & 0.45
\end{bmatrix}$$

### Krok 5: Maskowanie i softmax

W architekturze **decoder-only** (np. GPT, Claude) stosujemy maskę przyczynową (causal mask), która odcina tokenom dostęp do **przyszłości** — każdy token widzi tylko siebie i pozycje wcześniejsze. To właśnie ta własność umożliwia autoregresyjną generację tekstu.

Dla porównania architektura **encoder-only** (np. BERT) nie stosuje maski: każdy token widzi całą sekwencję (bidirectional attention).

**Dodanie maski (przed softmax):**

$$\frac{QK^T}{\sqrt{2}} + \text{Mask} = \begin{bmatrix}
0.71 & 0.14 & 0.57 \\
0.14 & 0.74 & 0.11 \\
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
\end{bmatrix}$$

> **Uwaga:** zapis $a + (-\infty)$ jest matematycznie nieformalny, ale stanowi standardową konwencję implementacyjną. W arytmetyce zmiennoprzecinkowej `-inf` to konkretna wartość, dla której $\exp(-\infty) = 0$, co zeruje zamaskowane pozycje po softmaksie.

Softmax stosujemy niezależnie do każdego wiersza:

$$\text{Attention Weights} = \text{softmax}\left(\frac{QK^T}{\sqrt{2}} + \text{Mask}\right) = \begin{bmatrix}
1.0 & 0.0 & 0.0 \\
0.35 & 0.65 & 0.0 \\
0.40 & 0.25 & 0.35
\end{bmatrix}$$

Każdy wiersz mówi, jak bardzo dany token „zwraca uwagę” na dostępne pozycje:

- **wiersz 0 („cat”)** — widzi wyłącznie siebie, więc cała waga trafia na jedyny dostępny token;
- **wiersz 1 („chases”)** — widzi „cat” i siebie, przy czym mocniej na siebie (0.65) niż na „cat” (0.35);
- **wiersz 2 („mouse”)** — widzi wszystkie trzy pozycje: najmocniej „cat” (0.40), potem siebie (0.35), najsłabiej „chases” (0.25).

### Krok 6: Wyjście — reprezentacje kontekstowe

Ostatnim krokiem samego attention jest pomnożenie wag przez macierz Value:

$$\text{Attention Out} = \text{Attention Weights} \cdot V =
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
\end{bmatrix}$$

Otrzymana macierz zawiera **reprezentacje kontekstowe** każdego tokenu — każdy wiersz jest ważoną kombinacją wektorów Value, a wagi pochodzą z attention scores.

**Co się zmieniło?**

- **„cat”** — bez zmian, $[1.0,\ 0.0]$, ponieważ przez maskę widzi tylko siebie;
- **„chases”** — z $[0.2,\ 1.0]$ na $[0.48,\ 0.65]$: wzrosła „zwierzęcość” (wpływ „cat”), spadła „akcja”;
- **„mouse”** — z $[0.8,\ 0.0]$ na $[0.73,\ 0.25]$: pojawiła się składowa „akcji” (wpływ „chases”).

Każdy token wchłonął informację o swoim kontekście. „Mouse” niesie teraz ślad tego, że jest gonione, a ta informacja okaże się kluczowa przy predykcji kolejnego tokenu. Przykład jest uproszczony, ale dokładnie ten sam mechanizm — agregacja kontekstu przez ważone sumy — działa w modelach produkcyjnych.

> **Uwaga:** w pełnej architekturze wyjście jest jeszcze mnożone przez macierz projekcji $W_O \in \mathbb{R}^{d_v \times d_{model}}$, którą tutaj pomijamy.

### Krok 7: Sieć feed-forward (FFN)

Po bloku attention następuje sieć feed-forward, stosowana niezależnie do każdej pozycji. W oryginalnej architekturze ([Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)) są to dwie warstwy liniowe z aktywacją ReLU:

$$\text{FFN}(x) = \max(0,\ xW_1 + b_1)W_2 + b_2$$

Dla uproszczenia użyjemy minimalnej wersji: jedna warstwa liniowa, bez aktywacji i bez biasu.

$$\text{FFN}(x) = xW_{FFN}, \qquad W_{FFN} = \begin{bmatrix}
0.5 & 1.0 \\
1.0 & 0.5
\end{bmatrix}$$

$$\text{FFN Out} = \text{Attention Out} \cdot W_{FFN} =
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
\end{bmatrix}$$

> **Uwaga:** pomijamy LayerNorm i połączenia rezydualne, które w prawdziwym Transformerze stabilizują uczenie.

### Krok 8: Predykcja następnego tokenu

Rozkład prawdopodobieństwa następnego tokenu odczytujemy z reprezentacji ostatniej pozycji:

$$h_{\text{mouse}} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix}$$

To w niej — dzięki attention — zebrał się kontekst całego zdania. Warto jednak zaznaczyć, że pozostałe pozycje nie stają się zbędne: ich klucze i wartości są nadal potrzebne w kolejnych warstwach, a podczas treningu każda pozycja przewiduje swój własny następny token. Odczyt z ostatniego wiersza to sytuacja z etapu generowania.

#### Projekcja na logity (unembedding)

Do przejścia z reprezentacji na wyniki dla całego słownika wykorzystamy ponownie $W_{vocab}$. Ten zabieg — użycie tej samej macierzy jako embeddingu i jako unembeddingu — nazywa się **weight tying** i jest stosowany w wielu prawdziwych modelach; oszczędza parametry i zwykle poprawia jakość.

$$\text{logits} = h_{\text{mouse}} \cdot W_{vocab} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix}
\begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}=
\begin{bmatrix}
0.62 & 0.984 & 0.496 & 0.43 & 0.0
\end{bmatrix}$$

Z logitów obliczamy prawdopodobieństwa:

$$P = \text{softmax}(\text{logits}) = \begin{bmatrix} 0.21 & 0.31 & 0.19 & 0.18 & 0.11 \end{bmatrix}$$

| Token | Prawdopodobieństwo |
|-------|--------------------|
| cat | 21% |
| chases | 31% |
| mouse | 19% |
| quickly | 18% |
| sleeping | 11% |

Według naszego modelu najbardziej prawdopodobnym kolejnym tokenem jest „chases”, co daje zdanie:

    cat chases mouse chases

Wynik jest bez sensu — i to dobry punkt wyjścia do pytania, dlaczego.

## Dlaczego to (nie) działa

Ponieważ wagi nie pochodzą z treningu. Dobrałem je ręcznie, tak żeby rachunki dało się prześledzić na kartce. Mógłbym je dostroić pod sensowną odpowiedź, ale wtedy przykład sugerowałby coś nieprawdziwego: że dwa wymiary i kilkanaście parametrów wystarczą do modelowania języka. Nie wystarczą. W prawdziwych modelach parametrów są miliardy i dopiero ich wspólne dopasowanie na ogromnym korpusie sprawia, że predykcje zaczynają mieć sens.

Co natomiast działa niezależnie od wartości wag, to sama struktura obliczeń. Attention pozwala każdemu tokenowi „spojrzeć” na dostępne pozycje i zdecydować, które z nich są istotne dla jego reprezentacji.

W architekturze **decoder-only** z maską przyczynową (jak w naszym przykładzie):

- każdy token buduje reprezentację wyłącznie na podstawie siebie i pozycji wcześniejszych,
- „mouse” może uwzględnić kontekst z „cat” i „chases”, ale nie odwrotnie,
- to umożliwia generację autoregresyjną: model przewiduje następny token, znając jedynie poprzednie.

W architekturze **encoder-only** (bez maski):

- każdy token widzi całą sekwencję,
- „cat” może zwracać uwagę na „mouse” i odwrotnie,
- model uczy się relacji dwukierunkowych.

Ta elastyczność pozwala Transformerom uchwycić strukturę i semantykę tekstu bez ręcznego definiowania reguł gramatycznych.

## Kluczowe właściwości

### Skalowanie przez $\sqrt{d_k}$

Dzielenie przez $\sqrt{d_k}$ powstrzymuje iloczyny skalarne przed zbyt szybkim wzrostem wraz z wymiarowością. Przy dużych wartościach softmax wchodzi w obszar nasycenia — rozkład staje się niemal zerojedynkowy, a gradienty zanikają, co utrudnia uczenie.

### Softmax

Softmax normalizuje wyniki tak, by wagi attention w każdym wierszu sumowały się do 1.0. Przy okazji wyostrza różnice: wartości większe stają się po transformacji jeszcze bardziej dominujące.

### Macierze Q, K, V

Rozdzielenie na Query, Key i Value daje modelowi swobodę:

- **Query** — „czego szukam?”
- **Key** — „po czym można mnie znaleźć?”
- **Value** — „jaką informację przekazuję?”

Token może szukać jednych cech (Q), być wyszukiwany po innych (K) i przekazywać jeszcze inne (V). Ta separacja dopuszcza relacje asymetryczne — to, że A zwraca uwagę na B, nie oznacza, że B zwraca uwagę na A.

## Multi-head attention

W praktyce nowoczesne Transformery używają **multi-head attention**:

1. embeddingi są rzutowane do $h$ różnych podprzestrzeni (głowic),
2. każda głowica ma własne macierze $W_Q^{(i)}, W_K^{(i)}, W_V^{(i)}$ prowadzące do $d_k = d_v = d_{model} / h$,
3. attention liczony jest równolegle w każdej głowicy,
4. wyniki są konkatenowane i rzutowane przez $W_O$.

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)\,W_O$$

gdzie:

$$\text{head}_i = \text{Attention}(QW_Q^{(i)},\ KW_K^{(i)},\ VW_V^{(i)})$$

Dzięki temu model uczy się kilku typów relacji równocześnie — jedna głowica może śledzić zależności składniowe, inna semantyczne, jeszcze inna pozycyjne.

## Podsumowanie

Attention to matematycznie oszczędny sposób modelowania zależności między elementami sekwencji. Kluczowe kroki to:

1. **embeddingi** — reprezentacja tokenów jako wektorów (+ positional encoding w pełnej architekturze),
2. **transformacje Q, K, V** — projekcje do przestrzeni query, key i value,
3. **attention scores** — obliczenie $QK^T/\sqrt{d_k}$,
4. **maskowanie** — maska przyczynowa (decoder) lub jej brak (encoder),
5. **softmax** — normalizacja do rozkładu prawdopodobieństwa,
6. **ważona suma Value** — reprezentacje kontekstowe,
7. **projekcja wyjściowa** — mnożenie przez $W_O$ (w pełnej architekturze).

Ten mechanizm, powtórzony w wielu warstwach i wielu głowicach, tworzy architekturę, która zmieniła przetwarzanie języka naturalnego.

## Przydatne linki

- [Attention is All You Need (oryginalny artykuł)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Transformer: A Novel Neural Network Architecture for Language Understanding](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)

---

## EN

## Introduction

The attention mechanism is the heart of the Transformer architecture and the foundation of every modern large language model. The theory behind it can feel abstract, which is why the best way to understand it is to follow a concrete computational example.

In this post we walk through the full set of calculations on a three-word sentence — from embeddings all the way to the next-token probability distribution — showing every matrix along the way.

> **Note:** for clarity we omit positional encoding and the final output projection $W_O$. Both are essential in real Transformers: positional encoding encodes token order, and $W_O$ projects the concatenated outputs of multiple heads back into the model's space.

## Example: "cat chases mouse"

Consider a sentence made of three tokens, `cat chases mouse`, and a vocabulary of size 5:

- token 0: "cat"
- token 1: "chases"
- token 2: "mouse"
- token 3: "quickly"
- token 4: "sleeping"

### Step 1: Token embeddings

We represent each token as a vector of dimension $d_{model} = 2$ (in real models this is typically 512, 768 or more). The entire vocabulary therefore fits into a $2 \times 5$ matrix whose columns are the embeddings of successive tokens:

$$W_{vocab} = \begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}$$

Our sentence consists of tokens 0, 1 and 2, so its embedding matrix $E$ is formed by taking the first three columns of $W_{vocab}$ and writing them as rows:

$$E = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

where:

- $E[0] = [1.0,\ 0.0]$ — embedding for "cat"
- $E[1] = [0.2,\ 1.0]$ — embedding for "chases"
- $E[2] = [0.8,\ 0.0]$ — embedding for "mouse"

#### Interpreting the dimensions

We do not directly control what a single dimension means, but we can try to read it post hoc. The classic observation is that embeddings for pairs such as `king` and `queen`, or `uncle` and `aunt`, are separated by a similar vector — the model has encoded gender along a particular direction in the space.

In our example one might speculate that:

- the first dimension corresponds to "animality" (cat = 1.0, mouse = 0.8, chases = 0.2),
- the second corresponds to "action/movement" (chases = 1.0, the rest = 0.0).

These numbers were chosen to fit the story, though. In models with hundreds of dimensions, interpretation is much harder and rarely unambiguous.

### Step 2: Weight matrices — Query, Key, Value

We define three weight matrices that transform embeddings into Query, Key and Value representations. The key and value dimensions are conventionally written $d_k$ and $d_v$. With a single head, $d_k = d_v = d_{model}$; in multi-head attention each head operates on $d_k = d_v = d_{model} / h$, where $h$ is the number of heads.

$$W_Q = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix} \qquad
W_K = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix} \qquad
W_V = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}$$

We use identity matrices to keep the arithmetic readable. In real models these are learned parameters, and they are precisely what determines what each head looks for in the sequence.

### Step 3: Computing Q, K, V

We multiply the embeddings by the respective weight matrices. With identity matrices, all three representations are identical to $E$:

$$Q = E W_Q = K = E W_K = V = E W_V = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix}$$

### Step 4: Attention scores

Attention is computed with the formula which can be found in [original attention article](https://arxiv.org/abs/1706.03762):
:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

where $d_k = 2$.

**The product $QK^T$:**

$$QK^T = \begin{bmatrix}
1.0 & 0.0 \\
0.2 & 1.0 \\
0.8 & 0.0
\end{bmatrix} \begin{bmatrix}
1.0 & 0.2 & 0.8 \\
0.0 & 1.0 & 0.0
\end{bmatrix} = \begin{bmatrix}
1.0 & 0.2 & 0.8 \\
0.2 & 1.04 & 0.16 \\
0.8 & 0.16 & 0.64
\end{bmatrix}$$

Entry $(i, j)$ is the dot product of token $i$'s query with token $j$'s key — a measure of how well they match.

**Scaling by $\sqrt{d_k} = \sqrt{2} \approx 1.414$:**

$$\frac{QK^T}{\sqrt{2}} = \begin{bmatrix}
0.71 & 0.14 & 0.57 \\
0.14 & 0.74 & 0.11 \\
0.57 & 0.11 & 0.45
\end{bmatrix}$$

### Step 5: Masking and softmax

In a **decoder-only** architecture (GPT, Claude) we apply a causal mask, which cuts off access to the **future** — each token sees only itself and earlier positions. This property is what makes autoregressive generation possible.

An **encoder-only** architecture (BERT) applies no mask: every token sees the entire sequence (bidirectional attention).

**Adding the mask (before softmax):**

$$\frac{QK^T}{\sqrt{2}} + \text{Mask} = \begin{bmatrix}
0.71 & 0.14 & 0.57 \\
0.14 & 0.74 & 0.11 \\
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
\end{bmatrix}$$

> **Note:** the notation $a + (-\infty)$ is mathematically informal but is a standard implementation convention. In floating-point arithmetic, `-inf` is a concrete value for which $\exp(-\infty) = 0$, zeroing out masked positions after the softmax.

Softmax is applied independently to each row:

$$\text{Attention Weights} = \text{softmax}\left(\frac{QK^T}{\sqrt{2}} + \text{Mask}\right) = \begin{bmatrix}
1.0 & 0.0 & 0.0 \\
0.35 & 0.65 & 0.0 \\
0.40 & 0.25 & 0.35
\end{bmatrix}$$

Each row shows how much that token attends to the available positions:

- **row 0 ("cat")** — sees only itself, so all the weight goes to the single available token;
- **row 1 ("chases")** — sees "cat" and itself, attending more to itself (0.65) than to "cat" (0.35);
- **row 2 ("mouse")** — sees all three positions: most to "cat" (0.40), then itself (0.35), least to "chases" (0.25).

### Step 6: Output — contextual representations

The final step of attention itself is multiplying the weights by the Value matrix:

$$\text{Attention Out} = \text{Attention Weights} \cdot V =
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
\end{bmatrix}$$

The resulting matrix holds the **contextual representation** of each token — every row is a weighted combination of Value vectors, with the weights coming from the attention scores.

**What changed?**

- **"cat"** — unchanged at $[1.0,\ 0.0]$, since the mask means it sees only itself;
- **"chases"** — from $[0.2,\ 1.0]$ to $[0.48,\ 0.65]$: "animality" rose (influence of "cat"), "action" fell;
- **"mouse"** — from $[0.8,\ 0.0]$ to $[0.73,\ 0.25]$: an "action" component appeared (influence of "chases").

Each token has absorbed information about its context. "Mouse" now carries a trace of being chased, and that information will matter when predicting the next token. The example is simplified, but exactly the same mechanism — aggregating context through weighted sums — runs inside production models.

> **Note:** in the full architecture the output is additionally multiplied by a projection matrix $W_O \in \mathbb{R}^{d_v \times d_{model}}$, which we omit here.

### Step 7: Feed-forward network (FFN)

The attention block is followed by a feed-forward network applied independently to each position. In the original architecture ([Vaswani et al., 2017](https://arxiv.org/abs/1706.03762)) it is two linear layers with a ReLU activation:

$$\text{FFN}(x) = \max(0,\ xW_1 + b_1)W_2 + b_2$$

For simplicity we use a minimal version: one linear layer, no activation, no bias.

$$\text{FFN}(x) = xW_{FFN}, \qquad W_{FFN} = \begin{bmatrix}
0.5 & 1.0 \\
1.0 & 0.5
\end{bmatrix}$$

$$\text{FFN Out} = \text{Attention Out} \cdot W_{FFN} =
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
\end{bmatrix}$$

> **Note:** we omit LayerNorm and residual connections, which stabilize training in a real Transformer.

### Step 8: Predicting the next token

The next-token distribution is read from the representation of the last position:

$$h_{\text{mouse}} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix}$$

This is where attention has gathered the context of the whole sentence. It is worth stressing, though, that the other positions do not become redundant: their keys and values are still needed in subsequent layers, and during training every position predicts its own next token. Reading from the last row is the generation-time picture.

#### Projecting to logits (unembedding)

To go from a representation to scores over the whole vocabulary, we reuse $W_{vocab}$. Using the same matrix for both embedding and unembedding is called **weight tying**; it is common in real models, saves parameters and usually improves quality.

$$\text{logits} = h_{\text{mouse}} \cdot W_{vocab} = \begin{bmatrix} 0.62 & 0.86 \end{bmatrix}
\begin{bmatrix}
1.0 & 0.2 & 0.8 & 0.0 &  0.0 \\
0.0 & 1.0 & 0.0 & 0.5 &  0.0
\end{bmatrix}=
\begin{bmatrix}
0.62 & 0.984 & 0.496 & 0.43 & 0.0
\end{bmatrix}$$

From the logits we compute probabilities:

$$P = \text{softmax}(\text{logits}) = \begin{bmatrix} 0.21 & 0.31 & 0.19 & 0.18 & 0.11 \end{bmatrix}$$

| Token | Probability |
|-------|-------------|
| cat | 21% |
| chases | 31% |
| mouse | 19% |
| quickly | 18% |
| sleeping | 11% |

According to our model the most likely next token is "chases", which gives the sentence:

    cat chases mouse chases

The result is nonsense — and that is a good starting point for asking why.

## Why this does (not) work

Because the weights did not come from training. I picked them by hand so that the arithmetic could be followed on paper. I could have tuned them toward a sensible answer, but the example would then imply something false: that two dimensions and a dozen parameters are enough to model language. They are not. Real models have billions of parameters, and it is only their joint fitting on an enormous corpus that makes predictions meaningful.

What does work regardless of the weight values is the structure of the computation. Attention lets every token look at the available positions and decide which of them matter for its own representation.

In a **decoder-only** architecture with a causal mask (as in our example):

- each token builds its representation only from itself and earlier positions,
- "mouse" can incorporate context from "cat" and "chases", but not the reverse,
- this enables autoregressive generation: the model predicts the next token knowing only the previous ones.

In an **encoder-only** architecture (no mask):

- each token sees the entire sequence,
- "cat" can attend to "mouse" and vice versa,
- the model learns bidirectional relationships.

This flexibility lets Transformers capture the structure and semantics of text without hand-written grammatical rules.

## Key properties

### Scaling by $\sqrt{d_k}$

Dividing by $\sqrt{d_k}$ keeps dot products from growing too quickly as dimensionality increases. With large values the softmax enters its saturated regime — the distribution becomes almost one-hot and gradients vanish, which makes learning harder.

### Softmax

Softmax normalizes the scores so that attention weights in each row sum to 1.0. It also sharpens differences: larger values become even more dominant after the transformation.

### Q, K, V matrices

Splitting into Query, Key and Value gives the model freedom:

- **Query** — "what am I looking for?"
- **Key** — "what can I be found by?"
- **Value** — "what information do I pass on?"

A token can search by one set of features (Q), be retrieved by another (K) and transmit yet another (V). This separation permits asymmetric relations — A attending to B does not imply B attending to A.

## Multi-head attention

In practice, modern Transformers use **multi-head attention**:

1. embeddings are projected into $h$ different subspaces (heads),
2. each head has its own $W_Q^{(i)}, W_K^{(i)}, W_V^{(i)}$ leading to $d_k = d_v = d_{model} / h$,
3. attention is computed in parallel in every head,
4. the results are concatenated and projected through $W_O$.

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h)\,W_O$$

where:

$$\text{head}_i = \text{Attention}(QW_Q^{(i)},\ KW_K^{(i)},\ VW_V^{(i)})$$

This lets the model learn several kinds of relationship at once — one head may track syntactic dependencies, another semantic ones, another positional ones.

## Summary

Attention is a mathematically economical way of modelling dependencies between elements of a sequence. The key steps are:

1. **embeddings** — representing tokens as vectors (+ positional encoding in the full architecture),
2. **Q, K, V transformations** — projections into query, key and value spaces,
3. **attention scores** — computing $QK^T/\sqrt{d_k}$,
4. **masking** — a causal mask (decoder) or none (encoder),
5. **softmax** — normalization into a probability distribution,
6. **weighted sum of Values** — contextual representations,
7. **output projection** — multiplication by $W_O$ (in the full architecture).

Repeated across many layers and many heads, this mechanism forms the architecture that changed natural language processing.

## Useful links

- [Attention is All You Need (original paper)](https://arxiv.org/abs/1706.03762)
- [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)
- [Transformer: A Novel Neural Network Architecture for Language Understanding](https://ai.googleblog.com/2017/08/transformer-novel-neural-network.html)
