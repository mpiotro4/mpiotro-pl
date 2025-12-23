---
title_pl: "JPA, Hibernate, JPQL, HQL - wyjaśnienie pojęć związanych z ORM w Javie"
title_en: "JPA, Hibernate, JPQL, HQL - Java ORM concepts explained"
date: 2025-12-25
updated: 2025-12-22
author: "Marcin Piotrowski"
tags: ["java", "hibernate", "jpa", "orm", "database"]
description_pl: "Kompleksowe wyjaśnienie ekosystemu ORM w Javie - czym są JPA, Hibernate, EntityManager, Session, JPQL, HQL i Criteria API oraz jak się do siebie mają."
description_en: "Comprehensive explanation of Java ORM ecosystem - what are JPA, Hibernate, EntityManager, Session, JPQL, HQL and Criteria API and how they relate to each other."
---

## PL

## Wstęp

ORM (Object-Relational Mapping) to technika programowania, która pozwala mapować encje z bazy danych na obiekty. Pozwala to uniknąć używania surowego SQL na każdym kroku. W przypadku Javy najpopularniejszym ORM-em jest Hibernate, lecz wraz z nim pojawiają się tajemnicze słowa i skróty, min. takie jak JPA, JPQL czy HQL. Przez lata używałem Hibernate'a na zasadzie "jakoś to działa" i nigdy nie zadałem sobie trudu, aby solidnie uporządkować sobie wiedzę na temat wszystkich tych pojęć. Ten wpis ma na celu to zmienić.

Zacznijmy od wysokopoziomowego podsumowania, gdzie w dalszej części wpisu po kolei zostanie omówiony każdy element łańcucha ORM w Javie.

JPA (Standard) → Hibernate (Implementacja) → EntityManager/Session (API do rozmowy) → JPQL/HQL/Criteria API (Język zapytań)

## JPA (Java Persistence API)

Wszystko zaczyna się od JPA, czyli Java Persistence API. Jest to specyfikacja będąca częścią Javy od 2006 roku, która ma na celu ustandaryzować zarządzanie relacyjnymi danymi w aplikacjach. JPA nie jest biblioteką, lecz zestawem interfejsów i reguł, które definiują jak powinien działać ORM.

JPA wprowadza kluczowe adnotacje takie jak `@Entity`, `@Table`, czy `@Id`:
```java
@Entity
public class Person {
    @Id
    private Long id;
    private String firstName;
    private String lastName;
    private int age;
}
```

## Hibernate

Hibernate to najpopularniejsza implementacja standardu JPA. Firma Red Hat wypuściła go w 2001 roku, czyli jeszcze przed powstaniem JPA! Okazał się być na tyle popularny, że kiedy w 2006 roku tworzono specyfikację JPA, w dużej mierze powstała ona na wzór Hibernate.

Co robi Hibernate?
* Implementuje wszystkie interfejsy JPA (min. `EntityManager`, `CriteriaBuilder`)
* Tłumaczy operacje na obiektach na zapytania SQL
* Zarządza cyklem życia obiektów (persistent, detached, transient)
* Optymalizuje wydajność (caching, lazy loading, batch processing)

Dodatkowe możliwości poza JPA:
* Session API - starszy interfejs Hibernate (alternatywa dla `EntityManager`)
* HQL (Hibernate Query Language) - rozszerzenie JPQL o dodatkowe funkcje
* Własne typy danych
* Zaawansowane strategie cachowania (first-level, second-level cache)

## API do rozmowy z bazą

> Kod źródłowy do tego wpisu dostępny jest w repozytorium github https://github.com/mpiotro4/HibernatePlayground/tree/blog/2025-12-22-hibernate

Istnieją dwie implementacje API do rozmowy z bazą - **EntityManager** (JPA) i **Session** (Hibernate). Oba to obiekty, przez które wykonuje się operacje na bazie danych. Pełnią rolę mostu pomiędzy kodem Java a tabelami w bazie.

### EntityManager (standard JPA)
```java
EntityManager em = entityManagerFactory.createEntityManager();

// Rozpocznij transakcję
em.getTransaction().begin();

// Zapisz obiekt do bazy
Person person = new Person();
person.setFirstName("Jan");
em.persist(person);

// Pobierz obiekt z bazy
Person found = em.find(Person.class, 1L);

// Zakończ transakcję
em.getTransaction().commit();
em.close();
```

