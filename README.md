
# BodyForge API

BodyForge API to edukacyjny projekt backendowy napisany w Pythonie z użyciem FastAPI.  
Aplikacja służy do tworzenia profili użytkowników, obliczania BMI, generowania prostych planów treningowych oraz monitorowania postępów użytkownika.

Projekt został przygotowany jako aplikacja backendowa z bazą danych PostgreSQL, autoryzacją JWT oraz uruchamianiem przez Docker Compose.

---

## Spis treści

- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Technologie](#technologie)
- [Struktura projektu](#struktura-projektu)
- [Uruchomienie projektu](#uruchomienie-projektu)
- [Dokumentacja API](#dokumentacja-api)
- [Przykładowy przepływ użycia](#przykładowy-przepływ-użycia)
- [Główne endpointy](#główne-endpointy)
- [Uwagi](#uwagi)

---

## Opis projektu

BodyForge API umożliwia użytkownikowi założenie profilu treningowego na podstawie podstawowych danych, takich jak:

- imię,
- adres e-mail,
- płeć,
- wzrost,
- waga,
- cel treningowy,
- czas trwania celu.

Na podstawie tych danych aplikacja oblicza BMI oraz generuje prosty plan treningowy.  
Użytkownik może później aktualizować wagę, wykonywać kontrolę BMI oraz sprawdzać, czy plan treningowy powinien zostać zmieniony.

Projekt ma charakter edukacyjny i pokazuje podstawowe elementy budowy aplikacji backendowej: REST API, baza danych, autoryzacja, konteneryzacja oraz warstwowa struktura kodu.

---

## Funkcjonalności

Aplikacja posiada następujące funkcje:

- rejestracja użytkownika,
- logowanie użytkownika i generowanie tokenu JWT,
- tworzenie profilu użytkownika,
- obliczanie BMI,
- generowanie planu treningowego,
- pobieranie danych profilu,
- pobieranie aktualnego planu treningowego,
- aktualizacja danych profilu,
- kontrola BMI,
- automatyczne oznaczanie profili wymagających aktualizacji BMI,
- soft delete profilu, czyli dezaktywacja zamiast trwałego usuwania,
- podstawowa obsługa roli administratora.

---

## Technologie

W projekcie wykorzystano:

- Python 3.11,
- FastAPI,
- Uvicorn,
- PostgreSQL,
- SQLAlchemy Core,
- databases,
- asyncpg,
- Docker,
- Docker Compose,
- JWT,
- passlib / bcrypt,
- APScheduler,
- Pydantic.

---

## Struktura projektu

```text
Project_BodyForge1/
│
├── apka/
│   ├── api/
│   │   ├── main.py
│   │   ├── auth.py
│   │   ├── deps.py
│   │   └── routers/
│   │       └── profiles.py
│   │
│   ├── core/
│   │   ├── domain/
│   │   │   ├── models.py
│   │   │   └── enums.py
│   │   ├── repositories/
│   │   │   └── profile_repository.py
│   │   └── services/
│   │       ├── bmi_service.py
│   │       └── planning_service.py
│   │
│   ├── infrastructure/
│   │   ├── repositories/
│   │   │   └── profile_repository_impl.py
│   │   └── services/
│   │       └── scheduler.py
│   │
│   ├── utils/
│   │   ├── bmi.py
│   │   ├── planning.py
│   │   └── security.py
│   │
│   ├── config.py
│   ├── container.py
│   └── db.py
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Uruchomienie projektu

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/twoj-login/Project_BodyForge1.git
cd Project_BodyForge1
```

### 2. Uruchomienie przez Docker Compose

```bash
docker compose up --build
```

Po uruchomieniu aplikacja będzie dostępna pod adresem:

```text
http://localhost:8001
```

Dokumentacja Swagger będzie dostępna pod adresem:

```text
http://localhost:8001/docs
```

---

## Konfiguracja bazy danych

Projekt korzysta z PostgreSQL uruchamianego w kontenerze Docker.

Domyślne dane bazy:

```text
DB_HOST=moja_baza_project1
DB_NAME=bodyforge1
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
```

Port PostgreSQL na komputerze lokalnym:

```text
5433:5432
```

---

## Dokumentacja API

FastAPI automatycznie generuje dokumentację API.

Po uruchomieniu projektu można wejść na:

```text
http://localhost:8001/docs
```

W Swaggerze można testować endpointy, wysyłać dane JSON oraz autoryzować użytkownika tokenem JWT.

---

## Przykładowy przepływ użycia

### 1. Rejestracja użytkownika

Endpoint:

```http
POST /profiles/register
```

Przykładowe dane:

```json
{
  "email": "user@example.com",
  "password": "test123",
  "name": "Jan",
  "gender": "male",
  "height_cm": 180,
  "weight_kg": 82,
  "goal": "recomposition",
  "goal_months": 2,
  "preferred_from_hour": 10,
  "preferred_to_hour": 18
}
```

Dostępne wartości dla `gender`:

```text
male
female
other
```

Dostępne wartości dla `goal`:

```text
lose_weight
gain_muscle
recomposition
```

Po rejestracji aplikacja tworzy profil użytkownika, oblicza BMI oraz generuje pierwszy plan treningowy.

---

### 2. Logowanie

Endpoint:

```http
POST /auth/login
```

Logowanie odbywa się przez formularz OAuth2 w Swaggerze.  
Jako `username` należy podać adres e-mail użytkownika, a jako `password` hasło.

Po poprawnym logowaniu aplikacja zwraca token JWT:

```json
{
  "access_token": "token",
  "token_type": "bearer"
}
```

Token należy dodać w Swaggerze przez przycisk `Authorize`.

---

### 3. Pobranie profilu

Endpoint:

```http
GET /profiles/{profile_id}
```

Endpoint wymaga autoryzacji tokenem JWT.  
Zwykły użytkownik może pobierać tylko własny profil, a administrator może pobierać profile innych użytkowników.

---

### 4. Pobranie aktualnego planu

Endpoint:

```http
GET /profiles/{profile_id}/plan
```

Zwraca ostatnio wygenerowany plan treningowy dla danego profilu.

---

### 5. Kontrola BMI

Endpoint:

```http
POST /profiles/{profile_id}/bmi-check
```

Przykładowe dane:

```json
{
  "weight_kg": 80
}
```

Aplikacja zapisuje nowy pomiar BMI i sprawdza, czy użytkownik robi postęp.  
Jeżeli nie ma postępu, aplikacja może wygenerować nowy plan z większym obciążeniem.

---

## Główne endpointy

| Metoda | Endpoint | Opis |
|---|---|---|
| GET | `/` | Sprawdzenie działania API |
| POST | `/profiles/register` | Rejestracja użytkownika i utworzenie planu |
| POST | `/auth/login` | Logowanie i pobranie tokenu JWT |
| GET | `/profiles/` | Lista aktywnych profili, tylko admin |
| GET | `/profiles/{profile_id}` | Pobranie profilu |
| PUT | `/profiles/{profile_id}` | Aktualizacja profilu |
| DELETE | `/profiles/{profile_id}` | Soft delete profilu |
| GET | `/profiles/{profile_id}/plan` | Pobranie aktualnego planu |
| POST | `/profiles/{profile_id}/bmi-check` | Aktualizacja BMI |
| POST | `/profiles/{profile_id}/restart-program` | Restart programu treningowego |

---

## Autoryzacja

Projekt używa tokenów JWT.

Po zalogowaniu użytkownik otrzymuje token, który jest wymagany do dostępu do chronionych endpointów.

Administrator jest rozpoznawany na podstawie adresu e-mail:

```text
admin@gmail.com
```

Użytkownik z tym adresem ma dostęp do endpointów administracyjnych, np. listy wszystkich aktywnych profili.

---

## Scheduler BMI

W projekcie wykorzystano APScheduler.

Scheduler codziennie sprawdza profile użytkowników i oznacza te, które od co najmniej 14 dni nie miały aktualizacji BMI.  
Takie profile otrzymują flagę:

```text
needs_bmi_update = true
```

Dzięki temu aplikacja może wskazać, że użytkownik powinien ponownie podać swoją wagę.

---

## Soft delete

Usuwanie profilu działa jako soft delete.  
Oznacza to, że profil nie jest fizycznie usuwany z bazy danych, tylko otrzymuje status:

```text
is_active = false
```

Dzięki temu aplikacja nie pokazuje nieaktywnych profili w standardowych zapytaniach.

---

## Ograniczenia projektu

Projekt ma charakter edukacyjny, dlatego niektóre elementy są uproszczone:

- plan treningowy jest generowany w prosty sposób,
- projekt nie zawiera zaawansowanego frontendu,
- sekret JWT jest zapisany w kodzie i w prawdziwej aplikacji powinien być przeniesiony do zmiennych środowiskowych,
- aplikacja nie korzysta z migracji bazy danych,
- logika treningowa i BMI nie powinna być traktowana jako profesjonalna porada medyczna lub trenerska.

---

## Możliwe dalsze rozszerzenia

W przyszłości projekt można rozbudować o:

- frontend w React,
- panel użytkownika,
- panel administratora,
- dokładniejszy generator planów treningowych,
- historię postępów użytkownika,
- wykresy BMI i wagi,
- migracje bazy danych,
- testy jednostkowe i integracyjne,
- obsługę resetowania hasła,
- lepszy system ról użytkowników.

---

## Informacja o charakterze projektu

Projekt został przygotowany w celach edukacyjnych jako aplikacja backendowa do nauki FastAPI, PostgreSQL, Dockera, JWT oraz podstaw architektury warstwowej.

Podczas pracy korzystano z dokumentacji technicznej, materiałów edukacyjnych oraz narzędzi AI jako wsparcia przy analizie błędów, generowaniu pomysłów i dopracowywaniu kodu.

---

## Autor

Raman Vaitsiuk  
Student informatyki  
Uniwersytet Warmińsko-Mazurski w Olsztynie
