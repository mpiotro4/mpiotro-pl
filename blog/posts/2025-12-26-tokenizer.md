---
title_pl: "Tokenizery w modelach językowych - praktyczne porównanie"
title_en: "Tokenizers in Language Models - A Practical Comparison"
date: 2025-12-26
updated: 2025-12-28
author: "Marcin Piotrowski"
tags: ["NLP", "tokenization", "transformers", "LLM", "BERT", "GPT"]
description_pl: "Praktyczny przewodnik po tokenizerach w dużych modelach językowych. Porównanie BERT, GPT-4, GPT-2, T5, StarCoder i XLM-RoBERTa na przykładach wielojęzycznych oraz budowa własnego tokenizera od podstaw."
description_en: "A practical guide to tokenizers in large language models. Comparison of BERT, GPT-4, GPT-2, T5, StarCoder and XLM-RoBERTa with multilingual examples, plus building your own tokenizer from scratch."
---

## PL

## Wstęp

Tokenizer to jeden z najważniejszych, choć często pomijanych komponentów każdego dużego modelu językowego. Jego wybór ma bezpośredni wpływ na wydajność modelu, jakość wyników oraz efektywność przetwarzania tekstu.
W tym artykule:
- Przyjrzymy się praktycznemu działaniu różnych tokenizerów
- Porównamy ich zachowanie na tekstach wielojęzycznych, emoji i kodzie
- Zbudujemy własny, prosty tokenizer od podstaw

