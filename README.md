# hexagonal-architecture-boilerplate-fastapi
Applying pattern Ports and Adapters with Python Fastapi.


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
        <td>Eventsourcing, Hexagonal Architecture</td>
    </tr>
    <tr>
        <td><strong>Technology:</strong></td>
        <td>Python with (FastAPI) and MongoDB</td>
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

- **Python 3.9**
- **FastAPI (Rest API)**
- **MongoDB**

This project has a structure that aims at the maximum decoupling between layers in order to give
support for creating components that are reusable across the entire business domain. It has a simple User CRUD with
examples of package organization and tests.

In addition to others, the main pattern that guides this project is the Hexagonal (+ Clean Architecture), in short, this pattern
provides a way to organize code so that the business logic is encapsulated, but separate from the underlying engine.
delivery. This allows for better maintenance and fewer dependencies.


---
## Running the project

### Option 1 - Via Docker Compose

#### Run docker-compose

Finally, run the project and its dependencies in the background using the command
```bash
docker-compose up -d
```

## References

- [Hexagonal Architecture](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)
- [Domain Driven Design - DDD](https://lyz-code.github.io/blue-book/architecture/domain_driven_design/)
- [Repository Pattern](https://lyz-code.github.io/blue-book/architecture/repository_pattern/)
- [Service Layer Pattern](https://www.cosmicpython.com/book/chapter_04_service_layer.html)