### Session (Hibernate API)
```java
Session session = sessionFactory.openSession();

// Rozpocznij transakcję
session.beginTransaction();

// Zapisz obiekt do bazy
Person person = new Person();
person.setFirstName("Jan");
session.save(person);

// Pobierz obiekt z bazy
Person found = session.get(Person.class, 1L);

// Zakończ transakcję
session.getTransaction().commit();
session.close();
```

Różnice:

* EntityManager - standard JPA, przenośny między implementacjami
* Session - specyficzny dla Hibernate, daje dostęp do dodatkowych funkcji Hibernate'a

W nowoczesnych aplikacjach (szczególnie ze Spring) częściej używa się EntityManager, bo jest standardem. Session spotkasz w starszych projektach lub gdy projekt świadomie korzysta z zaawansowanych funkcji Hibernate'a.

## Języki zapytań

Gdy potrzebujesz bardziej złożonych operacji niż proste `find()` czy `persist()`, używasz języków zapytań. Masz do wyboru cztery podejścia:

### 1. JPQL (Java Persistence Query Language) - standard JPA

Zapytania w stylu SQL, ale operujesz na obiektach i polach zamiast tabelach i kolumnach:
```java
List<Person> adults = em.createQuery(
    "SELECT p FROM Person p WHERE p.age >= 18", 
    Person.class
).getResultList();
```

Uwaga: `Person` to nazwa klasy, nie tabeli. `age` to pole obiektu, nie kolumna.

### 2. HQL (Hibernate Query Language) - rozszerzenie JPQL

Działa identycznie jak JPQL, ale ma dodatkowe możliwości specyficzne dla Hibernate:
```java
List<Person> adults = session.createQuery(
    "FROM Person p WHERE p.age >= 18", 
    Person.class
).list();
```

HQL jest w pełni kompatybilny z JPQL - każde zapytanie JPQL zadziała w HQL.

### 3. Criteria API - programistyczne budowanie zapytań

Type-safe alternatywa dla stringowych zapytań, idealna do dynamicznych filtrów:
```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Person> query = cb.createQuery(Person.class);
Root<Person> person = query.from(Person.class);

query.select(person)
     .where(cb.ge(person.get("age"), 18));

List<Person> adults = em.createQuery(query).getResultList();
```

Kiedy używać Criteria API? Gdy budujesz zapytanie dynamicznie w runtime - np. formularz wyszukiwania gdzie użytkownik może wybrać różne kombinacje filtrów.

### 4. Native SQL - czysty SQL

Możesz używać zwykłego SQL gdy potrzebujesz:
```java
List<Person> adults = em.createNativeQuery(
    "SELECT * FROM persons WHERE age >= 18", 
    Person.class
).getResultList();
```

Kiedy używać raw SQL?

* Specyficzne funkcje bazy danych (np. PostgreSQL JSONB)
* Optymalizacja wydajności dla skomplikowanych zapytań
* Legacy - masz już gotowe, przetestowane zapytania SQL
* Bulk operations na dużych ilościach danych

Wybór w praktyce:

* Proste zapytania → JPQL
* Dynamiczne filtry → Criteria API
* Zaawansowane funkcje Hibernate → HQL
* Pełna kontrola lub specyficzne funkcje DB → Native SQL

## Podsumowanie

ORM w Javie to system pozwalający pracować z bazami danych przez obiekty zamiast SQL. Opiera się na czterowarstwowej architekturze.
JPA to standard definiujący jak powinien działać ORM - wprowadza adnotacje (`@Entity`, `@Id`) i interfejsy. Dzięki temu kod jest przenośny między implementacjami.
Hibernate to najpopularniejsza implementacja JPA, która realizuje te interfejsy. W praktyce ma ~95% rynku i jest de facto standardem w projektach Java.
EntityManager (JPA) i Session (Hibernate) to API przez które wykonujesz operacje na bazie - zapisujesz, pobierasz i aktualizujesz dane.
Języki zapytań dają różne sposoby wyciągania danych: JPQL (standard JPA, stringi na obiektach), HQL (rozszerzenie od Hibernate), Criteria API (type-safe, dynamiczne zapytania) i raw SQL (pełna kontrola gdy ORM nie wystarcza).
W praktyce nauka JPA + Hibernate pokrywa większość potrzeb. Reszta to niszowe przypadki lub specyficzne wymagania projektów.

## EN