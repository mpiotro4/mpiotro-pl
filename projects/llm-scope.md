---
title_pl: "LLM-Scope — wizualizacja tego, co dzieje się wewnątrz Qwen3-0.6B"
title_en: "LLM-Scope — Visualizing What Happens Inside Qwen3-0.6B"
date: 2026-09-04
author: "Marcin Piotrowski"
tags: ["LLM", "mechanistic interpretability", "PyTorch", "transformers", "attention", "visualization", "Python"]
description_pl: "Narzędzie, które klatka po klatce — jedna klatka to jeden token — pokazuje, co dzieje się wewnątrz Qwen3-0.6B podczas czytania promptu i generowania odpowiedzi: aktywacje neuronów MLP, attention, logit lens i pełną 'podróż' pojedynczego tokenu przez wszystkie warstwy transformera."
description_en: "A tool that shows, frame by frame — one frame per token — what happens inside Qwen3-0.6B while it reads a prompt and generates a response: MLP neuron activations, attention, a logit lens, and a full 'token journey' through every transformer layer."
image: /static/images/projects/llm-scope/hero.png
---

## PL

Duże modele językowe zwykle traktuje się jak czarną skrzynkę: prompt wchodzi, tekst wychodzi, a to, co dzieje się pomiędzy, zostaje w środku. **LLM-Scope** otwiera tę skrzynkę na modelu prawdziwym, ale na tyle małym, że da się go oprzyrządować w całości — Qwen3-0.6B, 28 warstw. Aplikacja pokazuje każdą liczbę, która realnie powstaje po drodze: aktywacje neuronów, wagi attention, pośrednie predykcje na każdej głębokości i pełną drogę pojedynczego tokenu przez sieć.

Żywa wersja: **[mpiotro4.github.io/LLM-Scope](https://mpiotro4.github.io/LLM-Scope/)** (self-contained HTML, przechwycony na promptcie "The capital of France is") — kod: **[github.com/mpiotro4/LLM-Scope](https://github.com/mpiotro4/LLM-Scope)**.

<img alt="Widok aplikacji: baner statycznego demo, pasek kontrolek, tekst promptu z podświetlonym attention na 'capital' i 'France' podczas generowania tokenu 'Paris', oraz lista zwiniętych paneli poniżej" src="/static/images/projects/llm-scope/hero.png" width="800"/>

Każdy panel jest osobno zwijalny i ma własny przycisk **ⓘ** z dłuższym wyjaśnieniem — całą resztę tego wpisu można też po prostu kliknąć samodzielnie na żywym demie.

## Jak się tego używa

Wpisujesz prompt, model generuje odpowiedź, a aplikacja odtwarza całość jako **klatki: jedna klatka to jeden token**. Klatki można przewijać strzałkami, puścić jak animację i regulować tempo — najpierw widać fazę czytania promptu, potem generowanie kolejnych tokenów.

Kluczowe jest to, że wszystkie panele dzielą jedno zaznaczenie. Klik w dowolny token w tekście przestawia jednocześnie heatmapę, attention, logit lens i Token Journey na tę samą pozycję, więc zawsze patrzy się na ten sam moment obliczeń z czterech różnych stron.

## Heatmapa aktywacji neuronów

Model ma 28 warstw, a każda kończy swoje obliczenia szeroką siecią feedforward (SwiGLU MLP) z 3072 "neuronami". Heatmapa pokazuje, jak mocno każdy z nich zapalił się dla aktualnie wybranego tokenu — wiersz to warstwa, kolumna to neuron, jasność to `|aktywacja|`.

<img alt="Heatmapa aktywacji: 28 wierszy (warstwy) na 3072 kolumny (neurony), jasne piksele na ciemnym tle" src="/static/images/projects/llm-scope/neuron-heatmap.png" width="800"/>

Dwie rzeczy, które trzeba było rozwiązać, żeby to w ogóle było czytelne:

- **Skala.** Kilka neuronów w każdej warstwie potrafi mieć wartości o rząd wielkości większe od reszty ("massive activations" — dobrze udokumentowane zjawisko w dużych modelach). Normalizacja po maksimum zgasiłaby wtedy wszystko poza tą garstką outlierów. Zamiast tego każda warstwa jest przycinana do swojego 99. percentyla i dodatkowo pierwiastkowana, co ściska dynamikę bez gubienia słabszych sygnałów.
- **Kolejność neuronów.** Ukryte jednostki MLP nie mają żadnego naturalnego porządku (permutation symmetry) — kolejność "z modelu" jest wizualnie czystym szumem. `compute_neuron_order.py` liczy raz, offline, stabilny porządek przez hierarchiczne klastrowanie korelacji aktywacji na zbiorze różnorodnych promptów, dzięki czemu skorelowane neurony lądują obok siebie. W interfejsie przełącza się to selektorem `order`: `raw`, `clustered` albo `by mean`.

Warto od razu powiedzieć, czego ta heatmapa nie robi: przy 3072 kolumnach upchniętych w szerokość okna pojedynczy neuron zajmuje ułamek piksela. Świetnie widać ogólny wzór i różnice między warstwami, ale konkretnego neuronu się z niej nie odczyta — od tego jest lista top-k w Token Journey.

## Attention

Kliknięcie dowolnego tokenu w tekście podświetla różowym kolorem wcześniejsze tokeny proporcjonalnie do tego, ile uwagi im poświęcił (uśrednione po 16 głowicach attention albo dla pojedynczej wybranej warstwy). Panel **Attention Lens** poniżej pokazuje ten sam wiersz w pełnej rozdzielczości: wiersz = wcześniejszy token, kolumna = warstwa (0–27), jasność = waga uwagi.

<img alt="Attention Lens w trybie heatmap: etykiety tokenów po lewej, siatka 28 kolumn (warstwy), jasne pasma pokazujące gdzie token 'Paris' kieruje uwagę" src="/static/images/projects/llm-scope/attention-lens.png" width="800"/>

Ciekawostka implementacyjna: dlaczego dokładnie **jeden** kwadracik na warstwę, a nie jeden na głowicę? Bo 16 głowic jest uśrednianych już w momencie przechwytywania, po stronie Pythona, zanim cokolwiek trafi do danych wysyłanych do przeglądarki. Dla danej warstwy istnieje więc dokładnie jedna liczba na wcześniejszy token, a rozdzielczość per-głowica jest na tym etapie bezpowrotnie tracona — front-end nigdy jej nie widzi. Z tego samego powodu selektor warstwy **nie wpływa** na tryb heatmap, który zawsze pokazuje wszystkie 28 warstw naraz; działa tylko w trybie kolumnowym i na podświetleniu tekstu.

Drugi smaczek: pierwszy token sekwencji regularnie zgarnia nieproporcjonalnie dużo uwagi na każdej warstwie — to znane zjawisko "attention sink". Zostawiony jako punkt odniesienia zgasiłby resztę skali do czerni, więc jest wyłączony z normalizacji, choć nadal renderuje się z pełną intensywnością. Checkbox **skip sink** ukrywa go z panelu całkowicie i przelicza skalę względem reszty — różnica jest drastyczna. Przy generowaniu tokenu "Paris" bez tej opcji wszystko wygląda na równie ciemne; po jej włączeniu widać, że model patrzy przede wszystkim na "France" i "capital", czyli dokładnie tam, gdzie powinien.

Podgląd attention wymaga wag, których szybki domyślny kernel (`sdpa`) nigdy jawnie nie liczy — model trzeba załadować z `attn_implementation="eager"`, co kosztuje około 8–9× więcej czasu na token.

## Logit lens

Na każdej głębokości — wyjście embeddingu ("warstwa -1") i wyjście każdego z 28 bloków transformera — strumień rezydualny jest rzutowany przez finalną normalizację i `lm_head` modelu, tak jakby sieć skończyła liczyć właśnie tutaj. To pozwala podejrzeć, co model "sądzi" na długo przed faktycznym końcem obliczeń.

<img alt="Logit lens w trybie kolumnowym: sparkline entropii u góry, lista głębokości od -1 do 27 z top-1 tokenem i jego prawdopodobieństwem, słupki zmieniające się od niepewnych wczesnych warstw do bardzo pewnych późnych" src="/static/images/projects/llm-scope/logit-lens.png" width="800"/>

Dla warstw pośrednich to tylko przybliżenie: strumień rezydualny nie jest wyrażony w bazie, w której działa `lm_head`, aż do ostatniej warstwy, więc rzutowanie wcześniejszych głębokości przez tę samą macierz to heurystyka, a nie coś, do czego model był trenowany.

W praktyce widać dokładnie ten wzorzec. Dla promptu "The capital of France is" predykcja kolejnego tokenu po "Paris" jest przez pierwsze dwadzieścia warstw właściwie przypadkowa — pojawiają się tam urywki w rodzaju "ous" czy przecinek — a od warstwy 21 zatrzaskuje się na `**` (zamknięcie pogrubienia) z pewnością 96–99% i już się nie zmienia. Obserwowanie, *gdzie* dokładnie następuje ten moment, jest samo w sobie interesujące.

Na samej górze listy widać jeszcze jeden artefakt: na głębokości -1, czyli tuż po embeddingu, model "przewiduje" po prostu ten sam token, który właśnie czyta. To nie błąd — Qwen3 ma związane wagi embeddingu i `lm_head` (`lm_head.weight` to dosłownie ten sam tensor co `embed_tokens.weight`), więc rzutowanie świeżego embeddingu z powrotem przez tę macierz najmocniej trafia w niego samego.

Generacja jest zachłanna — czysty argmax, bez samplingu. To celowe: dzięki temu najgłębszy wiersz logit lens wykonuje dokładnie to samo obliczenie, co sam model, i zgadza się z jego wyjściem co do bitu. Sampling wprowadziłby szum, który zaciemniłby to, co ten panel ma pokazywać.

## Token Journey

Panel prowadzący pojedynczy, aktualnie wybrany token przez cały pipeline, od góry do dołu: **tokenizacja** (tekst → ID w słowniku) → **wektor embeddingu** → wnętrze jednego **bloku transformera** (z własnym stepperem warstw, niezależnym od reszty paneli) → **wektor wyjściowy** → **predykcja** → **detokenizacja**.

<img alt="Token Journey: pełny pipeline dla tokenu Paris — tokenizacja, wektor embeddingu, wnętrze bloku transformera z formułami RMSNorm/Q-K-V/RoPE, top attended tokens, aktywacje MLP, residual OUT, wektor wyjściowy, predykcja top-5 i detokenizacja" src="/static/images/projects/llm-scope/token-journey.png" width="600"/>

Cały panel trzyma się jednej zasady: **nigdy nie pokazuje liczby, której nie przechwycił**. Pomarańczowe, wypełnione ramki to realne wartości tego tokenu — te same liczby co w panelach powyżej, plus same wektory embeddingu, residual i wyjściowy jako małe paski-heatmapy. Ramki przerywane to schematy tego, czego aplikacja nie zapisuje ani nie przesyła: surowych wektorów Q/K/V, kątów RoPE, wyników przed softmaxem. Widać tam wzór i kształt tensora, ale nigdy zmyśloną liczbę.

Drobiazg, który łatwo przeoczyć, a który panel podaje poprawnie: w Qwen3 wymiar pojedynczej głowicy (128) nie wynika z podziału `hidden_size` przez liczbę głowic, bo to dałoby 1024/16 = 64. Projekcja Q wychodzi więc **szersza niż sam strumień rezydualny** — 16 × 128 = 2048 wobec 1024. Większość materiałów wyjaśniających transformery milcząco zakłada tu ten podział i podaje złe kształty.

1024-wymiarowy wektor pokazany jako "residual IN", "residual OUT", wektor embeddingu i wektor wyjściowy to na każdym etapie ta sama płynąca wielkość — OUT jednej warstwy jest identyczny z IN kolejnej, od embedding lookupu aż po finalny wektor wyjściowy. Przeskakując warstwy strzałkami bloku transformera, widać, jak ten jeden wektor stopniowo się odkształca, przechodząc przez wszystkie 28 warstw.

## Dwa tryby: offline i live

Cała logika przechwytywania (ładowanie modelu, hooki, pętla generacji, logit lens) siedzi w jednym module i jest współdzielona przez dwa niezależne wejścia:

- **Offline replay** (`capture.py`) — puszcza jeden prompt przez model i zapisuje cały przebieg jako samodzielny plik HTML, który można otworzyć offline i przewijać klatka po klatce. Współdzielony CSS/JS ze `static/` jest wklejany bezpośrednio do pliku, więc wynik to jeden plik bez żadnych zewnętrznych zależności — to właśnie ten plik ląduje na GitHub Pages.
- **Live** (`server.py`) — trzyma model w pamięci i streamuje aktywność przez Server-Sent Events, w miarę jak wpisuje się kolejne prompty. Jedna instancja modelu obsługuje jedno żądanie naraz (prosty globalny lock) — wystarczające do użytku lokalnego, nie do wielu użytkowników naraz.

## Wdrożenie i CI/CD

Wersja online (ten link u góry) nie jest ręcznie odświeżanym zrzutem — GitHub Action buduje ją od nowa **przy każdym pushu na `main`**: instaluje zależności, ściąga i cache'uje Qwen3-0.6B (~1,2 GB, tylko raz), odpala `capture.py` na CI-owym runnerze i publikuje wynikowy HTML na GitHub Pages przez oficjalny `actions/deploy-pages`. Nic nie wraca do repo jako commit — wygenerowany plik żyje wyłącznie jako deployment Pages, więc historia gita nie puchnie od kolejnych wersji tego samego kilkumegabajtowego pliku.

## Stack technologiczny

- **PyTorch** + **Transformers** (`AutoModelForCausalLM`/`AutoTokenizer`) — ładowanie modelu, forward hooki na `down_proj` każdej warstwy (przechwytują aktywacje MLP) i na wyjściu każdego bloku (przechwytują residual stream)
- **FastAPI** + Server-Sent Events — tryb live
- Czysty **JavaScript + Canvas**, bez frameworka — świadomy wybór, żeby offline output mógł zostać jednym plikiem HTML bez etapu budowania
- **NumPy / SciPy / Pillow** — klastrowanie kolejności neuronów i skrypt weryfikacyjny
- **pytest** — testy, w tym golden test pilnujący, żeby pipeline liczbowy nie zaczął po cichu zwracać czegoś innego
- **GitHub Actions** — CI/CD do GitHub Pages

## Ograniczenia

- Attention wymaga `attn_implementation="eager"`, ~8–9× wolniejszego niż domyślny szybki kernel — to cena za wyciągnięcie wag, których model normalnie nigdy jawnie nie materializuje.
- Logit lens dla warstw pośrednich to heurystyka, nie ścisła interpretacja (patrz wyżej) — zgodność z faktyczną predykcją modelu jest gwarantowana tylko dla najgłębszej warstwy.
- Heatmapa upycha 3072 kolumny w szerokość okna, więc pojedynczego neuronu nie da się w niej odczytać — pokazuje wzór, nie konkret.
- Wagi attention są uśredniane po głowicach już przy przechwytywaniu, więc struktura pojedynczych głowic jest niedostępna.
- Twardy limit 300 nowych tokenów (model i tak zwykle trafia w EOS wcześniej) — każda klatka niesie ciężki payload (aktywacje + attention + logit lens), więc otwarty limit ryzykowałby wielogigabajtowy plik HTML albo bardzo długi stream.
- `server.py` obsługuje jedno żądanie generacji naraz — to nie jest hosting wieloużytkownikowy.
- Kolejność neuronów w heatmapie jest arbitralna, dopóki nie uruchomi się raz `compute_neuron_order.py`.
- To narzędzie do obserwacji, nie do interwencji — nie da się w nim wyciszyć neuronu ani przyciąć attention i zobaczyć, jak zmieni się wyjście.

## Źródła

- [Repozytorium projektu](https://github.com/mpiotro4/LLM-Scope)
- [Żywe demo (GitHub Pages)](https://mpiotro4.github.io/LLM-Scope/)
- [Qwen/Qwen3-0.6B na Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)

## EN

Large language models are usually treated as a black box: a prompt goes in, text comes out, and whatever happens in between stays inside. **LLM-Scope** opens that box on a model that's real but small enough to instrument end to end — Qwen3-0.6B, 28 layers. It shows every number that actually gets computed along the way: neuron activations, attention weights, intermediate predictions at every depth, and the complete path a single token takes through the network.

Live version: **[mpiotro4.github.io/LLM-Scope](https://mpiotro4.github.io/LLM-Scope/)** (a self-contained HTML file, captured on the prompt "The capital of France is") — code: **[github.com/mpiotro4/LLM-Scope](https://github.com/mpiotro4/LLM-Scope)**.

<img alt="App overview: the static-demo banner, playback controls, the prompt text with attention highlighting 'capital' and 'France' while generating the token 'Paris', and the list of collapsed panels below" src="/static/images/projects/llm-scope/hero.png" width="800"/>

Every panel is independently collapsible and has its own **ⓘ** button with a longer explanation — the rest of this write-up doubles as a walkthrough you can click through yourself on the live demo.

## How you actually use it

You type a prompt, the model generates a response, and the app replays the whole thing as **frames — one frame per token**. You can step through them, hit play to watch it animate, and adjust the speed; first comes the prompt-reading phase, then token-by-token generation.

The key part is that every panel shares one selection. Clicking any token in the text moves the heatmap, attention, logit lens and Token Journey to that same position at once, so you're always looking at a single moment of computation from four different angles.

## Neuron activation heatmap

The model has 28 layers, and each one ends its computation with a wide feed-forward network (a SwiGLU MLP) of 3072 "neurons." The heatmap shows how strongly each one fired for the currently selected token — row = layer, column = neuron, brightness = `|activation|`.

<img alt="Activation heatmap: 28 rows (layers) by 3072 columns (neurons), bright pixels on a dark background" src="/static/images/projects/llm-scope/neuron-heatmap.png" width="800"/>

Two things had to be solved to make this actually legible:

- **Scale.** A handful of neurons in every layer can have values an order of magnitude larger than the rest ("massive activations" — a well-documented phenomenon in large models). Normalizing by the maximum would crush everything else to black. Instead, each layer is clipped to its own 99th percentile and additionally sqrt-compressed, squeezing the dynamic range without losing the weaker signal.
- **Neuron order.** MLP hidden units have no inherent ordering (permutation symmetry) — the model's native order is visually pure noise. `compute_neuron_order.py` computes a stable order once, offline, via correlation-based hierarchical clustering over a diverse prompt corpus, so correlated neurons end up next to each other. In the UI this is the `order` selector: `raw`, `clustered` or `by mean`.

Worth saying up front what this heatmap doesn't do: with 3072 columns squeezed into the window width, a single neuron occupies a fraction of a pixel. It's great for the overall pattern and for differences between layers, but you can't read an individual neuron off it — that's what the top-k list in Token Journey is for.

## Attention

Clicking any token in the text washes earlier tokens in pink, proportional to how much attention that token paid them (averaged over all 16 attention heads, or for a single chosen layer). The **Attention Lens** panel below shows the same row at full resolution: row = earlier token, column = layer (0–27), brightness = attention weight.

<img alt="Attention Lens in heatmap mode: token labels on the left, a 28-column grid (layers), bright bands showing where the token 'Paris' directs its attention" src="/static/images/projects/llm-scope/attention-lens.png" width="800"/>

An implementation detail worth calling out: why exactly **one** cell per layer, rather than one per head? Because the 16 heads are averaged together at capture time, on the Python side, before anything reaches the data sent to the browser. For a given layer there is therefore exactly one number per earlier token, and per-head resolution is thrown away irreversibly at that stage — the front-end never sees it. For the same reason, the layer selector has **no effect** on heatmap mode, which always shows all 28 layers at once; it only matters in column mode and for the text overlay.

A second quirk: the very first token in a sequence routinely soaks up a disproportionate share of attention at every layer — the well-documented "attention sink" phenomenon. Left in as a reference point it would crush the rest of the scale to near-invisible, so it's excluded from normalization while still rendering at full intensity itself. The **skip sink** checkbox hides it from the panel entirely and rescales against what's left, and the difference is dramatic: while generating "Paris", everything looks uniformly dark without it; turn it on and you can see the model attending mainly to "France" and "capital" — exactly where it should be looking.

Seeing attention at all requires weights the fast default kernel (`sdpa`) never computes explicitly — the model has to be loaded with `attn_implementation="eager"` instead, which costs roughly 8–9x more time per token.

## Logit lens

At every depth — the embedding output ("layer -1") and the output of each of the 28 transformer blocks — the residual stream is projected through the model's own final norm and `lm_head`, as if the network had stopped computing right there. It's a way to eavesdrop on what the model "believes" long before it's actually done.

<img alt="Logit lens in column mode: an entropy sparkline at the top, a list of depths from -1 to 27 with the top-1 token and its probability, bars going from uncertain early layers to very confident late ones" src="/static/images/projects/llm-scope/logit-lens.png" width="800"/>

For intermediate layers this is only an approximation: the residual stream isn't expressed in the basis `lm_head` operates in until the final layer, so projecting earlier depths through that same matrix is a heuristic, not something the model was trained to support.

In practice you see exactly that pattern. For the prompt "The capital of France is", the prediction following "Paris" is essentially random for the first twenty layers — fragments like "ous" or a comma show up — and then from layer 21 it locks onto `**` (closing the bold) at 96–99% confidence and never moves again. Watching exactly *where* that moment happens is interesting in its own right.

There's one more artifact right at the top of the list: at depth -1, just after the embedding, the model "predicts" the very token it's currently reading. That's not a bug — Qwen3 ties the embedding and `lm_head` weights (`lm_head.weight` is literally the same tensor as `embed_tokens.weight`), so projecting a fresh embedding back through that matrix lands hardest on the token itself.

Generation is greedy — plain argmax, no sampling. That's deliberate: it means the deepest logit-lens row performs exactly the same computation the model does, and matches its output bit for bit. Sampling would add noise that muddies the very thing this panel exists to show.

## Token Journey

A panel that walks the single, currently-selected token through the whole pipeline, top to bottom: **tokenization** (text → vocabulary ID) → **embedding vector** → the internals of one **transformer block** (with its own layer stepper, independent of every other panel) → **output vector** → **prediction** → **detokenization**.

<img alt="Token Journey: the full pipeline for the token Paris — tokenization, embedding vector, transformer block internals with RMSNorm/Q-K-V/RoPE formulas, top attended tokens, MLP activations, residual OUT, output vector, top-5 prediction and detokenization" src="/static/images/projects/llm-scope/token-journey.png" width="600"/>

The whole panel follows one rule: **it never shows a number it didn't capture.** Solid amber boxes hold this token's actual values — the same numbers as the panels above, plus the embedding, residual and output vectors themselves as small heatmap strips. Dashed boxes are schematics of what the app never records or transmits: raw Q/K/V vectors, RoPE angles, pre-softmax scores. You get the formula and the tensor shape, never an invented number.

One detail that's easy to miss and that the panel gets right: in Qwen3 the per-head dimension (128) does not come from dividing `hidden_size` by the head count, which would give 1024/16 = 64. The Q projection therefore comes out **wider than the residual stream itself** — 16 × 128 = 2048 against 1024. Most transformer explainers quietly assume that division and print the wrong shapes.

The 1024-dim vector shown as "residual IN", "residual OUT", the embedding vector and the output vector is the same running quantity at every stage — one layer's OUT is identical to the next layer's IN, all the way from the embedding lookup to the final output vector. Stepping through layers with the transformer block's own arrows shows this single vector gradually deforming as it passes through all 28 layers.

## Two modes: offline and live

All the capture logic (model loading, hooks, the generation loop, the logit lens) lives in one module shared by two independent entry points:

- **Offline replay** (`capture.py`) — runs one prompt through the model and writes the whole run out as a single self-contained HTML file you can open offline and scrub through frame by frame. The shared CSS/JS from `static/` is inlined directly into the file, so the output is one dependency-free file — this is exactly the file that ends up on GitHub Pages.
- **Live** (`server.py`) — keeps the model resident in memory and streams activity over Server-Sent Events as you type prompts. One model instance serves one request at a time (a simple global lock) — fine for local use, not for concurrent multi-user hosting.

## Deployment and CI/CD

The online version (the link at the top) isn't a manually refreshed snapshot — a GitHub Action rebuilds it from scratch **on every push to `main`**: it installs dependencies, downloads and caches Qwen3-0.6B (~1.2 GB, once), runs `capture.py` on a CI runner, and publishes the resulting HTML to GitHub Pages through the official `actions/deploy-pages`. Nothing is committed back — the generated file lives only as the Pages deployment, so the git history doesn't accumulate yet another copy of the same multi-megabyte file on every refresh.

## Tech stack

- **PyTorch** + **Transformers** (`AutoModelForCausalLM`/`AutoTokenizer`) — model loading, forward hooks on every layer's `down_proj` (capturing MLP activations) and on each block's output (capturing the residual stream)
- **FastAPI** + Server-Sent Events — the live mode
- Plain **JavaScript + Canvas**, no framework — a deliberate choice so the offline output can stay a single HTML file with no build step
- **NumPy / SciPy / Pillow** — neuron-order clustering and the verification script
- **pytest** — the test suite, including a golden test that catches the numeric pipeline quietly starting to return something different
- **GitHub Actions** — CI/CD to GitHub Pages

## Limitations

- Attention requires `attn_implementation="eager"`, roughly 8–9x slower than the default fast kernel — the cost of extracting weights the model never normally materializes explicitly.
- The logit lens is a heuristic for intermediate layers, not a strict interpretation (see above) — only the deepest layer is guaranteed to match the model's actual prediction.
- The heatmap squeezes 3072 columns into the window width, so you can't read an individual neuron off it — it shows the pattern, not the specifics.
- Attention weights are averaged over heads at capture time, so per-head structure isn't available.
- A hard cap of 300 new tokens (the model usually hits EOS well before that anyway) — each frame carries a heavy payload (activations + attention + logit lens), so an open-ended limit would risk a multi-gigabyte HTML file or a very long stream.
- `server.py` serves one generation request at a time — this is not multi-user hosting.
- Neuron order in the heatmap is arbitrary until `compute_neuron_order.py` has been run once.
- This is a tool for observation, not intervention — you can't silence a neuron or clamp attention and watch the output change.

## References

- [Project repository](https://github.com/mpiotro4/LLM-Scope)
- [Live demo (GitHub Pages)](https://mpiotro4.github.io/LLM-Scope/)
- [Qwen/Qwen3-0.6B on Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B)