> Prezentowany materiał został opracowany w oparciu o wiedzę zdobytą podczas krótkiego, darmowego kursu dostępnego na platformie deeplearning.ai: [How Transformer LLMs Work](https://www.deeplearning.ai/short-courses/how-transformer-llms-work/)
> **Kod źródłowy:** [Google Colab - Tokenizer Comparison](https://colab.research.google.com/drive/1nuKOvO3WqcEySQeHeUEa4ZzzheRX7FFw?usp=sharing)


## Tokenizer - most między człowiekiem a modelem

Tokenizer stanowi punkt wejścia do każdego dużego modelu językowego. Można powiedzieć, że stanowi most pomiędzy człowiekiem a modelem, ponieważ model nie operuje bezpośrednio na słowach czy literach, lecz na tokenach. W praktyce często upraszcza się, że słowo = token, lecz w rzeczywistości jedno słowo może składać się z wielu tokenów. 
Każdy LLM posiada swój własny słownik tokenów - każdy token ma unikalne ID. Zadaniem tokenizera jest zamiana tekstu na ciąg tokenów i przekazanie listy ich ID, aby model mógł wykonać swoją pracę. 
W tym wpisie przybliżę działanie różnych tokenizerów w praktyce i zaobserwujemy różnice między nimi, nie wchodząc w szczegóły techniczne. Wykorzystamy do tego celu API Hugging Face.

## Praktyczna demonstracja

Aby dokonać zamiany tekstu na tokeny, wystarczy kilka linii kodu:

```python
from transformers import AutoTokenizer
sentence = "Hello world!"
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
tokens = tokenizer(sentence)
```

`AutoTokenizer` to jedna z klas API Hugging Face, które udostępnia tysiące modeli na zasadach open source. Na podstawie podanej nazwy modelu (w tym przypadku `bert-base-cased`) automatycznie:

1. Pobiera odpowiedni tokenizer z repozytorium Hugging Face
2. Ładuje jego konfigurację i słownik
3. Zapisuje go lokalnie w cache na przyszłość

Dzięki temu nie musimy ręcznie sprawdzać, jakiego konkretnie tokenizera użyć - `AutoTokenizer` rozpoznaje typ modelu i ładuje właściwą implementację.

### Struktura obiektu BatchEncoding

Zwrócony obiekt `tokens` jest instancją klasy `BatchEncoding`, która implementuje interfejs słownikowy i zawiera następujące komponenty:

| Klucz | Opis | Przykład |
|-------|------|----------|
| `input_ids` | Sekwencja identyfikatorów tokenów | `[101, 8667, 1362, 106, 102]` |
| `attention_mask` | Maska wskazująca rzeczywiste tokeny vs. padding | `[1, 1, 1, 1, 1]` |
| `token_type_ids` | Identyfikacja przynależności do segmentów (w zadaniach z parami zdań) | `[0, 0, 0, 0, 0]` |
```python
print(tokens)
# Output:
# {'input_ids': [101, 8667, 1362, 106, 102], 
#  'token_type_ids': [0, 0, 0, 0, 0], 
#  'attention_mask': [1, 1, 1, 1, 1]}
```


### Dekodowanie tokenów

Aby zdekodować ID tokenów do konkretnych słów, wystarczy użyć funkcji `decode`:

```python
for id in token_ids:
    print(tokenizer.decode(id))
```
```
[CLS]
Hello
world
!
[SEP]
```

W zdekodowanych tokenach poza słowami widzimy tzw. **tokeny specjalne**, które mają następujące znaczenia:

- **`[CLS]`** (*classification*) - token inicjalizujący sekwencję, wykorzystywany w zadaniach klasyfikacyjnych
- **`[SEP]`** (*separator*) - delimiter segmentujący lub terminujący sekwencję
- **`[UNK]`** (*unknown*) - reprezentacja tokenów nieobecnych w słowniku
- **`[PAD]`** (*padding*) - wyrównanie długości sekwencji w batch'ach

Powyższy przykład demonstruje operacje wykonywane przez każdy LLM podczas obsługi naszych zapytań. Najpierw wejściowy prompt jest zamieniany na tokeny, następnie model przetwarza te tokeny, a na sam koniec są one dekodowane z powrotem do tekstu, aby użytkownik mógł go przeczytać.

## Porównanie tokenizerów

Aby systematycznie przeanalizować różnice w implementacjach tokenizerów, przygotowano tekst testowy zawierający wyzwania charakterystyczne dla przetwarzania języka naturalnego:

-  Teksty w języku angielskim z różnicowaną wielkością liter
-  Emotikony i symbole Unicode (🎵 🥸 鸟)
-  Fragmenty kodu źródłowego z operatorami logicznymi
-  Sekwencje białych znaków (tabulatory, spacje)
-  Wyrażenia numeryczne i matematyczne
-  Tekst w języku polskim ze znakami diakrytycznymi

```python
text = """
English and CAPITALIZATION
🎵 🥸  鸟
show_tokens False None elif == >= else: two tabs:"    " Three tabs: "       "
12.0*50=600
Przykładowe zdanie w języku polskim, żółć
"""
```

#### Wyniki porównania

### BERT base-cased
**Charakterystyka:** Model BERT z zachowaniem wielkości liter, słownik: 28,996 tokenów
```
Vocab length: 28996
[CLS] English and CA ##PI ##TA ##L ##I ##Z ##AT ##ION [UNK] [UNK] [UNK] show _ token ##s F ##als ##e None el ##if = = > = else : two ta ##bs : " " Three ta ##bs : " " 12 . 0 * 50 = 600 P ##rz ##yk ##ła ##do ##we z ##dan ##ie w j ##ę ##zy ##ku p ##ols ##kim , ż ##ó ##ł ##ć [SEP]
```
**Obserwacje:**
- Wykorzystanie prefiksu `##` do oznaczenia sub-tokenów (WordPiece)
- Słowa wielosylabowe zostały rozbite na liczne tokeny
- Brak wsparcia dla emoji → tokeny `[UNK]`
- Obsługuje polskie znaki diakrytyczne, lecz rozbija je na osobne tokeny 

---

### BERT base-uncased
**Charakterystyka:** Wariant BERT z normalizacją do małych liter, słownik: 30,522 tokenów
```
ocab length: 30522
[CLS] english and capital ##ization [UNK] [UNK] [UNK] show _ token ##s false none eli ##f = = > = else : two tab ##s : " " three tab ##s : " " 12 . 0 * 50 = 600 pr ##zy ##k ##ła ##do ##we z ##dan ##ie w je ##zy ##ku pol ##ski ##m , z ##o ##ł ##c [SEP]
```
**Obserwacje:**
- Całkowita utrata informacji o wielkości liter
- Nieznacznie większy słownik niż wersja *cased*
- Podobne problemy z reprezentacją znaków specjalnych, ponadto utrata części informacji (ż -> z)

---

### Xenova/gpt-4
**Charakterystyka:** Implementacja tokenizera GPT-4, słownik: 100,263 tokeny
```
Vocab length: 100263

 English  and  CAPITAL IZATION 
 � � �  � � �    � � � 
 show _tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         "
 12 . 0 * 50 = 600 
 Pr zy k ł adow e  zd anie  w  j ę zy ku  pol sk im ,  ż ół ć 
```
**Obserwacje:**
- Znacząco większy słownik umożliwia bardziej efektywną tokenizację, nie ma tak dużej ilości tokenów dla wielosylabowych słów
- Lepsza obsługa białych znaków i struktury kodu
- Umiarkowane wsparcie dla języka polskiego, dalej rozbija polskie słowa na wiele tokenów
- Problematyczna reprezentacja emoji

---

### gpt2
**Charakterystyka:** Klasyczny tokenizer GPT-2 (BPE), słownik: 50,257 tokenów

```
Vocab length: 50257

 English  and  CAP ITAL IZ ATION 
 � � �  � � �    � � � 
 show _ t ok ens  False  None  el if  ==  >=  else :  two  tabs :"        "  Three  tabs :  "              " 
 12 . 0 * 50 = 600 
 Pr zyk ł adow e  z dan ie  w  j � � zy ku  pol sk im ,  � � ó ł ć 
```
**Obserwacje:**
- Znacząca degradacja reprezentacji znaków Unicode
- Nieprecyzyjna obsługa sekwencji białych znaków
- Brak obsługi części polskich znaków

---

### google/flan-t5-small
**Charakterystyka:** Kompaktowy model T5 (Text-to-Text Transfer Transformer) z instrukcyjnym fine-tuningiem, słownik: 32,100 tokenów
```
Vocab length: 32100
English and CA PI TAL IZ ATION  <unk>  <unk>  <unk> show _ to ken s Fal s e None  e l if = = > = else : two tab s : " " Three tab s : " " 12. 0 * 50 = 600 Pr zy k <unk> a dow e  z d ani e  w  j <unk> zy ku  pol s kim ,  <unk> ó <unk>  </s>
```
**Obserwacje:**
- Token `</s>` jako marker końca sekwencji (charakterystyczny dla T5)
- `<unk>` dla znaków spoza słownika
- Ograniczona efektywność dla tekstów wielojęzycznych

---

### BigCode StarCoder2-15B

**Charakterystyka:** Specjalizowany model dla generacji kodu, słownik: 49,152 tokeny
```
Vocab length: 49152

 English  and  CAPITAL IZATION 
 � � �  � � �     � � 
 show _ tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         " 
 1 2 . 0 * 5 0 = 6 0 0 
 Pr zy k ł adow e  z d anie  w  j ę zy ku  pol sk im ,  ż ó ł ć 
```

**Obserwacje:**
- Precyzyjna obsługa składni programistycznej (operatory, słowa kluczowe)
- Atomizacja cyfr w wyrażeniach numerycznych
- Rozsądna reprezentacja polskich znaków diakrytycznych
- Nadal problematyczna obsługa emoji

---

### xlm-roberta-large
**Charakterystyka:** Wielojęzyczny model Transformer, słownik: 250,002 tokeny

```
Vocab length: 250002
<s> English and CAP ITA LIZA TION  🎵  <unk>  鸟 show _ tok ens Fal se No ne el if  == > = else : two tab s : " " Three tab s : " " 1 2.0 * 50 = 600 Przy kład owe z danie w język u polskim ,  żół ć </s> 
```
**Obserwacje:**
- **Najlepsze wsparcie dla języka polskiego** wśród wszystkich testowanych modeli, najpewniej za sprawą największego słownika
- Rozpoznawanie emoji muzycznej 🎵 i chińskiego znaku 鸟
- Minimalna fragmentacja słów w języku polskim
- Tokeny `<s>` i `</s>` na początku i końcu sekwencji.

---

## Kluczowe obserwacje

| Aspekt | Wnioski |
|--------|---------|
| **Rozmiar słownika** | Od ~29k (BERT) do ~250k (XLM-RoBERTa). Większy słownik = bardziej efektywna tokenizacja i mniej sub-tokenów |
| **Wsparcie wielojęzyczne** | Silnie zależne od rozmiaru słownika. Małe słowniki rozbiją nieznane słowa na wiele drobnych tokenów |
| **Obsługa emoji i Unicode** | Modele nowszej generacji (XLM-RoBERTa, GPT-4) radzą sobie znacząco lepiej |
| **Specjalizacja** | Modele domenowe (StarCoder dla kodu) lepiej obsługują swoją dziedzinę |
| **Język polski** | Najlepsza obsługa w XLM-RoBERTa dzięki wielojęzycznemu treningowi i dużemu słownikowi |

## Co to oznacza w praktyce?

Wybór odpowiedniego tokenizera powinien być uzależniony od konkretnego przypadku użycia:

* **Dla tekstów angielskich:**
    - Większość tokenizerów zapewni dobre rezultaty
    - GPT-4 i XLM-RoBERTa oferują najlepszą efektywność
* **Dla generacji kodu:**
    - **StarCoder** - dedykowany, precyzyjny w obsłudze składni 
    - GPT-4 - uniwersalny, sprawdza się również w kodzie
* **Dla tekstów wielojęzycznych (w tym polskiego):**
    - **XLM-RoBERTa** - bezkonkurencyjny lider
    - Modele anglojęzyczne (BERT, GPT-2) mogą znacząco fragmentować tekst
* **Dla emoji i Unicode:**
    - Nowsze modele (XLM-RoBERTa, GPT-4, Qwen)
    - Unikaj starszych tokenizerów (GPT-2, wczesne BERT)


## Własny tokenizer

> Przykład własnego tokenizera pochodzi z kursu Andreja Karpathy'ego: [Building makemore](https://www.youtube.com/watch?v=kCc8FmEb1nY)

Możemy również stworzyć własny tokenizer. Nie będzie on tak zaawansowany jak wcześniej omawiane, lecz świetnie nada się do celów edukacyjnych. Zbudujemy najprostszy możliwy tokenizer, w którym tokenami są pojedyncze znaki.
Zaczniemy od tekstu, który chcemy podzielić na tokeny. Wykorzystamy publicznie dostępny dataset zawierający wszystkie teksty Shakespearea: [Tiny Shakespeare](https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt)
Po wczytaniu całego datasetu wystarczy zamienić go na `set`, aby uzyskać zbiór unikalnych znaków. Następnie konwertujemy z powrotem do listy i sortujemy:
```python
chars = sorted(list(set(text)))
vocab_size = len(chars)
print(''.join(chars))
print(vocab_size)
```
```
 !$&',-.3:;?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
65
```
Nasz słownik zawiera 65 tokenów - wszystkie litery alfabetu oraz niektóre znaki specjalne.
Następnie potrzebujemy funkcji do kodowania tekstu na tokeny oraz dekodowania tokenów z powrotem do tekstu. W tym celu tworzymy dwa słowniki mapujące:

- **`stoi`** (string to integer) - znaki → liczby
- **`itos`** (integer to string) - liczby → znaki
```python
# Mapowanie znaków na liczby i odwrotnie
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }

# Funkcje kodujące i dekodujące
encode = lambda s: [stoi[c] for c in s]  # tekst → lista liczb
decode = lambda l: ''.join([itos[i] for i in l])  # lista liczb → tekst

print(encode("hii there"))
print(decode(encode("hii there")))
```
```
[46, 47, 47, 1, 58, 46, 43, 56, 43]
hii there
```
I to wszystko! Tak prosty tokenizer na pewno nie pozwoli na skonstruowanie zaawansowanego LLM, ale można z jego użyciem zbudować prosty transformer i zaobserwować działanie mechanizmu attention. O tym w kolejnych wpisach.

## Podsumowanie

Tokenizer to często niedoceniany, ale kluczowy element każdego LLM. Jak pokazują powyższe porównania, różnice między tokenizerami mogą być znaczące - szczególnie przy pracy z językami innymi niż angielski, znakami specjalnymi czy kodem źródłowym.
Wybór tokenizera ma bezpośredni wpływ na:
- **Efektywność** - mniej tokenów = szybsze przetwarzanie i niższe koszty API
- **Jakość** - lepsza reprezentacja = lepsze zrozumienie kontekstu przez model
- **Uniwersalność** - wsparcia dla różnych języków i formatów tekstu
Warto eksperymentować z różnymi modelami i tokenizerami, aby znaleźć optymalne rozwiązanie dla swojego przypadku użycia.
**Ciekawostka na koniec:** Emoji 🥸 (twarz z wąsami i okularami) jest stosunkowo nowe (Unicode 13.0, 2020), dlatego żaden z testowanych tokenizerów nie rozpoznał go poprawnie - większość modeli była trenowana wcześniej i nie ma tego znaku w swoim słowniku.

## Przydatne linki

- [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers/index)
- [Tokenizer Arena - interaktywne porównanie](https://huggingface.co/spaces/Xenova/the-tokenizer-playground)
- [Kurs: How Transformer LLMs Work](https://www.deeplearning.ai/short-courses/how-transformer-llms-work/)
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer)


## EN

---
title: "Tokenizers in Language Models - A Practical Comparison"
date: 2025-12-26
updated: 2025-12-28
author: "Marcin Piotrowski"
tags: ["NLP", "tokenization", "transformers", "LLM", "BERT", "GPT"]
description: "A practical guide to tokenizers in large language models. Comparison of BERT, GPT-4, GPT-2, T5, StarCoder and XLM-RoBERTa with multilingual examples, plus building your own tokenizer from scratch."
---

## Introduction

A tokenizer is one of the most important, yet often overlooked, components of every large language model. Its choice has a direct impact on model performance, output quality, and text processing efficiency.
In this article:
- We'll look at the practical behavior of different tokenizers
- We'll compare their behavior on multilingual texts, emoji, and code
- We'll build our own simple tokenizer from scratch

> This material was developed based on knowledge gained from a short, free course available on the deeplearning.ai platform: [How Transformer LLMs Work](https://www.deeplearning.ai/short-courses/how-transformer-llms-work/)
> **Source code:** [Google Colab - Tokenizer Comparison](https://colab.research.google.com/drive/1nuKOvO3WqcEySQeHeUEa4ZzzheRX7FFw?usp=sharing)


## Tokenizer - the bridge between humans and the model

A tokenizer serves as the entry point to every large language model. You could say it acts as a bridge between humans and the model, because the model doesn't operate directly on words or letters, but on tokens. In practice, it's often simplified that word = token, but in reality one word can consist of many tokens.
Every LLM has its own token vocabulary - each token has a unique ID. The tokenizer's job is to convert text into a sequence of tokens and pass the list of their IDs so the model can do its work.
In this post I'll walk through the behavior of different tokenizers in practice and observe the differences between them, without going into technical details. We'll use the Hugging Face API for this purpose.

## Practical demonstration

To convert text into tokens, just a few lines of code are needed:

```python
from transformers import AutoTokenizer
sentence = "Hello world!"
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
tokens = tokenizer(sentence)
```

`AutoTokenizer` is one of the Hugging Face API classes that provides thousands of open-source models. Based on the given model name (in this case `bert-base-cased`) it automatically:

1. Downloads the appropriate tokenizer from the Hugging Face repository
2. Loads its configuration and vocabulary
3. Saves it locally in cache for future use

This means we don't have to manually check which specific tokenizer to use - `AutoTokenizer` recognizes the model type and loads the correct implementation.

### BatchEncoding object structure

The returned `tokens` object is an instance of the `BatchEncoding` class, which implements a dictionary interface and contains the following components:

| Key | Description | Example |
|-----|-------------|---------|
| `input_ids` | Sequence of token identifiers | `[101, 8667, 1362, 106, 102]` |
| `attention_mask` | Mask indicating real tokens vs. padding | `[1, 1, 1, 1, 1]` |
| `token_type_ids` | Segment membership identification (in sentence-pair tasks) | `[0, 0, 0, 0, 0]` |

```python
print(tokens)
# Output:
# {'input_ids': [101, 8667, 1362, 106, 102], 
#  'token_type_ids': [0, 0, 0, 0, 0], 
#  'attention_mask': [1, 1, 1, 1, 1]}
```


### Decoding tokens

To decode token IDs back to actual words, simply use the `decode` function:

```python
for id in token_ids:
    print(tokenizer.decode(id))
```
```
[CLS]
Hello
world
!
[SEP]
```

In the decoded tokens, beyond the words we can see so-called **special tokens**, which have the following meanings:

- **`[CLS]`** (*classification*) - sequence-initializing token, used in classification tasks
- **`[SEP]`** (*separator*) - delimiter that segments or terminates the sequence
- **`[UNK]`** (*unknown*) - representation of tokens absent from the vocabulary
- **`[PAD]`** (*padding*) - equalizes sequence lengths in batches

The above example demonstrates the operations performed by every LLM when handling our queries. First, the input prompt is converted into tokens, then the model processes those tokens, and finally they are decoded back into text for the user to read.

## Tokenizer comparison

To systematically analyze the differences in tokenizer implementations, a test text was prepared containing challenges characteristic of natural language processing:

- English texts with varied capitalization
- Emoticons and Unicode symbols (🎵 🥸 鸟)
- Source code fragments with logical operators
- Whitespace sequences (tabs, spaces)
- Numerical and mathematical expressions
- Polish text with diacritic characters

```python
text = """
English and CAPITALIZATION
🎵 🥸  鸟
show_tokens False None elif == >= else: two tabs:"    " Three tabs: "       "
12.0*50=600
Przykładowe zdanie w języku polskim, żółć
"""
```

#### Comparison results

### BERT base-cased
**Characteristics:** BERT model with case preservation, vocabulary: 28,996 tokens
```
Vocab length: 28996
[CLS] English and CA ##PI ##TA ##L ##I ##Z ##AT ##ION [UNK] [UNK] [UNK] show _ token ##s F ##als ##e None el ##if = = > = else : two ta ##bs : " " Three ta ##bs : " " 12 . 0 * 50 = 600 P ##rz ##yk ##ła ##do ##we z ##dan ##ie w j ##ę ##zy ##ku p ##ols ##kim , ż ##ó ##ł ##ć [SEP]
```
**Observations:**
- Use of the `##` prefix to mark sub-tokens (WordPiece)
- Polysyllabic words were split into numerous tokens
- No emoji support → `[UNK]` tokens
- Handles Polish diacritic characters but splits them into separate tokens

---

### BERT base-uncased
**Characteristics:** BERT variant with lowercasing normalization, vocabulary: 30,522 tokens
```
Vocab length: 30522
[CLS] english and capital ##ization [UNK] [UNK] [UNK] show _ token ##s false none eli ##f = = > = else : two tab ##s : " " three tab ##s : " " 12 . 0 * 50 = 600 pr ##zy ##k ##ła ##do ##we z ##dan ##ie w je ##zy ##ku pol ##ski ##m , z ##o ##ł ##c [SEP]
```
**Observations:**
- Complete loss of capitalization information
- Slightly larger vocabulary than the *cased* version
- Similar issues with special character representation, plus loss of some information (ż -> z)

---

### Xenova/gpt-4
**Characteristics:** GPT-4 tokenizer implementation, vocabulary: 100,263 tokens
```
Vocab length: 100263

 English  and  CAPITAL IZATION 
 � � �  � � �    � � � 
 show _tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         "
 12 . 0 * 50 = 600 
 Pr zy k ł adow e  zd anie  w  j ę zy ku  pol sk im ,  ż ół ć 
```
**Observations:**
- Significantly larger vocabulary enables more efficient tokenization with fewer tokens for polysyllabic words
- Better handling of whitespace and code structure
- Moderate support for Polish, still splits Polish words into many tokens
- Problematic emoji representation

---

### gpt2
**Characteristics:** Classic GPT-2 tokenizer (BPE), vocabulary: 50,257 tokens

```
Vocab length: 50257

 English  and  CAP ITAL IZ ATION 
 � � �  � � �    � � � 
 show _ t ok ens  False  None  el if  ==  >=  else :  two  tabs :"        "  Three  tabs :  "              " 
 12 . 0 * 50 = 600 
 Pr zyk ł adow e  z dan ie  w  j � � zy ku  pol sk im ,  � � ó ł ć 
```
**Observations:**
- Significant degradation of Unicode character representation
- Imprecise handling of whitespace sequences
- No support for some Polish characters

---

### google/flan-t5-small
**Characteristics:** Compact T5 (Text-to-Text Transfer Transformer) model with instruction fine-tuning, vocabulary: 32,100 tokens
```
Vocab length: 32100
English and CA PI TAL IZ ATION  <unk>  <unk>  <unk> show _ to ken s Fal s e None  e l if = = > = else : two tab s : " " Three tab s : " " 12. 0 * 50 = 600 Pr zy k <unk> a dow e  z d ani e  w  j <unk> zy ku  pol s kim ,  <unk> ó <unk>  </s>
```
**Observations:**
- `</s>` token as end-of-sequence marker (characteristic of T5)
- `<unk>` for characters outside the vocabulary
- Limited efficiency for multilingual texts

---

### BigCode StarCoder2-15B

**Characteristics:** Specialized model for code generation, vocabulary: 49,152 tokens
```
Vocab length: 49152

 English  and  CAPITAL IZATION 
 � � �  � � �     � � 
 show _ tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         " 
 1 2 . 0 * 5 0 = 6 0 0 
 Pr zy k ł adow e  z d anie  w  j ę zy ku  pol sk im ,  ż ó ł ć 
```

**Observations:**
- Precise handling of programming syntax (operators, keywords)
- Atomization of digits in numerical expressions
- Reasonable representation of Polish diacritic characters
- Still problematic emoji handling

---

### xlm-roberta-large
**Characteristics:** Multilingual Transformer model, vocabulary: 250,002 tokens

```
Vocab length: 250002
<s> English and CAP ITA LIZA TION  🎵  <unk>  鸟 show _ tok ens Fal se No ne el if  == > = else : two tab s : " " Three tab s : " " 1 2.0 * 50 = 600 Przy kład owe z danie w język u polskim ,  żół ć </s> 
```
**Observations:**
- **Best Polish language support** among all tested models, most likely due to the largest vocabulary
- Recognition of the musical emoji 🎵 and Chinese character 鸟
- Minimal fragmentation of Polish words
- `<s>` and `</s>` tokens at the beginning and end of the sequence

---

## Key observations

| Aspect | Findings |
|--------|---------|
| **Vocabulary size** | From ~29k (BERT) to ~250k (XLM-RoBERTa). Larger vocabulary = more efficient tokenization and fewer sub-tokens |
| **Multilingual support** | Strongly dependent on vocabulary size. Small vocabularies will split unknown words into many small tokens |
| **Emoji and Unicode handling** | Newer generation models (XLM-RoBERTa, GPT-4) handle these significantly better |
| **Specialization** | Domain-specific models (StarCoder for code) handle their domain better |
| **Polish language** | Best support in XLM-RoBERTa thanks to multilingual training and large vocabulary |

## What does this mean in practice?

The choice of the right tokenizer should depend on the specific use case:

* **For English texts:**
    - Most tokenizers will provide good results
    - GPT-4 and XLM-RoBERTa offer the best efficiency
* **For code generation:**
    - **StarCoder** - dedicated, precise in syntax handling
    - GPT-4 - universal, also works well with code
* **For multilingual texts (including Polish):**
    - **XLM-RoBERTa** - unrivaled leader
    - English-language models (BERT, GPT-2) may significantly fragment text
* **For emoji and Unicode:**
    - Newer models (XLM-RoBERTa, GPT-4, Qwen)
    - Avoid older tokenizers (GPT-2, early BERT)


## Building your own tokenizer

> This example of a custom tokenizer comes from Andrej Karpathy's course: [Building makemore](https://www.youtube.com/watch?v=kCc8FmEb1nY)

We can also create our own tokenizer. It won't be as advanced as the ones discussed earlier, but it's great for educational purposes. We'll build the simplest possible tokenizer where the tokens are individual characters.
We'll start with the text we want to tokenize. We'll use a publicly available dataset containing all of Shakespeare's texts: [Tiny Shakespeare](https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt)
After loading the entire dataset, simply convert it to a `set` to get the collection of unique characters. Then convert back to a list and sort:
```python
chars = sorted(list(set(text)))
vocab_size = len(chars)
print(''.join(chars))
print(vocab_size)
```
```
 !$&',-.3:;?ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
65
```
Our vocabulary contains 65 tokens - all letters of the alphabet and some special characters.
Next we need functions to encode text into tokens and decode tokens back into text. For this we create two mapping dictionaries:

- **`stoi`** (string to integer) - characters → numbers
- **`itos`** (integer to string) - numbers → characters
```python
# Character to number mapping and vice versa
stoi = { ch:i for i,ch in enumerate(chars) }
itos = { i:ch for i,ch in enumerate(chars) }

# Encoding and decoding functions
encode = lambda s: [stoi[c] for c in s]  # text → list of numbers
decode = lambda l: ''.join([itos[i] for i in l])  # list of numbers → text

print(encode("hii there"))
print(decode(encode("hii there")))
```
```
[46, 47, 47, 1, 58, 46, 43, 56, 43]
hii there
```
And that's it! Such a simple tokenizer certainly won't allow building an advanced LLM, but you can use it to build a simple transformer and observe how the attention mechanism works. More on that in future posts.

## Summary

A tokenizer is an often underappreciated but crucial element of every LLM. As the comparisons above show, the differences between tokenizers can be significant - especially when working with languages other than English, special characters, or source code.
The choice of tokenizer has a direct impact on:
- **Efficiency** - fewer tokens = faster processing and lower API costs
- **Quality** - better representation = better context understanding by the model
- **Universality** - support for different languages and text formats

It's worth experimenting with different models and tokenizers to find the optimal solution for your use case.

**Fun fact:** The 🥸 emoji (face with mustache and glasses) is relatively new (Unicode 13.0, 2020), which is why none of the tested tokenizers recognized it correctly - most models were trained earlier and don't have this character in their vocabulary.

## Useful links

- [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers/index)
- [Tokenizer Arena - interactive comparison](https://huggingface.co/spaces/Xenova/the-tokenizer-playground)
- [Course: How Transformer LLMs Work](https://www.deeplearning.ai/short-courses/how-transformer-llms-work/)
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer)