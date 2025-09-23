### Design Overview

- The project uses FastAPI + SQLAlchemy for a clean service-oriented backend.
- The `Person` abstract base model demonstrates abstraction and inheritance; `Student` and `Teacher` extend it.
- Encapsulation is shown via the `full_name` computed property and keeping internal columns private to the model layer.
- Polymorphism is shown by overriding `role_label` in `Student` and `Teacher`.
- Business rules are enforced at the CRUD layer: preventing duplicate enrollments and enforcing course capacity.
- The scraper runs independently and inserts into `scraped_resources` via shared DB models, and can also be imported through API endpoint `/scraped/import`.

### Entities

- `Person (abstract)` -> `Student`, `Teacher`
- `Course (capacity, teacher)`
- `Enrollment (unique student-course)`
- `ScrapedResource (source, title, url, category_or_author, price)`

### Error Handling

- CRUD raises `ValueError` for business rule violations; API converts them to HTTP 400.

### Testing

- Tests cover enrollment rules, API endpoint happy-path, and scraper parsing functions.