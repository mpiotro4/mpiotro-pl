---
title_pl: "Tokenizery w modelach językowych - praktyczne porównanie"
title_en: "Tokenizers in Language Models - A Practical Comparison"
date: 2025-12-26
author: "Marcin Piotrowski"
tags: ["NLP", "tokenization", "transformers", "LLM", "BERT", "GPT"]
description_pl: "Praktyczny przewodnik po tokenizerach w dużych modelach językowych. Porównanie działania tokenizers BERT, GPT-4, GPT-2, T5, StarCoder i XLM-RoBERTa na przykładach wielojęzycznych."
description_en: "A practical guide to tokenizers in large language models. Comparison of BERT, GPT-4, GPT-2, T5, StarCoder and XLM-RoBERTa tokenizers with multilingual examples."
---

## PL

## Wstęp

Tokenizer to jeden z najważniejszych, choć często pomijanych komponentów każdego dużego modelu językowego. Jego wybór ma bezpośredni wpływ na wydajność modelu, jakość wyników oraz efektywność przetwarzania tekstu. W tym artykule przyjrzymy się praktycznemu działaniu różnych tokenizerów i zobaczymy, jak radzą sobie z wielojęzycznymi tekstami, emoji i kodem źródłowym.

> Prezentowany materiał został opracowany w oparciu o wiedzę zdobytą podczas krótkiego, darmowego kursu dostępnego na platformie deeplearning.ai: [How Transformer LLMs Work](https://www.deeplearning.ai/short-courses/how-transformer-llms-work/)
> **Kod źródłowy:** Wszystkie eksperymenty z tego artykułu dostępne są w : [Google Colab - Tokenizer Comparison](https://colab.research.google.com/drive/1nuKOvO3WqcEySQeHeUEa4ZzzheRX7FFw?usp=sharing)


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

### 🔹 BERT base-cased
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

### 🔹 BERT base-uncased
**Charakterystyka:** Wariant BERT z normalizacją do małych liter, słownik: 30,522 tokenów
```
ocab length: 30522
[CLS] english and capital ##ization [UNK] [UNK] [UNK] show _ token ##s false none eli ##f = = > = else : two tab ##s : " " three tab ##s : " " 12 . 0 * 50 = 600 pr ##zy ##k ##ła ##do ##we z ##dan ##ie w je ##zy ##ku pol ##ski ##m , z ##o ##ł ##c [SEP]
```
**Obserwacje:**
- Całkowita utrata informacji o wielkości liter
- Nieznacznie większy słownik niż wersja *cased*
- Podobne problemy z reprezentacją znaków specjalnych, ponadto utrata części informacji (ż -> z)

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

## Podsumowanie

Tokenizer to często niedoceniany, ale kluczowy element każdego LLM. Jak pokazują powyższe porównania, różnice między tokenizerami mogą być znaczące - szczególnie przy pracy z językami innymi niż angielski, znakami specjalnymi czy kodem źródłowym.
Wybór tokenizera ma bezpośredni wpływ na:
- **Efektywność** - mniej tokenów = szybsze przetwarzanie i niższe koszty API
- **Jakość** - lepsza reprezentacja = lepsze zrozumienie kontekstu przez model
- **Uniwersalność** - wsparcie dla różnych języków i formatów tekstu
Warto eksperymentować z różnymi modelami i tokenizerami, aby znaleźć optymalne rozwiązanie dla swojego przypadku użycia.
A no i ostatnia uwaga na marginesie, emoji 🥸 jest stosunkowo nowe (Unicode 13.0, 2020) więc najprawdopodobniej dlatego żaden z tokenizerów go poprawnie nie rozpoznał

## Przydatne linki

- [Hugging Face Tokenizers](https://huggingface.co/docs/tokenizers/index)
- [Tokenizer Arena - interaktywne porównanie](https://huggingface.co/spaces/Xenova/the-tokenizer-playground)
- [Kurs: How Transformer LLMs Work](https://www.deeplearning.ai/short-courses/how-transformer-llms-work/)
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer)


## EN