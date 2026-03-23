1. Code Quality & Structure

Use clear modular structure (separate controllers, services, models, utils)

Follow PEP 8 (use black, isort, flake8)

Use meaningful variable/function names

Avoid hardcoding values → use environment variables (.env)

2. Type Safety

Always use type hints (typing / pydantic)

Enable strict type checking with mypy

3. Error Handling

Never use generic except:

Use specific exceptions and proper logging

Add global error handlers (especially in APIs like FastAPI)

4. Logging

Use logging module instead of print

Configure log levels (INFO, ERROR, DEBUG)

Add structured logs (JSON if possible)

5. Configuration Management

Use pydantic.BaseSettings or dotenv

Separate configs for dev/staging/prod

6. Dependency Management

Use requirements.txt or poetry

Lock versions properly

7. Performance

Use async/await where needed (FastAPI, aiohttp)

Avoid blocking operations

Optimize DB queries (indexes, batching)

8. Security

Validate all inputs (use pydantic)

Never expose secrets in code

Use hashing for passwords (bcrypt)

Protect APIs (JWT, OAuth)

9. Testing

Write unit tests using pytest

Use mocks for external services

Maintain good coverage

10. API Standards (if backend)

Use proper HTTP status codes

Version your APIs (/v1/)

Add OpenAPI/Swagger docs

11. Project Setup

Use virtual environments (venv / poetry)

Add .gitignore

Maintain clean folder structure

12. CI/CD & Build

Run lint + type check + tests before merge

Ensure production build works without manual fixes

13. Use GPU acceleration for model training instead of CPU. The system has an NVIDIA RTX 5060 Ti available—ensure it is properly configured and utilized (CUDA/cuDNN) so all training workloads run on the GPU for optimal performance.

14. Once all development work is completed, ensure both backend and frontend builds run successfully without errors, are properly integrated, and function as expected in a production-ready environment.

15. For Frontend
1. No .tsx file should exceed 200 lines. If it does, break it down into multiple smaller, reusable components, organized inside a folder named after the main component.
2. Use the **`size` attribute** for **MUI Grid** layouts. and import from import Grid from '@mui/material/Grid';
3. Avoid using **SCSS**.
4. Please make sure all things should be absolute responsive
5. Use Formik and Yup for and React Form
6. Use Context API only for deep or global data sharing; otherwise use props with strongly typed interfaces and avoid any, unknown, and misuse of never.
7. Use MUI Components only
8. Add Breadcrumb to all Pages
9. Ensure every table supports pagination, filtering, searching, and sorting, with backend APIs designed accordingly.