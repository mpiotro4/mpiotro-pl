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

ORM (Object-Relational Mapping) to technika programowania, która pozwala mapować encje z bazy danych na obiekty, aby uniknąć używania surowego SQL na każdym kroku. W przypadku Javy najpopularniejszym ORM-em jest Hibernate, lecz wraz z nim pojawiają się tajemnicze słowa i skróty, min. takie jak JPA, JPQL czy HQL. Przez lata używałem Hibernate'a na zasadzie "jakoś to działa" i nigdy nie zadałem sobie trudu, aby solidnie uporządkować sobie wiedzę na temat wszystkich tych pojęć. Ten wpis ma na celu to zmienić.

Zacznijmy od wysokopoziomowego podsumowania, gdzie w dalszej części wpisu po kolei zostanie omówiony każdy element. ORM w Javie można przedstawić w postaci poniższego łańcucha:
**JPA (Standard) → Hibernate (Implementacja) → EntityManager/Session (API do rozmowy) → JPQL/HQL/Criteria API (Język zapytań)**
## JPA (Java Persistence API)

Wszystko zaczyna się od JPA, czyli Java Persistence API. Jest to interfejs będąca częścią Javy od 2006 roku, która ma na celu ustandaryzować zarządzanie relacyjnymi danymi w aplikacjach. JPA nie jest biblioteką, lecz zestawem interfejsów i reguł, które definiują jak powinien działać ORM.

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

> Kod źródłowy do tego wpisu dostępny jest w [repozytorium github]( https://github.com/mpiotro4/HibernatePlayground/tree/blog/2025-12-22-hibernate)

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

## EN

## Introduction

ORM (Object-Relational Mapping) is a programming technique that allows mapping database entities to objects, in order to avoid writing raw SQL at every step. In Java, the most popular ORM is Hibernate, but along with it come mysterious words and abbreviations, such as JPA, JPQL, or HQL. For years I used Hibernate on a "somehow it works" basis and never took the time to properly organize my knowledge of all these concepts. This post aims to change that.

Let's start with a high-level summary, where each element will be discussed in detail further in the post. ORM in Java can be represented as the following chain:
**JPA (Standard) → Hibernate (Implementation) → EntityManager/Session (Communication API) → JPQL/HQL/Criteria API (Query Language)**

## JPA (Java Persistence API)

Everything starts with JPA, or Java Persistence API. It is an interface that has been part of Java since 2006, with the goal of standardizing the management of relational data in applications. JPA is not a library, but a set of interfaces and rules that define how an ORM should work.

JPA introduces key annotations such as `@Entity`, `@Table`, and `@Id`:
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

Hibernate is the most popular implementation of the JPA standard. Red Hat released it in 2001 — before JPA even existed! It turned out to be so popular that when the JPA specification was being created in 2006, it was largely modeled after Hibernate.

What does Hibernate do?

* Implements all JPA interfaces (including `EntityManager`, `CriteriaBuilder`)
* Translates operations on objects into SQL queries
* Manages the lifecycle of objects (persistent, detached, transient)
* Optimizes performance (caching, lazy loading, batch processing)

Additional capabilities beyond JPA:

* Session API - older Hibernate interface (alternative to `EntityManager`)
* HQL (Hibernate Query Language) - extension of JPQL with additional features
* Custom data types
* Advanced caching strategies (first-level, second-level cache)

## API for communicating with the database

> The source code for this post is available in the [GitHub repository](https://github.com/mpiotro4/HibernatePlayground/tree/blog/2025-12-22-hibernate)

There are two implementations of the API for communicating with the database — **EntityManager** (JPA) and **Session** (Hibernate). Both are objects through which database operations are performed. They act as a bridge between Java code and database tables.

### EntityManager (JPA standard)
```java
EntityManager em = entityManagerFactory.createEntityManager();

// Begin transaction
em.getTransaction().begin();

// Save object to database
Person person = new Person();
person.setFirstName("Jan");
em.persist(person);

// Retrieve object from database
Person found = em.find(Person.class, 1L);

// Commit transaction
em.getTransaction().commit();
em.close();
```

### Session (Hibernate API)
```java
Session session = sessionFactory.openSession();

// Begin transaction
session.beginTransaction();

// Save object to database
Person person = new Person();
person.setFirstName("Jan");
session.save(person);

// Retrieve object from database
Person found = session.get(Person.class, 1L);

// Commit transaction
session.getTransaction().commit();
session.close();
```

Differences:

* EntityManager - JPA standard, portable between implementations
* Session - Hibernate-specific, provides access to additional Hibernate features

In modern applications (especially with Spring), EntityManager is more commonly used because it is the standard. You'll encounter Session in older projects or when a project consciously uses advanced Hibernate features.

## Query Languages

When you need more complex operations than simple `find()` or `persist()`, you use query languages. You have four approaches to choose from:

### 1. JPQL (Java Persistence Query Language) - JPA standard

SQL-style queries, but you operate on objects and fields instead of tables and columns:
```java
List<Person> adults = em.createQuery(
    "SELECT p FROM Person p WHERE p.age >= 18", 
    Person.class
).getResultList();
```

Note: `Person` is the class name, not the table name. `age` is the object field, not the column.

### 2. HQL (Hibernate Query Language) - JPQL extension

Works identically to JPQL, but has additional Hibernate-specific capabilities:
```java
List<Person> adults = session.createQuery(
    "FROM Person p WHERE p.age >= 18", 
    Person.class
).list();
```

HQL is fully compatible with JPQL — every JPQL query will work in HQL.

### 3. Criteria API - programmatic query building

Type-safe alternative to string-based queries, ideal for dynamic filters:
```java
CriteriaBuilder cb = em.getCriteriaBuilder();
CriteriaQuery<Person> query = cb.createQuery(Person.class);
Root<Person> person = query.from(Person.class);

query.select(person)
     .where(cb.ge(person.get("age"), 18));

List<Person> adults = em.createQuery(query).getResultList();
```

When to use Criteria API? When you're building a query dynamically at runtime — e.g. a search form where the user can choose different combinations of filters.

### 4. Native SQL - plain SQL

You can use plain SQL when you need:
```java
List<Person> adults = em.createNativeQuery(
    "SELECT * FROM persons WHERE age >= 18", 
    Person.class
).getResultList();
```

When to use raw SQL?

* Database-specific features (e.g. PostgreSQL JSONB)
* Performance optimization for complex queries
* Legacy - you already have ready, tested SQL queries
* Bulk operations on large amounts of data

Practical choice:

* Simple queries → JPQL
* Dynamic filters → Criteria API
* Advanced Hibernate features → HQL
* Full control or DB-specific features → Native SQL

## Summary

ORM in Java is a system that allows working with databases through objects instead of SQL. It is based on a four-layer architecture.
JPA is the standard defining how ORM should work — it introduces annotations (`@Entity`, `@Id`) and interfaces. This makes the code portable between implementations.
Hibernate is the most popular JPA implementation that realizes these interfaces. In practice it holds ~95% of the market and is the de facto standard in Java projects.
EntityManager (JPA) and Session (Hibernate) are the APIs through which you perform database operations — saving, retrieving, and updating data.
Query languages provide different ways of fetching data: JPQL (JPA standard, strings on objects), HQL (Hibernate extension), Criteria API (type-safe, dynamic queries), and raw SQL (full control when ORM isn't enough).