# Contributing to AI-Powered Misinformation Defense Platform

We welcome contributions to the AI-Powered Misinformation Defense Platform! This document provides guidelines for contributing to the project.

## 🌟 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug reports and fixes**
- **Feature requests and implementations**
- **Documentation improvements**
- **Code quality improvements**
- **Testing and test coverage**
- **Translations and multilingual support**
- **Performance optimizations**
- **Security improvements**

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork locally

git clone https://github.com/YOUR_USERNAME/misinformation-defense.git
cd misinformation-defense

# Add the original repository as upstream
git remote add upstream https://github.com/original-org/misinformation-defense.git
```

### 2. Set Up Development Environment

Follow our [Setup Guide](SETUP_GUIDE.md) to set up your local development environment.

```bash
# Quick setup
make setup-new-dev

# Start development environment
make dev
```

### 3. Create a Branch

```bash
# Create and switch to a new branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 📝 Development Guidelines

### Code Style

#### Backend (Python)

We use the following tools for code quality:

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Or use make commands
make format-backend
make lint-backend
```

**Style Guidelines:**
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused (< 50 lines preferred)
- Use meaningful variable and function names

#### Frontend (TypeScript/React)

```bash
# Format and lint
npm run lint
npm run format

# Type checking
npm run type-check

# Or use make commands
make format-frontend
make lint-frontend
```

**Style Guidelines:**
- Use TypeScript for all new files
- Follow React best practices and hooks patterns
- Use proper component naming (PascalCase)
- Implement proper error boundaries
- Write accessible components (ARIA labels, semantic HTML)

### Testing

#### Backend Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Test specific files
pytest tests/test_api.py -v
```

**Testing Guidelines:**
- Write unit tests for all business logic
- Include integration tests for API endpoints
- Mock external services (Vertex AI, Firestore, etc.)
- Aim for >80% code coverage
- Use descriptive test names

#### Frontend Tests

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Component tests
npm run test:components
```

**Testing Guidelines:**
- Test user interactions and workflows
- Test component rendering and state changes
- Mock API calls and external dependencies
- Test accessibility features
- Include visual regression tests for UI components

### Documentation

- Update README.md for significant changes
- Add/update API documentation in OpenAPI format
- Include inline code comments for complex logic
- Update setup guides for new dependencies
- Write clear commit messages

## 🐛 Bug Reports

When reporting bugs, please include:

### Bug Report Template

```markdown
## Bug Description
A clear description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Submit '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Windows 11, macOS 13, Ubuntu 22.04]
- Browser: [e.g. Chrome 120, Firefox 119]
- Node.js version: [e.g. 18.17.0]
- Python version: [e.g. 3.11.5]

## Screenshots
If applicable, add screenshots to help explain the problem.

## Additional Context
Any other context about the problem here.
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
A clear description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve?

## Proposed Solution
Describe how you envision this feature working.

## Alternative Solutions
Other approaches you've considered.

## Impact
Who would benefit from this feature and how?

## Implementation Notes
Any technical considerations or suggestions.
```

## 📋 Pull Request Process

### 1. Pre-submission Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No merge conflicts with main branch
- [ ] PR description clearly explains changes

### 2. Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots
If applicable, add screenshots of UI changes.

## Related Issues
Closes #[issue number]

## Additional Notes
Any additional information or context.
```

### 3. Review Process

1. **Automated Checks**: Ensure all CI/CD checks pass
2. **Code Review**: At least one maintainer will review your code
3. **Testing**: Verify that tests pass and functionality works
4. **Documentation**: Check that documentation is updated
5. **Approval**: Maintainer approval required before merging

## 🔒 Security

### Reporting Security Issues

**DO NOT** report security vulnerabilities through public GitHub issues.

Instead:
1. Email security concerns to: [security@example.com]
2. Include "SECURITY" in the subject line
3. Provide detailed description of the vulnerability
4. Include steps to reproduce if applicable

### Security Guidelines

- Never commit sensitive information (API keys, passwords, etc.)
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication and authorization
- Follow OWASP security guidelines

## 🌍 Internationalization

We welcome contributions for multilingual support:

### Adding New Languages

1. **Backend**: Add language support to translation service
2. **Frontend**: Add translation files to `frontend/locales/`
3. **Documentation**: Translate key documentation
4. **Testing**: Include tests for new language support

### Current Language Support

- **Primary**: English (en)
- **Secondary**: Hindi (hi)
- **Planned**: Bengali (bn), Telugu (te), Tamil (ta), Marathi (mr), Kannada (kn)

## 📊 Performance Guidelines

### Backend Performance

- Optimize database queries
- Implement proper caching strategies
- Use async/await for I/O operations
- Monitor API response times
- Implement rate limiting

### Frontend Performance

- Optimize bundle size
- Implement code splitting
- Use proper image optimization
- Minimize re-renders
- Implement proper loading states

## 🎯 Roadmap and Priorities

### Current Priorities

1. **Core functionality**: Improving accuracy of misinformation detection
2. **User experience**: Enhancing frontend interface and usability
3. **Performance**: Optimizing response times and scalability
4. **Multilingual support**: Adding support for more Indian languages
5. **Educational content**: Expanding learning modules and explanations

### How to Align Contributions

- Check existing issues and PRs before starting work
- Discuss major changes in GitHub Discussions
- Follow the project roadmap priorities
- Ask questions if unsure about implementation approach

## 🏆 Recognition

### Contributors

We recognize contributions in several ways:

- **GitHub Contributors**: Automatic recognition in repository
- **Release Notes**: Major contributors mentioned in releases
- **Documentation**: Contributors section in README
- **Community**: Recognition in community discussions

### Becoming a Maintainer

Regular contributors may be invited to become maintainers based on:

- Consistent, quality contributions
- Understanding of codebase and architecture
- Positive community interaction
- Alignment with project goals and values

## 📞 Community and Support

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code reviews and technical discussions

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and professional
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect different viewpoints and experiences
- Report inappropriate behavior to maintainers

### Getting Help

If you need help with contributions:

1. Check existing documentation and setup guides
2. Search existing issues and discussions
3. Ask questions in GitHub Discussions
4. Reach out to maintainers for guidance

## 📚 Additional Resources

### Technical Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Project Roadmap](roadmap.md)

### Learning Resources

- [Clean Code Principles](https://github.com/ryanmcdermott/clean-code-javascript)
- [React Best Practices](https://react.dev/learn)
- [Python Best Practices](https://realpython.com/python-code-quality/)
- [API Design Guidelines](https://github.com/microsoft/api-guidelines)

---

**Thank you for contributing to the fight against misinformation! 🛡️**

Your contributions help build a more informed and digitally literate society. Every bug fix, feature addition, and documentation improvement makes a difference in our mission to combat misinformation effectively.

For questions about contributing, please reach out through GitHub Discussions or create an issue.
