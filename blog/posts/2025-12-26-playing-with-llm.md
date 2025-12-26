---
title_pl: ""
title_en: ""
date: 2025-12-26
author: "Marcin Piotrowski"
tags: []
description_pl: ""
description_en: ""
---

## PL

## Wstęp

> Niniejszy wpis został w dużej mierze oparty na wiedzy zdobytej w krótkim darmowym kursie dostępnym na platformie deeplearning.ai pod linkiem: https://www.deeplearning.ai/short-courses/how-transformer-llms-work/

## Tokenizer

Tokenizer stanowi punkt wejścia do każdego dużego modelu językowego. Można powiedzieć, że stanowi most pomiędzy człowiekiem a modelem, ponieważ model nie operuje bezpośrednio na słowach czy literach, lecz na tokenach. W praktyce często upraszcza się, że słowo = token, lecz w rzeczywistości jedno słowo może składać się z wielu tokenów. Każdy LLM posiada swój własny słownik tokenów - każdy token ma unikalne ID. Zadaniem tokenizera jest zamiana tekstu na ciąg tokenów i przekazanie listy ich ID, aby model mógł wykonać swoją pracę. W tym wpisie przybliżę działanie różnych tokenizerów w praktyce i zaobserwujemy różnice między nimi, nie wchodząc w szczegóły techniczne. Wykorzystamy do tego celu API Hugging Face.

```python
from transformers import AutoTokenizer
sentence = "Hello world!"
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
tokens = tokenizer(sentence)
```

`tokens` to obiekt typu BatchEncoding (działa jak słownik).
Zawiera przetworzone dane wejściowe dla modelu:

* input_ids - tekst zamieniony na liczby (ID tokenów)
*  attention_mask - które pozycje są prawdziwymi tokenami (1), a które paddingiem (0)
*  token_type_ids - rozróżnienie zdań w parach zdań

```
{'input_ids': [101, 8667, 1362, 106, 102], 'token_type_ids': [0, 0, 0, 0, 0], 'attention_mask': [1, 1, 1, 1, 1]}

```

Aby zdekodować id tokenów, do konkretnych słów wystarczy użyć funkcji `decode`

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

Powyższy przykład demonstruje operacje wykonywane przez każdy LLM podczas obsługi naszych zapytań. Najpierw wejściowy prompt jest zamieniany na tokeny, z kolei na sam koniec tokeny są z powrotem dekodowane do tekst aby użytkownik mógł go przeczytać.

Istnieje wiele tokenizerów gdzie każdy wykonuje swoją pracę w inny sposób, poniżej porównanie kilku z nich. Tekst poniżej posłuży do testowania różnych tokenizerów. Zawiera potencjalne pułapki takie jak emoji, wielkie litery, fragmenty kodu, białe znaki, liczby oraz zdanie w języku polskim. Pozwoli to zaobserwować różnice w działaniu poszczególnych tokenizerów.

```python
text = """
English and CAPITALIZATION
🎵 🥸  鸟
show_tokens False None elif == >= else: two tabs:"    " Three tabs: "       "
12.0*50=600
Przykładowe zdanie w języku polskim, żółć
"""
```

### bert-base-cased 

```
Vocab length: 28996
[CLS] English and CA ##PI ##TA ##L ##I ##Z ##AT ##ION [UNK] [UNK] [UNK] show _ token ##s F ##als ##e None el ##if = = > = else : two ta ##bs : " " Three ta ##bs : " " 12 . 0 * 50 = 600 P ##rz ##yk ##ła ##do ##we z ##dan ##ie w j ##ę ##zy ##ku p ##ols ##kim , ż ##ó ##ł ##ć [SEP]
```

### bert-base-uncased

```
ocab length: 30522
[CLS] english and capital ##ization [UNK] [UNK] [UNK] show _ token ##s false none eli ##f = = > = else : two tab ##s : " " three tab ##s : " " 12 . 0 * 50 = 600 pr ##zy ##k ##ła ##do ##we z ##dan ##ie w je ##zy ##ku pol ##ski ##m , z ##o ##ł ##c [SEP]
```

### Xenova/gpt-4

```
Vocab length: 100263

 English  and  CAPITAL IZATION 
 � � �  � � �    � � � 
 show _tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         "
 12 . 0 * 50 = 600 
 Pr zy k ł adow e  zd anie  w  j ę zy ku  pol sk im ,  ż ół ć 
```

### gpt2

```
Vocab length: 50257

 English  and  CAP ITAL IZ ATION 
 � � �  � � �    � � � 
 show _ t ok ens  False  None  el if  ==  >=  else :  two  tabs :"        "  Three  tabs :  "              " 
 12 . 0 * 50 = 600 
 Pr zyk ł adow e  z dan ie  w  j � � zy ku  pol sk im ,  � � ó ł ć 
```

### google/flan-t5-small

```
Vocab length: 32100
English and CA PI TAL IZ ATION  <unk>  <unk>  <unk> show _ to ken s Fal s e None  e l if = = > = else : two tab s : " " Three tab s : " " 12. 0 * 50 = 600 Pr zy k <unk> a dow e  z d ani e  w  j <unk> zy ku  pol s kim ,  <unk> ó <unk>  </s>
```

### bigcode/starcoder2-15b

```
Vocab length: 49152

 English  and  CAPITAL IZATION 
 � � �  � � �     � � 
 show _ tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         " 
 1 2 . 0 * 5 0 = 6 0 0 
 Pr zy k ł adow e  z d anie  w  j ę zy ku  pol sk im ,  ż ó ł ć 
```

### microsoft/Phi-3-mini-4k-instruct

```
Vocab length: 32011
 
 English and C AP IT AL IZ ATION 
 � � � �  � � � �   � � � 
 show _ to kens False None elif == >= else : two tabs :"    " Three tabs : "       " 
 1 2 . 0 * 5 0 = 6 0 0 
 Pr zyk ład owe zd anie w j ę zy ku pol skim , ż ół ć 
```

### Qwen/Qwen2-VL-7B-Instruct

```
Vocab length: 151657

 English  and  CAPITAL IZATION 
 🎵  � � �    � � � 
 show _tokens  False  None  elif  ==  >=  else :  two  tabs :"      "  Three  tabs :  "         "
 1 2 . 0 * 5 0 = 6 0 0 
 Pr zy k ł adow e  zd anie  w  języ ku  pol sk im ,  ż ół ć 
```

### xlm-roberta-large

```
Vocab length: 250002
<s> English and CAP ITA LIZA TION  🎵  <unk>  鸟 show _ tok ens Fal se No ne el if  == > = else : two tab s : " " Three tab s : " " 1 2.0 * 50 = 600 Przy kład owe z danie w język u polskim ,  żół ć </s> 
```

## EN