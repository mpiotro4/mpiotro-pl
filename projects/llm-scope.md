---
title_pl: "LLM-Scope — wizualizacja tego, co dzieje się wewnątrz Qwen3-0.6B"
title_en: "LLM-Scope — Visualizing What Happens Inside Qwen3-0.6B"
date: 2026-09-04
author: "Marcin Piotrowski"
tags: ["LLM", "mechanistic interpretability", "PyTorch", "transformers", "attention", "visualization", "Python"]
description_pl: "Narzędzie wizualizujące krok po kroku, co dzieje się wewnątrz Qwen3-0.6B podczas czytania promptu i generowania odpowiedzi: aktywacje neuronów MLP, attention, logit lens i pełna 'podróż' pojedynczego tokenu przez wszystkie warstwy transformera."
description_en: "A tool that visualizes, step by step, what happens inside Qwen3-0.6B while it reads a prompt and generates a response: MLP neuron activations, attention, a logit lens, and a full 'token journey' through every transformer layer."
image: /static/images/projects/llm-scope/hero.png
---

## PL

Duże modele językowe zwykle traktuje się jak czarną skrzynkę — prompt wchodzi, tekst wychodzi, a to, co dzieje się pomiędzy, zostaje w środku. **LLM-Scope** to próba otwarcia tej skrzynki na żywym, ale wystarczająco małym modelu (Qwen3-0.6B, 28 warstw, 0,6 mld parametrów), żeby dało się go w całości podłączyć hookami i pokazać dosłownie każdą liczbę, która realnie powstaje w trakcie liczenia: aktywacje neuronów, wagi attention, pośrednie predykcje na każdej głębokości i pełną drogę pojedynczego tokenu przez sieć.

Żywa wersja: **[mpiotro4.github.io/LLM-Scope](https://mpiotro4.github.io/LLM-Scope/)** (self-contained HTML, przechwycony na promptcie "The capital of France is") — kod: **[github.com/mpiotro4/LLM-Scope](https://github.com/mpiotro4/LLM-Scope)**.

<img alt="Widok aplikacji: baner statycznego demo, pasek kontrolek, tekst promptu z podświetlonym attention na 'capital' i 'France' podczas generowania tokenu 'Paris', oraz lista zwiniętych paneli poniżej" src="/static/images/projects/llm-scope/hero.png" width="800"/>

Każdy panel jest osobno zwijalny i ma własny przycisk **ⓘ** z dłuższym wyjaśnieniem — całą resztę tego wpisu można też po prostu kliknąć samodzielnie na żywym demie.

## Heatmapa aktywacji neuronów

Model ma 28 warstw, a każda kończy swoje obliczenia szeroką siecią feedforward (SwiGLU MLP) z 3072 "neuronami". Heatmapa pokazuje, jak mocno każdy z nich zapalił się dla aktualnie wybranego tokenu — wiersz to warstwa, kolumna to neuron, jasność to `|aktywacja|`.

<img alt="Heatmapa aktywacji: 28 wierszy (warstwy) na 3072 kolumny (neurony), jasne piksele na ciemnym tle" src="/static/images/projects/llm-scope/neuron-heatmap.png" width="800"/>

Dwie rzeczy, które trzeba było rozwiązać, żeby to w ogóle było czytelne:

- **Skala.** Kilka neuronów w każdej warstwie potrafi mieć wartości o rząd wielkości większe od reszty ("massive activations" — dobrze udokumentowane zjawisko w dużych modelach). Normalizacja po maksimum zgasiłaby wtedy wszystko poza tą garstką outlierów. Zamiast tego każda warstwa jest przycinana do swojego 99. percentyla i dodatkowo pierwiastkowana (sqrt-compression), żeby skompresować dynamikę bez utraty słabszych sygnałów.
- **Kolejność neuronów.** Ukryte jednostki MLP nie mają żadnego naturalnego porządku (permutation symmetry) — kolejność "z modelu" jest wizualnie czystym szumem. `compute_neuron_order.py` liczy raz, offline, stabilny porządek przez hierarchiczne klastrowanie korelacji aktywacji na zbiorze różnorodnych promptów, co odsłania sąsiadujące, skorelowane neurony zamiast losowego mieszania.

## Attention

Kliknięcie dowolnego tokenu w tekście podświetla różowym kolorem wcześniejsze tokeny proporcjonalnie do tego, ile uwagi im poświęcił (uśrednione po 16 głowach attention, albo pojedyncza wybrana warstwa). Panel **Attention Lens** poniżej pokazuje ten sam wiersz w pełnej rozdzielczości: wiersz = wcześniejszy token, kolumna = warstwa (0–27), jasność = waga uwagi.

<img alt="Attention Lens w trybie heatmap: etykiety tokenów po lewej, siatka 28 kolumn (warstwy), jasne pasma pokazujące gdzie token 'Paris' kieruje uwagę" src="/static/images/projects/llm-scope/attention-lens.png" width="800"/>

Ciekawostka implementacyjna: dlaczego dokładnie **jeden** kwadracik na warstwę, a nie np. jeden na głowę? Bo 16 głów attention jest uśrednianych już w momencie przechwytywania, w Pythonie, zanim cokolwiek trafi do danych wysyłanych do przeglądarki — więc dla danej warstwy istnieje dokładnie jedna liczba na parę (wcześniejszy token, waga). Rozdzielczość per-głowę jest bezpowrotnie tracona na tym etapie; front-end nigdy jej nie widzi. Z tego samego powodu selektor warstwy w kontrolkach panelu **nie wpływa** na tryb heatmap (który zawsze pokazuje wszystkie 28 warstw naraz) — działa tylko w trybie kolumnowym i na podświetleniu tekstu.

Osobny smaczek: pierwszy token sekwencji regularnie zgarnia nieproporcjonalnie dużo uwagi na każdej warstwie — to znane zjawisko "attention sink". Zostawiony jako punkt odniesienia zgasiłby resztę skali do czerni, więc jest wyłączony z normalizacji (ale nadal renderowany z pełną intensywnością) — a checkbox **skip sink** potrafi ukryć go z tego panelu całkowicie i przeliczyć skalę na nowo względem reszty.

Uwaga wymaga wag, których szybki domyślny kernel (`sdpa`) nigdy jawnie nie liczy — model trzeba załadować z `attn_implementation="eager"`, co kosztuje około 8–9× więcej czasu na token.

## Logit lens

Na każdej głębokości — wyjście embeddingu ("warstwa -1") i wyjście każdego z 28 bloków transformera — strumień rezydualny jest rzutowany przez finalną normalizację i `lm_head` modelu, tak jakby sieć skończyła liczyć właśnie tutaj. To pozwala podejrzeć, co model "sądzi" na długo przed faktycznym końcem obliczeń.

<img alt="Logit lens w trybie kolumnowym: sparkline entropii u góry, lista głębokości od -1 do 27 z top-1 tokenem i jego prawdopodobieństwem, słupki zmieniające się od niepewnych wczesnych warstw do bardzo pewnych późnych" src="/static/images/projects/llm-scope/logit-lens.png" width="800"/>

To tylko przybliżenie dla warstw pośrednich — strumień rezydualny nie jest wyrażony w bazie, w której działa `lm_head`, aż do ostatniej warstwy, więc rzutowanie wcześniejszych głębokości przez tę samą macierz to heurystyka, nie coś, do czego model był trenowany. W praktyce widać dokładnie ten wzorzec: wczesne warstwy zgadują coś generycznego albo wprost bez sensu, a predykcja "zaskakuje" w miejsce dopiero na pewnej głębokości i już tam zostaje — obserwowanie *gdzie* dokładnie to się dzieje jest samo w sobie interesujące.

## Token Journey

Panel prowadzący pojedynczy, aktualnie wybrany token przez cały pipeline, od góry do dołu: **tokenizacja** (tekst → ID w słowniku) → **wektor embeddingu** → wnętrze jednego **bloku transformera** (z własnym stepperem warstw, niezależnym od reszty paneli) → **wektor wyjściowy** → **predykcja** → **detokenizacja**.

<img alt="Token Journey: pełny pipeline dla tokenu Paris — tokenizacja, wektor embeddingu, wnętrze bloku transformera z formułami RMSNorm/Q-K-V/RoPE, top attended tokens, aktywacje MLP, residual OUT, wektor wyjściowy, predykcja top-5 i detokenizacja" src="/static/images/projects/llm-scope/token-journey.png" width="600"/>

Pomarańczowe, wypełnione ramki trzymają realne przechwycone wartości tego tokenu (te same liczby co w panelach powyżej, plus same wektory embeddingu/residual/wyjściowy jako małe paski-heatmapy). Przerywane ramki to schematyczne diagramy wnętrza, którego ta aplikacja nigdy nie przechwytuje ani nie przesyła — surowe wektory Q/K/V, kąty RoPE, wyniki przed softmaxem — pokazane jako sam wzór/kształt, nigdy jako zmyślone liczby.

1024-wymiarowy wektor pokazany jako "residual IN" / "residual OUT" / wektor embeddingu / wektor wyjściowy to dosłownie ta sama, płynąca wielkość na każdym etapie — OUT jednej warstwy jest bajt w bajt identyczny z IN kolejnej, od embedding lookupu aż po finalny wektor wyjściowy. Przełączanie warstw własnymi strzałkami bloku transformera widocznie odkształca ten jeden wektor, gdy przechodzi przez wszystkie 28 warstw.

## Dwa tryby: offline i live

Cała logika przechwytywania (ładowanie modelu, hooki, pętla generacji, logit lens) siedzi w jednym module i jest współdzielona przez dwa niezależne wejścia:

- **Offline replay** (`capture.py`) — puszcza jeden prompt przez model i zapisuje cały przebieg jako samodzielny plik HTML, który można otworzyć offline i przewijać klatka po klatce. Współdzielony CSS/JS ze `static/` jest wklejany bezpośrednio do pliku, więc wynik to jeden plik bez żadnych zewnętrznych zależności — to właśnie ten plik ląduje na GitHub Pages.
- **Live** (`server.py`) — trzyma model w pamięci i streamuje aktywność przez Server-Sent Events, w miarę jak wpisuje się kolejne prompty. Jedna instancja modelu obsługuje jedno żądanie naraz (prosty globalny lock) — wystarczające do użytku lokalnego/osobistego, nie do wielu użytkowników naraz.

## Wdrożenie i CI/CD

Wersja online (ten link u góry) nie jest ręcznie odświeżanym zrzutem — GitHub Action buduje ją od nowa **przy każdym pushu na `main`**: instaluje zależności, ściąga i cache'uje Qwen3-0.6B (~1,2 GB, tylko raz), odpala `capture.py` na CI-owym runnerze i publikuje wynikowy HTML na GitHub Pages przez oficjalny `actions/deploy-pages`. Nic nie wraca do repo jako commit — wygenerowany plik żyje wyłącznie jako deployment Pages, więc historia gita się nie zapycha kolejnymi wersjami tego samego kilkumegabajtowego pliku.

## Stack technologiczny

- **PyTorch** + **Transformers** (`AutoModelForCausalLM`/`AutoTokenizer`) — ładowanie modelu, forward hooki na `down_proj` każdej warstwy (przechwytują aktywacje MLP) i na wyjściu każdego bloku (przechwytują residual stream)
- **FastAPI** + Server-Sent Events — tryb live
- Czysty **JavaScript + Canvas**, bez frameworka — świadomy wybór, żeby offline output mógł zostać jednym plikiem HTML bez etapu budowania
- **NumPy / SciPy / Pillow** — klastrowanie kolejności neuronów i skrypt weryfikacyjny
- **GitHub Actions** — CI/CD do GitHub Pages

## Ograniczenia

- Attention wymaga `attn_implementation="eager"`, ~8–9× wolniejszego niż domyślny szybki kernel — cena za wyciągnięcie wag, których model normalnie nigdy jawnie nie materializuje.
- Logit lens dla warstw pośrednich to heurystyka, nie ścisła interpretacja (patrz wyżej) — tylko najgłębsza warstwa jest gwarantowanie zgodna z faktyczną predykcją modelu.
- Twardy limit 300 nowych tokenów (model i tak zwykle trafia w EOS wcześniej) — każda klatka niesie ciężki payload (aktywacje + attention + logit lens), więc otwarty limit ryzykowałby wielogigabajtowy plik HTML albo bardzo długi stream.
- `server.py` obsługuje jedno żądanie generacji naraz — nie jest to hosting wieloużytkownikowy.
- Kolejność neuronów w heatmapie jest arbitralna, dopóki nie uruchomi się raz `compute_neuron_order.py`.

## Źródła

- [Repozytorium projektu](https://github.com/mpiotro4/LLM-Scope)
- [Żywe demo (GitHub Pages)](https://mpiotro4.github.io/LLM-Scope/)
- [Qwen/Qwen3-0.6B na Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)

## EN

Large language models are usually treated as a black box — a prompt goes in, text comes out, and whatever happens in between stays inside. **LLM-Scope** is an attempt to open that box on a real but small enough model (Qwen3-0.6B, 28 layers, 0.6B parameters) to fully instrument it with hooks and show, quite literally, every number that actually gets computed along the way: neuron activations, attention weights, intermediate predictions at every depth, and the complete path a single token takes through the network.

Live version: **[mpiotro4.github.io/LLM-Scope](https://mpiotro4.github.io/LLM-Scope/)** (a self-contained HTML file, captured on the prompt "The capital of France is") — code: **[github.com/mpiotro4/LLM-Scope](https://github.com/mpiotro4/LLM-Scope)**.

<img alt="App overview: the static-demo banner, playback controls, the prompt text with attention highlighting 'capital' and 'France' while generating the token 'Paris', and the list of collapsed panels below" src="/static/images/projects/llm-scope/hero.png" width="800"/>

Every panel is independently collapsible and has its own **ⓘ** button with a longer explanation — the rest of this write-up doubles as a walkthrough you can click through yourself on the live demo.

## Neuron activation heatmap

The model has 28 layers, and each one ends its computation with a wide feed-forward network (a SwiGLU MLP) of 3072 "neurons." The heatmap shows how strongly each one fired for the currently selected token — row = layer, column = neuron, brightness = `|activation|`.

<img alt="Activation heatmap: 28 rows (layers) by 3072 columns (neurons), bright pixels on a dark background" src="/static/images/projects/llm-scope/neuron-heatmap.png" width="800"/>

Two things had to be solved to make this actually legible:

- **Scale.** A handful of neurons in every layer can have values an order of magnitude larger than the rest ("massive activations" — a well-documented phenomenon in large models). Normalizing by the maximum would crush everything else to black. Instead, each layer is clipped to its own 99th percentile and additionally sqrt-compressed, squeezing the dynamic range without losing the weaker signal.
- **Neuron order.** MLP hidden units have no inherent ordering (permutation symmetry) — the model's native order is visually pure noise. `compute_neuron_order.py` computes a stable order once, offline, via correlation-based hierarchical clustering over a diverse prompt corpus, surfacing neighboring, correlated neurons instead of a random shuffle.

## Attention

Clicking any token in the text washes earlier tokens in pink, proportional to how much attention that token paid them (averaged over all 16 attention heads, or a single chosen layer). The **Attention Lens** panel below shows the same row at full resolution: row = earlier token, column = layer (0–27), brightness = attention weight.

<img alt="Attention Lens in heatmap mode: token labels on the left, a 28-column grid (layers), bright bands showing where the token 'Paris' directs its attention" src="/static/images/projects/llm-scope/attention-lens.png" width="800"/>

An implementation detail worth calling out: why exactly **one** cell per layer, rather than, say, one per head? Because the 16 attention heads are already averaged together in Python at capture time, before anything reaches the data sent to the browser — so for a given layer there is exactly one number per (earlier token, weight) pair. Per-head resolution is thrown away irreversibly at that stage; the front-end never sees it. For the same reason, the layer selector in the panel's controls has **no effect** on heatmap mode (which always shows all 28 layers at once) — it only matters in column mode and for the text overlay.

A separate quirk: the very first token in a sequence routinely soaks up a disproportionate share of attention at every layer — the well-documented "attention sink" phenomenon. Left in as a reference point it would crush the rest of the scale to near-invisible, so it's excluded from normalization (while still rendering at full intensity itself) — and a **skip sink** checkbox can hide it from this panel entirely and rescale against what's left.

Attention requires weights the fast default kernel (`sdpa`) never computes explicitly — the model has to be loaded with `attn_implementation="eager"` instead, which costs roughly 8–9x more time per token.

## Logit lens

At every depth — the embedding output ("layer -1") and the output of each of the 28 transformer blocks — the residual stream is projected through the model's own final norm and `lm_head`, as if the network had stopped computing right there. It's a way to eavesdrop on what the model "believes" long before it's actually done.

<img alt="Logit lens in column mode: an entropy sparkline at the top, a list of depths from -1 to 27 with the top-1 token and its probability, bars going from uncertain early layers to very confident late ones" src="/static/images/projects/llm-scope/logit-lens.png" width="800"/>

This is only an approximation for intermediate layers — the residual stream isn't expressed in the basis `lm_head` operates in until the final layer, so projecting earlier depths through that same matrix is a heuristic, not something the model was trained to support. In practice you see exactly that pattern: early layers guess something generic or plainly wrong, and the prediction "locks in" at some depth and stays there — watching exactly *where* that happens is interesting in its own right.

## Token Journey

A panel that walks the single, currently-selected token through the whole pipeline, top to bottom: **tokenization** (text → vocabulary ID) → **embedding vector** → the internals of one **transformer block** (with its own layer stepper, independent of every other panel) → **output vector** → **prediction** → **detokenization**.

<img alt="Token Journey: the full pipeline for the token Paris — tokenization, embedding vector, transformer block internals with RMSNorm/Q-K-V/RoPE formulas, top attended tokens, MLP activations, residual OUT, output vector, top-5 prediction and detokenization" src="/static/images/projects/llm-scope/token-journey.png" width="600"/>

Solid amber boxes hold this token's actual captured values (the same numbers as the panels above, plus the embedding/residual/output vectors themselves as small heatmap strips). Dashed boxes are schematic diagrams of internals this app never captures or transmits — raw Q/K/V vectors, RoPE angles, pre-softmax scores — shown as their formula/shape only, never invented numbers.

The 1024-dim vector shown as "residual IN" / "residual OUT" / the embedding vector / the output vector is literally the same running quantity at every stage — one layer's OUT is byte-identical to the next layer's IN, all the way from the embedding lookup to the final output vector. Stepping through layers with the transformer block's own arrows visibly morphs this one vector as it passes through all 28 layers.

## Two modes: offline and live

All the capture logic (model loading, hooks, the generation loop, the logit lens) lives in one module shared by two independent entry points:

- **Offline replay** (`capture.py`) — runs one prompt through the model and writes the whole run out as a single self-contained HTML file you can open offline and scrub through frame by frame. The shared CSS/JS from `static/` is inlined directly into the file, so the output is one dependency-free file — this is exactly the file that ends up on GitHub Pages.
- **Live** (`server.py`) — keeps the model resident in memory and streams activity over Server-Sent Events as you type prompts. One model instance serves one request at a time (a simple global lock) — fine for local/personal use, not for concurrent multi-user hosting.

## Deployment and CI/CD

The online version (the link at the top) isn't a manually refreshed snapshot — a GitHub Action rebuilds it from scratch **on every push to `main`**: it installs dependencies, downloads and caches Qwen3-0.6B (~1.2 GB, once), runs `capture.py` on a CI runner, and publishes the resulting HTML to GitHub Pages through the official `actions/deploy-pages`. Nothing is committed back to the repo — the generated file lives only as the Pages deployment, so the git history doesn't accumulate yet another copy of the same multi-megabyte file on every refresh.

## Tech stack

- **PyTorch** + **Transformers** (`AutoModelForCausalLM`/`AutoTokenizer`) — model loading, forward hooks on every layer's `down_proj` (capturing MLP activations) and on each block's output (capturing the residual stream)
- **FastAPI** + Server-Sent Events — the live mode
- Plain **JavaScript + Canvas**, no framework — a deliberate choice so the offline output can stay a single HTML file with no build step
- **NumPy / SciPy / Pillow** — neuron-order clustering and the verification script
- **GitHub Actions** — CI/CD to GitHub Pages

## Limitations

- Attention requires `attn_implementation="eager"`, roughly 8–9x slower than the default fast kernel — the cost of extracting weights the model never normally materializes explicitly.
- The logit lens is a heuristic for intermediate layers, not a strict interpretation (see above) — only the deepest layer is guaranteed to match the model's actual prediction.
- A hard cap of 300 new tokens (the model usually hits EOS well before that anyway) — each frame carries a heavy payload (activations + attention + logit lens), so an open-ended limit would risk a multi-gigabyte HTML file or a very long stream.
- `server.py` serves one generation request at a time — this is not multi-user hosting.
- Neuron order in the heatmap is arbitrary until `compute_neuron_order.py` has been run once.

## References

- [Project repository](https://github.com/mpiotro4/LLM-Scope)
- [Live demo (GitHub Pages)](https://mpiotro4.github.io/LLM-Scope/)
- [Qwen/Qwen3-0.6B on Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)
