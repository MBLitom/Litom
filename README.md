# MB Litom

MB Litom is a professional AI-accelerated software development studio website and future client platform.

The product direction is a serious B2B system for project requests, proposals, approvals, deposit and milestone payment requests, project tracking, and delivery. This repository starts as a Django monolith so the public website and client portal can grow from one maintainable codebase.

## Stack

- Python
- Django 5.x
- PostgreSQL
- Redis
- Docker and Docker Compose
- Tailwind CSS later
- HTMX or Alpine.js later where useful
- Paysera Checkout later

## Local Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Start the local services:

```bash
docker compose up --build
```

Open the website:

```text
http://localhost:8010/
```

Admin is available at:

```text
http://localhost:8010/admin/
```

Healthcheck is available at:

```text
http://localhost:8010/health/
```

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

Create an admin user:

```bash
docker compose exec web python manage.py createsuperuser
```

## Useful Commands

Validate Django configuration:

```bash
python manage.py check
```

Validate Docker Compose configuration:

```bash
docker compose config
```

Run Django commands in Docker:

```bash
docker compose exec web python manage.py check
```

Stop services:

```bash
docker compose down
```

## Project Structure

```text
config/          Django project settings and URL configuration
apps/core/       Shared core utilities and healthcheck route
apps/website/    Public marketing website
apps/accounts/   Future authentication and account ownership
apps/clients/    Future client portal features
apps/projects/   Future project requests, proposals, milestones, and delivery tracking
apps/payments/   Future Paysera-backed payment request flows
templates/       Shared and app templates
static/          Static assets
media/           User-uploaded media in local development
```

## Next Milestones

- Add Tailwind CSS build pipeline.
- Add project request intake flow.
- Add accounts and client portal authentication.
- Model proposals, approvals, milestones, and payment requests.
- Integrate Paysera Checkout after the proposal and payment-request flow is designed.
- Prepare production deployment settings for Cloudflare and Hetzner.
