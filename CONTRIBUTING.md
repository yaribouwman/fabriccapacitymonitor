# Contributing to Fabric Capacity Monitor

Thank you for your interest in contributing to this project. We welcome contributions from consulting companies, Fabric administrators, and the broader community.

## How to Contribute

### Reporting Issues

If you encounter a bug or have a feature request:

1. Check the existing issues to avoid duplicates
2. Open a new issue with a clear title and description
3. Include reproduction steps for bugs
4. For feature requests, explain the use case and expected behavior

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Make your changes following the code style guidelines below
4. Test your changes thoroughly
5. Commit with clear, descriptive messages
6. Push to your fork and open a pull request

### Code Style Guidelines

#### Bicep
- Follow naming conventions in `.cursor/rules/bicep-infra.mdc`
- Use lowercase with hyphens for resource names
- Add comments for non-obvious logic
- Run `az bicep build` to validate syntax

#### Python
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Use async/await for I/O operations
- Add docstrings for public functions
- Run `black` formatter before committing

#### Documentation
- Follow the style guide in `.cursor/rules/documentation.mdc`
- Keep README concise, put details in `docs/`
- Use mermaid diagrams for architecture flows
- Explain "why" not just "what"

## Development Setup

### Prerequisites
- Azure CLI
- Python 3.12+
- Docker (optional, for local testing)
- Git

### Local Development

```bash
git clone https://github.com/yaribouwman/fabriccapacitymonitor.git
cd fabriccapacitymonitor

cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your local database connection
```

### Running Tests

```bash
cd backend
pytest tests/
```

### Building Docker Image

```bash
cd backend
docker build -t fabriccapacitymonitor:local .
```

## Areas for Contribution

We welcome contributions in these areas:

- **Fabric API Integration**: Improvements to data collection from Fabric APIs
- **Frontend Development**: Building a web UI for the monitoring dashboard
- **Alerting**: Adding email/Teams/Slack notifications for capacity issues
- **Documentation**: Improving guides, adding examples, fixing typos
- **Testing**: Adding unit tests, integration tests, end-to-end tests
- **Performance**: Optimizing database queries, API calls, background jobs
- **Security**: Identifying and fixing vulnerabilities

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the MIT license terms

## Questions?

Open a discussion in the GitHub Discussions tab or contact the maintainers via email.
