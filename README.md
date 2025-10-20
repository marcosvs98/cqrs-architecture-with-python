# cqrs-architecture-with-python
Applying pattern Ports and Adapters + CQRS with Python Fastapi.


## Bounded Contexts

<table>
    <tr>
        <td><strong>Domain:</strong></td>
        <td>Ordering</td>
    </tr>
    <tr>
        <td><strong>Concepts:</strong></td>
        <td>Domain Driven Design (Subdomains, Bounded Contexts, Ubiquitous Language, Aggregates, Value Objects)</td>
    </tr>
    <tr>
        <td><strong>Architecture style:</strong></td>
        <td>Event Driven Microservices</td>
    </tr>
    <tr>
        <td><strong>Architectural patterns:</strong></td>
        <td>Event Sourcing, Hexagonal Architecture and CQRS</td>
    </tr>
    <tr>
        <td><strong>Technology:</strong></td>
        <td>Python with (FastAPI), MongoDB and Redis</td>
    </tr>
</table>

## Domain
Customers use the website application(s) to place orders. Application coordinates order preparation and delivery.

## Sub-domains
- **Order**: This domain is responsible for managing and processing orders placed by customers, including product selection, pricing, and payment completion.
- **Product**: This domain is responsible for managing and providing information about the products available for sale, including descriptions, prices and images.
- **Delivery**: This domain is responsible for managing and tracking deliveries, including scheduling deliveries, tracking carrier location, and processing returns.
- **Maps**: This domain is responsible for providing geographic information including delivery routes, delivery locations and estimated travel time.
- **Payment**: This domain is responsible for processing payments, including credit card authorizations, balance checks and payment confirmations


## Domain model

Sub-domain *software programing* models:

 - [ordering](https://github.com/marcosvs98/hexagonal-architecture-with-python/tree/main/src/domain)

> Domain model is mainly a software programing model which is applied to a specific sub-domain.
> It defines the vocabulary and acts as a communication tool for everyone involved (business and IT), deriving a [Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html).

## Bounded Context

Each of this group of applications/services belongs to a specific bounded context:
- [ordering](https://github.com/marcosvs98/hexagonal-architecture-with-python/tree/main/src/domain) - Order bounded context, with messages serialized to JSON


> A goal is to develop a [Ubiquitous Language](https://martinfowler.com/bliki/UbiquitousLanguage.html) as our domain (sub-domain) model within an explicitly Bounded Context.
> Therefore, there are a number of rules for Models and Contexts
> - Explicitly define the context within which a model applies
> - Ideally, keep one sub-domain model per one Bounded Context
> - Explicitly set boundaries in terms of team organization, usage within specific parts of the application, and physical manifestations such as code bases and database schemas



## Technologies and patterns used

- **Python 3.12**
- **FastAPI (Rest API)**
- **MongoDB**
- **Pydantic 2.5**
- **Redis**
- **CQRS**
- **Ports & Adapters**
- **Event Sourcing**

In addition to others, the main pattern that guides this project is the Ports & Adapter + CQRS. In summary, this pattern provides a way to organize code so that business logic is encapsulated, but separated from the underlying delivery mechanism. This allows for better maintenance and fewer dependencies.

With CQRS, we have a clear separation of concerns, making the codebase easier to understand and maintain.Developers can more easily reason about how changes to the codebase will affect the overall system. Additionally, its use allows each model to evolve independently since they are not strongly coupled. This means changes to one model can be made without affecting the other model.

## Logging

This project uses [structlog](https://www.structlog.org/en/stable/) for structured JSON logging.
Logs include contextual information (timestamp, level, module, line number) and are ready for integration with APM/observability tools.

---
## Running the project

### Option 1 - Via Docker Compose

```bash
docker compose up -d && docker compose logs -f app
```

The Compose stack now provisions MongoDB, Redis, Zookeeper and Kafka. Kafka is used by the
`KafkaDomainEventPublisher` to broadcast domain events emitted by the ordering service. The
application container is pre-configured with `EVENT_PUBLISHER_ENABLED=true` so events are
published automatically in the local environment.

### Option 2 - Via Makefile
```bash
Make build-env
```

### API & Query Endpoints
- `POST /core/v1/orders` — create an order (command side).
- `PATCH /core/v1/orders/{order_id}` — update order status (command side).
- `GET /core/v1/orders/{order_id}` — retrieve an order projection.
- `GET /core/v1/orders` — list order projections with optional filters (`status`, `buyer_id`, `limit`, `offset`).
- `GET /metrics` — lightweight service metrics (uptime) for scraping/observability.
- `GET /` — health probe used by container health checks.

The query endpoints are backed by a dedicated MongoDB projection (`order_projections`) that is
kept in sync through the event store and published events.

### Testing

```bash
poetry install  # ensure dev dependencies are available
make tests      # runs pytest against src/tests/unit
```

A coverage-friendly target is also available via `make test-cov`.

### Environment

The `.env_example` file documents all configurable variables, including the read-model Mongo
connection and Kafka publisher settings. Copy it to `.env` and adjust values as needed:

```bash
cp .env_example .env
```

Key variables:

- `ORDER_REPOSITORY_*` — transactional aggregate store (MongoDB).
- `ORDER_READ_*` — read-model projection store.
- `ORDER_EVENT_STORE_*` — event sourcing collection.
- `EVENT_PUBLISHER_*` — Kafka bootstrap and topic configuration.
- `CACHE_SILENT_MODE` — controls Redis failure behaviour.

## References

- [Hexagonal Architecture](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)
- [Domain Driven Design - DDD](https://lyz-code.github.io/blue-book/architecture/domain_driven_design/)
- [Repository Pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/)
- [Service Layer Pattern](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
