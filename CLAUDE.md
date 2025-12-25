# Agent Guidelines for DocHub

This codebase is destined to live for a long time,
with minimal maintenance and to be accessible to junior newcomers.
We minimize the number of dependencies. 
We prefer simple patterns over clever ones.
JavaScript is kept to a minimum, we do not use build steps.
We prefer plain HTML first, hotwire turbo second, hotwire stimulus third and other
JS libs only when necessary

## Commands
- **Run tests**: `uv run pytest` (all tests) or `uv run pytest path/to/test_file.py::TestClass::test_method` (single test)
- **Lint**: `uv run ruff check --fix`
- **Format**: `uv run black .` and `uv run isort .`
- **Type check**: `uv run mypy`
- **Pre-commit**: `uv run pre-commit run --all-files`
- **Database setup**: `make database` (creates test users and sample data)
- **Run server**: `uv run manage.py runserver`

## Code Style
- Use **Black** formatting with **isort** for imports (profile=black)
- Use **Django 6.0** patterns and **Python 3.13** features
- Type hints required (mypy enabled for main modules)
- Use Django's TextChoices for model choices
- Prefer `models.CASCADE` for foreign key deletions
- Use `verbose_name` for user-facing model fields
- Follow Django naming: models in PascalCase, fields/methods in snake_case
- Use `blank=True, default=""` for optional text fields

## Text Tone & User-Facing Content
The application uses a **friendly, informal, student-to-student tone** in all user-facing text:

- **Always use "tu" form** (informal you), never "vous" (formal you)
- **Conversational and approachable** - write like a helpful fellow student
- **Encouraging and supportive** - use phrases like "N'hésite pas" (Don't hesitate)
- **Reassuring in errors** - emphasize it's not the user's fault, we're here to help
- **Community-oriented** - emphasize peer-to-peer sharing and mutual help
- **Positive framing** - even for empty states or errors, maintain warmth
- **Simple, clear language** - avoid technical jargon where possible

Examples:
- "DocHub te permet" not "DocHub vous permet"
- "N'oublie pas" not formal imperatives
- "Ne t'inquiètes pas, le problème vient de notre côté" for errors
- "C'est grâce à des gens comme toi que DocHub est si bien fourni"
