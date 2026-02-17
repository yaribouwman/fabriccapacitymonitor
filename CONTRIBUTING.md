# Contributing to Fabric Capacity Monitor

This project accepts contributions from consulting companies, Microsoft partners, Fabric administrators, and individual developers.

## Reporting Issues

Bug reports and feature requests:

1. Search existing issues to avoid duplicates
2. Open a new issue with a descriptive title
3. For bugs, include:
   - Azure region and Container App environment
   - Fabric API version (if relevant)
   - Error messages from Container App logs
   - Reproduction steps
4. For feature requests, describe the use case and expected behavior

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature-name`)
3. Follow the code style guidelines below
4. Test changes against a real Azure deployment
5. Validate Bicep templates with `az bicep build`
6. Run Python tests with `pytest` before committing
7. Commit with descriptive messages
8. Push to your fork and open a pull request

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

## Contribution Areas

Current priorities:

**Fabric API Integration**:
- Support for additional metrics beyond capacity state and SKU
- Handle throttling and retry logic for Azure Resource Manager APIs
- Multi-region capacity discovery

**Frontend**:
- Web UI for customer management (currently CLI-only)
- Real-time capacity status dashboard
- Historical metric visualization

**Alerting**:
- Webhook notifications for capacity state changes
- Integration with Teams, Slack, or email
- Configurable threshold-based alerts

**Security**:
- Authentication for customer data endpoints
- PostgreSQL Row-Level Security policies
- Secret rotation automation

**Testing**:
- Integration tests for Azure API interactions
- Load testing for multi-customer scenarios
- Bicep validation in CI/CD pipeline

**Performance**:
- Database query optimization for large metric datasets
- Concurrent collection performance tuning
- Background job scheduling improvements

## Questions

Open an issue for questions about the codebase, architecture, or Azure deployment. For security issues, see `docs/security.md`.
