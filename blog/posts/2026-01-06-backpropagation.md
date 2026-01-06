---
title_pl: "Wsteczna propagacja gradientu krok po kroku - przykład obliczeniowy"
date: 2025-01-06
author: "Marcin Piotrowski"
tags: ["deep learning", "backpropagation", "gradient descent", "sieci neuronowe"]
description_pl: "Szczegółowy przykład obliczeniowy backpropagation z ręcznymi obliczeniami. Od forward pass przez backward pass aż po krok optymalizatora."
---

## PL

## Wstęp

Wsteczna propagacja błędu (backpropagation) to algorytm, który umożliwił praktyczne trenowanie głębokich sieci neuronowych. Działa na prostej zasadzie: oblicza pochodne funkcji straty względem wag sieci, wskazując kierunek, w którym należy je zmodyfikować, aby zmniejszyć błąd.
Warto wiedzieć, że backpropagation to uniwersalny algorytm optymalizacji – działa dla dowolnej funkcji złożonej z wielu operacji, nie tylko sieci neuronowych. Na przykład w transformerach tym samym mechanizmem trenowane są zarówno wagi sieci, jak i embeddingi tokenów, które są po prostu tablicą parametrów, a nie warstwą neuronową.

Dobrym sposobem na zrozumienie backpropagation jest prześledzenie konkretnego przykładu z kartką i długopisem. W tym wpisie przeprowadzimy kompletne obliczenia dla prostej funkcji.

## Gradient, pochodna, pochodna cząstkowa – wyjaśnienie terminów

Zanim przejdziemy do obliczeń, jeszcze szybka dygresja matematyczna:

**Pochodna** – dotyczy funkcji jednej zmiennej: $f(x)$. Mówi, jak szybko funkcja rośnie wraz ze zmianą $x$. Oznaczenie: $\frac{df}{dx}$ lub $f'(x)$.

**Pochodna cząstkowa** – dotyczy funkcji wielu zmiennych: $f(x, y, z)$. Mówi, jak funkcja zmienia się względem **jednej** zmiennej, przy założeniu, że pozostałe są stałe. Oznaczenie: $\frac{\partial f}{\partial x}$.

**Gradient** – to **wektor** wszystkich pochodnych cząstkowych. Dla funkcji $f(x, y, z)$ gradient to:

$$\nabla f = \left[\frac{\partial f}{\partial x}, \frac{\partial f}{\partial y}, \frac{\partial f}{\partial z}\right]$$

Gradient wskazuje kierunek najszybszego wzrostu funkcji.

**W tym wpisie** używamy terminu "gradient" w kontekście całego wektora gradientów (np. "obliczamy gradienty parametrów"), a "pochodna cząstkowa" dla poszczególnych składowych (np. $\frac{\partial L}{\partial a}$)

## Przykład obliczeniowy

Rozważmy funkcję straty (loss) zależną od trzech parametrów:

$$L = (a \cdot b + c)^2$$

**Dane wejściowe:**

* $a = 2$
* $b = -3$  
* $c = 10$

Naszym celem jest obliczenie gradientów $\frac{\partial L}{\partial a}$, $\frac{\partial L}{\partial b}$, $\frac{\partial L}{\partial c}$. Powiedzą nam one, jak zmiana każdego parametru wpływa na wartość funkcji straty.

### Graf obliczeniowy

Rozbijmy funkcję na elementarne operacje:
```
a ──┐
    ├──[×]── d ──┐
b ──┘            ├──[+]── e ──[^2]── L
             c ──┘
```

Gdzie:

* $d = a \cdot b$
* $e = d + c$
* $L = e^2$

Kluczowe jest zdekomponowanie całej funkcji na atomowe operacje, dzięki temu policzenie pochodnych dla każdej z nich będzie trywialne.

### Krok 1: Forward Pass

Obliczamy wartości "do przodu", od wejść do wyjścia:

$$d = a \cdot b = 2 \cdot (-3) = -6$$

$$e = d + c = -6 + 10 = 4$$

$$L = e^2 = 4^2 = 16$$

Zapamiętujemy wszystkie wartości pośrednie, w backward pass będą potrzebne do obliczenia gradientów. Bez nich musielibyśmy przeliczać je od nowa, co byłoby nieefektywne.

| Zmienna | Wartość |
|---------|---------|
| $a$ | 2 |
| $b$ | -3 |
| $c$ | 10 |
| $d$ | -6 |
| $e$ | 4 |
| $L$ | 16 |

## Krok 2: Backward Pass

Teraz propagujemy gradienty "wstecz", od wyjścia do wejść. Używamy **reguły łańcuchowej**:

$$\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial x}$$

gdzie $y$ jest zmienną pośrednią między $L$ a $x$.

W Wikipedii można znaleźć bardzo intuicyjne wyjaśnienie tej reguły, które podaje George F. Simmons: "Jeśli samochód jedzie dwa razy szybciej niż rower, a rower cztery razy szybciej niż idący człowiek, to samochód jedzie 2 × 4 = 8 razy szybciej niż człowiek."

### 2.1 Gradient wyjściowy

$$\frac{\partial L}{\partial L} = 1$$

Gradient funkcji względem siebie samej wynosi zawsze 1. To nasz punkt startowy.

### 2.2 Gradient względem $e$

$$L = e^2 \implies \frac{\partial L}{\partial e} = 2e = 2 \cdot 4 = 8$$

### 2.3 Gradienty względem $d$ i $c$

$$e = d + c$$

Pochodna sumy po każdym składniku wynosi 1:

$$\frac{\partial e}{\partial d} = 1, \quad \frac{\partial e}{\partial c} = 1$$

Stosując regułę łańcuchową:

$$\frac{\partial L}{\partial d} = \frac{\partial L}{\partial e} \cdot \frac{\partial e}{\partial d} = 8 \cdot 1 = 8$$

$$\frac{\partial L}{\partial c} = \frac{\partial L}{\partial e} \cdot \frac{\partial e}{\partial c} = 8 \cdot 1 = 8$$

### 2.4 Gradienty względem $a$ i $b$

$$d = a \cdot b$$

Pochodna iloczynu:

$$\frac{\partial d}{\partial a} = b = -3, \quad \frac{\partial d}{\partial b} = a = 2$$

Stosując regułę łańcuchową:

$$\frac{\partial L}{\partial a} = \frac{\partial L}{\partial d} \cdot \frac{\partial d}{\partial a} = 8 \cdot (-3) = -24$$

$$\frac{\partial L}{\partial b} = \frac{\partial L}{\partial d} \cdot \frac{\partial d}{\partial b} = 8 \cdot 2 = 16$$

### Podsumowanie gradientów

| Zmienna | Gradient |
|---------|----------|
| $a$ | $-24$ |
| $b$ | $16$ |
| $c$ | $8$ |

### Interpretacja gradientów

Co nam mówią te liczby?

- **$\frac{\partial L}{\partial a} = -24$** — zwiększenie $a$ o mały $\Delta$ zmniejszy $L$ o około $24\Delta$
- **$\frac{\partial L}{\partial b} = 16$** — zwiększenie $b$ o mały $\Delta$ zwiększy $L$ o około $16\Delta$
- **$\frac{\partial L}{\partial c} = 8$** — zwiększenie $c$ o mały $\Delta$ zwiększy $L$ o około $8\Delta$

Gradient wskazuje kierunek **najszybszego wzrostu** funkcji. Jeśli chcemy **minimalizować** $L$, musimy iść w kierunku przeciwnym do gradientu.

## Krok 3: Gradient Descent

Mając gradienty, możemy zaktualizować parametry aby zmniejszyć wartość funkcji straty.

**Reguła aktualizacji:**

$$\theta_{new} = \theta_{old} - \eta \cdot \frac{\partial L}{\partial \theta}$$

gdzie $\eta$ to **learning rate** (współczynnik uczenia). Ustalamy $\eta = 0.01$.

### Obliczenia

$$a_{new} = 2 - 0.01 \cdot (-24) = 2 + 0.24 = 2.24$$

$$b_{new} = -3 - 0.01 \cdot 16 = -3 - 0.16 = -3.16$$

$$c_{new} = 10 - 0.01 \cdot 8 = 10 - 0.08 = 9.92$$

## Krok 4: Weryfikacja

Sprawdźmy, czy loss rzeczywiście zmalał:

$$d_{new} = 2.24 \cdot (-3.16) = -7.08$$

$$e_{new} = -7.08 + 9.92 = 2.84$$

$$L_{new} = 2.84^2 = 8.07$$

**Loss spadł z 16 do 8.07** ✓

Powtarzając ten proces (forward → backward → update) wielokrotnie, loss będzie dalej maleć, aż osiągnie minimum.

## Parę słów na koniec

### Dlaczego odejmujemy gradient?

Gradient wskazuje kierunek najszybszego **wzrostu** funkcji. My chcemy ją **minimalizować**, więc idziemy w przeciwnym kierunku, stąd minus w regule aktualizacji.

Intuicja: jeśli stoisz na zboczu góry i chcesz zejść w dół, idziesz w kierunku przeciwnym do najstromszego wznoszenia.

### Rola learning rate

Learning rate $\eta$ kontroluje wielkość kroku:

- **Za duży $\eta$** — możemy "przeskoczyć" minimum i oscylować lub divergować
- **Za mały $\eta$** — uczenie będzie bardzo powolne
- **W sam raz** — stabilna konwergencja do minimum

W praktyce dobór learning rate to jeden z kluczowych hiperparametrów. Nowoczesne optymalizatory (Adam, AdaGrad) adaptują go automatycznie dla każdego parametru.

### Od przykładu do sieci neuronowej

W prawdziwej sieci neuronowej mamy:
- Tysiące/miliony parametrów (wagi $w$ i biasy $b$)
- Wielowarstwowy graf obliczeniowy
- Funkcje aktywacji (ReLU, tanh, sigmoid)
- Operacje macierzowe zamiast skalarnych

Ale mechanizm jest identyczny:
1. **Forward pass** — oblicz wyjście sieci i loss
2. **Backward pass** — propaguj gradienty od loss do wszystkich wag
3. **Update** — zaktualizuj wagi w kierunku przeciwnym do gradientu
4. **Repeat** — powtarzaj aż loss będzie wystarczająco mały

## Podsumowanie

Backpropagation to eleganckie zastosowanie reguły łańcuchowej do efektywnego obliczania gradientów w grafach obliczeniowych. Kluczowe elementy:

1. **Forward pass** — oblicz wartości od wejść do wyjścia, zapamiętaj pośrednie
2. **Backward pass** — propaguj gradienty od wyjścia do wejść używając reguły łańcuchowej  
3. **Gradient descent** — zaktualizuj parametry: $\theta = \theta - \eta \cdot \nabla_\theta L$
4. **Iteracja** — powtarzaj aż do zbieżności

Ten prosty algorytm, zaimplementowany efektywnie na GPU, umożliwia trenowanie modeli o miliardach parametrów.

## Przydatne linki

- [Calculus on Computational Graphs: Backpropagation (Chris Olah)](https://colah.github.io/posts/2015-08-Backprop/)
- [Neural Networks and Deep Learning, Chapter 2 (Michael Nielsen)](http://neuralnetworksanddeeplearning.com/chap2.html)
- [CS231n: Backpropagation (Stanford)](https://cs231n.github.io/optimization-2/)

## EN