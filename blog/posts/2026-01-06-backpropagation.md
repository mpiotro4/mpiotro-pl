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

## Implementacja w PyTorch

Na **sam koniec** jeszcze jedna ciekawostka.
PyTorch (i inne frameworki deep learningowe) automatycznie obliczają gradienty za nas. Zobaczmy, jak wygląda nasz przykład w kodzie:
```python
import torch

# Definiujemy parametry jako tensory z włączonym śledzeniem gradientów
a = torch.tensor([2.0], requires_grad=True)
b = torch.tensor([-3.0], requires_grad=True)
c = torch.tensor([10.0], requires_grad=True)

# Forward pass - PyTorch buduje graf obliczeniowy automatycznie
d = a * b
e = d + c
L = e ** 2

print(f"Loss: {L.item()}")  # 16.0

# Backward pass - jeden wywołanie oblicza wszystkie gradienty
L.backward()

# Odczytujemy gradienty
print('---')
print(f'∂L/∂a = {a.grad.item()}')  # -24.0
print(f'∂L/∂b = {b.grad.item()}')  # 16.0
print(f'∂L/∂c = {c.grad.item()}')  # 8.0
```

**Wynik:**
```
Loss: 16.0
---
∂L/∂a = -24.0
∂L/∂b = 16.0
∂L/∂c = 8.0
```

Dokładnie te same wartości, które obliczyliśmy ręcznie! PyTorch wykonał za nas całą pracę: zbudował graf obliczeniowy, zapamiętał wartości pośrednie i zastosował regułę łańcuchową.

**Kluczowe elementy:**
- `requires_grad=True` – włącza śledzenie operacji dla danego tensora
- `L.backward()` – uruchamia backpropagation od zmiennej `L`
- `.grad` – zawiera obliczony gradient dla każdego parametru

Przyjrzymy się bliżej temu mechanizmowi w kolejnym wpisie, gdzie stworzymy prostą sieć neuronową od zera.

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

---
title: "Backpropagation Step by Step — A Worked Example"
date: 2025-01-06
author: "Marcin Piotrowski"
tags: ["deep learning", "backpropagation", "gradient descent", "neural networks"]
description: "A detailed walkthrough of backpropagation with manual calculations. From forward pass through backward pass all the way to the optimizer step."
---

## Introduction

Backpropagation is the algorithm that made training deep neural networks practical. The idea is straightforward: compute the derivatives of the loss function with respect to the network's parameters, telling us in which direction to nudge each one to reduce the error.

Worth noting — backpropagation is a general-purpose optimization algorithm. It works for any function built from composable operations, not just neural networks. In transformers, for example, the same mechanism trains both the network weights and the token embeddings, which are simply a table of parameters rather than a neural layer.

The best way to build real intuition for backpropagation is to work through a concrete example by hand. That's exactly what we'll do here.

## Gradient, Derivative, Partial Derivative — Quick Definitions

Before the calculations, a brief math refresher:

**Derivative** — applies to a function of one variable: $f(x)$. It describes how fast the function changes as $x$ changes. Notation: $\frac{df}{dx}$ or $f'(x)$.

**Partial derivative** — applies to a function of multiple variables: $f(x, y, z)$. It describes how the function changes with respect to **one** variable, holding the others fixed. Notation: $\frac{\partial f}{\partial x}$.

**Gradient** — a **vector** of all partial derivatives. For $f(x, y, z)$:

$$\nabla f = \left[\frac{\partial f}{\partial x}, \frac{\partial f}{\partial y}, \frac{\partial f}{\partial z}\right]$$

The gradient points in the direction of steepest ascent.

**In this post** we use "gradient" for the full vector (e.g. "compute the parameter gradients") and "partial derivative" for individual components (e.g. $\frac{\partial L}{\partial a}$).

## The Example

Consider a loss function depending on three parameters:

$$L = (a \cdot b + c)^2$$

**Input values:**

* $a = 2$
* $b = -3$  
* $c = 10$

Our goal is to compute $\frac{\partial L}{\partial a}$, $\frac{\partial L}{\partial b}$, $\frac{\partial L}{\partial c}$ — these tell us how each parameter affects the loss.

### Computational Graph

Let's break the function down into atomic operations:

```
a ──┐
    ├──[×]── d ──┐
b ──┘            ├──[+]── e ──[^2]── L
             c ──┘
```

Where:

* $d = a \cdot b$
* $e = d + c$
* $L = e^2$

Decomposing into atomic operations is key — the derivative of each individual step becomes trivial to compute.

### Step 1: Forward Pass

Compute values from inputs to output:

$$d = a \cdot b = 2 \cdot (-3) = -6$$

$$e = d + c = -6 + 10 = 4$$

$$L = e^2 = 4^2 = 16$$

We store all intermediate values — they'll be needed during the backward pass. Without them, we'd have to recompute everything from scratch.

| Variable | Value |
|----------|-------|
| $a$ | 2 |
| $b$ | -3 |
| $c$ | 10 |
| $d$ | -6 |
| $e$ | 4 |
| $L$ | 16 |

## Step 2: Backward Pass

Now we propagate gradients backwards, from output to inputs. We use the **chain rule**:

$$\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} \cdot \frac{\partial y}{\partial x}$$

where $y$ is an intermediate variable between $L$ and $x$.

A nice intuition for the chain rule comes from George F. Simmons: *"If a car travels twice as fast as a bicycle, and the bicycle travels four times as fast as a walking person, then the car travels 2 × 4 = 8 times as fast as the person."*

### 2.1 Output Gradient

$$\frac{\partial L}{\partial L} = 1$$

A function's derivative with respect to itself is always 1. This is our starting point.

### 2.2 Gradient w.r.t. $e$

$$L = e^2 \implies \frac{\partial L}{\partial e} = 2e = 2 \cdot 4 = 8$$

### 2.3 Gradients w.r.t. $d$ and $c$

$$e = d + c$$

The derivative of a sum with respect to each term is 1:

$$\frac{\partial e}{\partial d} = 1, \quad \frac{\partial e}{\partial c} = 1$$

Applying the chain rule:

$$\frac{\partial L}{\partial d} = \frac{\partial L}{\partial e} \cdot \frac{\partial e}{\partial d} = 8 \cdot 1 = 8$$

$$\frac{\partial L}{\partial c} = \frac{\partial L}{\partial e} \cdot \frac{\partial e}{\partial c} = 8 \cdot 1 = 8$$

### 2.4 Gradients w.r.t. $a$ and $b$

$$d = a \cdot b$$

Product rule:

$$\frac{\partial d}{\partial a} = b = -3, \quad \frac{\partial d}{\partial b} = a = 2$$

Applying the chain rule:

$$\frac{\partial L}{\partial a} = \frac{\partial L}{\partial d} \cdot \frac{\partial d}{\partial a} = 8 \cdot (-3) = -24$$

$$\frac{\partial L}{\partial b} = \frac{\partial L}{\partial d} \cdot \frac{\partial d}{\partial b} = 8 \cdot 2 = 16$$

### Gradient Summary

| Variable | Gradient |
|----------|----------|
| $a$ | $-24$ |
| $b$ | $16$ |
| $c$ | $8$ |

### Interpreting the Gradients

What do these numbers actually mean?

- **$\frac{\partial L}{\partial a} = -24$** — increasing $a$ by a small $\Delta$ will *decrease* $L$ by roughly $24\Delta$
- **$\frac{\partial L}{\partial b} = 16$** — increasing $b$ by a small $\Delta$ will *increase* $L$ by roughly $16\Delta$
- **$\frac{\partial L}{\partial c} = 8$** — increasing $c$ by a small $\Delta$ will *increase* $L$ by roughly $8\Delta$

The gradient points toward the **steepest ascent**. To **minimize** $L$, we move in the opposite direction.

## Step 3: Gradient Descent

With the gradients in hand, we update the parameters to reduce the loss.

**Update rule:**

$$\theta_{new} = \theta_{old} - \eta \cdot \frac{\partial L}{\partial \theta}$$

where $\eta$ is the **learning rate**. We'll use $\eta = 0.01$.

### Calculations

$$a_{new} = 2 - 0.01 \cdot (-24) = 2 + 0.24 = 2.24$$

$$b_{new} = -3 - 0.01 \cdot 16 = -3 - 0.16 = -3.16$$

$$c_{new} = 10 - 0.01 \cdot 8 = 10 - 0.08 = 9.92$$

## Step 4: Verification

Let's confirm the loss actually went down:

$$d_{new} = 2.24 \cdot (-3.16) = -7.08$$

$$e_{new} = -7.08 + 9.92 = 2.84$$

$$L_{new} = 2.84^2 = 8.07$$

**Loss dropped from 16 to 8.07** ✓

Repeating this cycle (forward → backward → update) will keep driving the loss down until it reaches a minimum.

## A Few Closing Thoughts

### Why Subtract the Gradient?

The gradient points toward the steepest **increase** of the function. Since we want to **minimize** it, we go the other way — hence the minus sign in the update rule.

Think of it like hiking: if you want to get to the bottom of a valley, you walk in the direction opposite to the steepest slope.

### The Role of Learning Rate

The learning rate $\eta$ controls the step size:

- **Too large** — you may overshoot the minimum and oscillate or diverge
- **Too small** — training becomes painfully slow
- **Just right** — stable convergence to a minimum

Choosing the right learning rate is one of the most important hyperparameter decisions in practice. Modern optimizers (Adam, AdaGrad) handle this automatically by adapting the learning rate per parameter.

### From This Example to a Real Neural Network

In a real network you have:
- Thousands or millions of parameters (weights $w$ and biases $b$)
- A deep, multi-layer computational graph
- Activation functions (ReLU, tanh, sigmoid)
- Matrix operations instead of scalars

But the mechanism is identical:
1. **Forward pass** — compute the network output and loss
2. **Backward pass** — propagate gradients from the loss back to all weights
3. **Update** — move parameters in the direction opposite to the gradient
4. **Repeat** — until the loss is small enough

## Implementation in PyTorch

One last thing — PyTorch computes all of this for us automatically. Here's our example in code:

```python
import torch

# Define parameters as tensors with gradient tracking enabled
a = torch.tensor([2.0], requires_grad=True)
b = torch.tensor([-3.0], requires_grad=True)
c = torch.tensor([10.0], requires_grad=True)

# Forward pass — PyTorch builds the computational graph automatically
d = a * b
e = d + c
L = e ** 2

print(f"Loss: {L.item()}")  # 16.0

# Backward pass — one call computes all gradients
L.backward()

# Read the gradients
print('---')
print(f'∂L/∂a = {a.grad.item()}')  # -24.0
print(f'∂L/∂b = {b.grad.item()}')  # 16.0
print(f'∂L/∂c = {c.grad.item()}')  # 8.0
```

**Output:**
```
Loss: 16.0
---
∂L/∂a = -24.0
∂L/∂b = 16.0
∂L/∂c = 8.0
```

Exactly the values we computed by hand! PyTorch handled everything: building the graph, caching intermediate values, and applying the chain rule.

**Key elements:**
- `requires_grad=True` — enables operation tracking for a tensor
- `L.backward()` — kicks off backpropagation from `L`
- `.grad` — holds the computed gradient for each parameter

We'll take a closer look at this mechanism in the next post, where we'll build a simple neural network from scratch.

## Summary

Backpropagation is an elegant application of the chain rule for efficiently computing gradients in computational graphs. The key steps:

1. **Forward pass** — compute values from inputs to output, cache intermediates
2. **Backward pass** — propagate gradients from output to inputs using the chain rule
3. **Gradient descent** — update parameters: $\theta = \theta - \eta \cdot \nabla_\theta L$
4. **Iterate** — repeat until convergence

This simple algorithm, implemented efficiently on GPUs, is what makes training models with billions of parameters possible.

## Further Reading

- [Calculus on Computational Graphs: Backpropagation (Chris Olah)](https://colah.github.io/posts/2015-08-Backprop/)
- [Neural Networks and Deep Learning, Chapter 2 (Michael Nielsen)](http://neuralnetworksanddeeplearning.com/chap2.html)
- [CS231n: Backpropagation (Stanford)](https://cs231n.github.io/optimization-2/)