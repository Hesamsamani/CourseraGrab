```markdown
# CourseraGrab Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill provides guidance for contributing to the CourseraGrab Python codebase. It documents the project's coding conventions, commit patterns, and testing approaches, helping developers maintain consistency and quality. The repository does not use a specific framework and follows Pythonic best practices for file naming, imports, and exports.

## Coding Conventions

### File Naming
- Use **snake_case** for all Python filenames.
  - Example: `course_parser.py`, `data_fetcher.py`

### Import Style
- Use **relative imports** within the package.
  - Example:
    ```python
    from .utils import parse_course
    ```

### Export Style
- Use **named exports** (explicitly define what is exported in `__all__`).
  - Example:
    ```python
    __all__ = ['fetch_courses', 'parse_course']
    ```

### Commit Patterns
- Follow **conventional commits** with the prefix `fix`.
- Commit messages are concise (avg. 42 characters).
  - Example: `fix: handle missing course description`

## Workflows

### Code Contribution
**Trigger:** When adding new features or fixing bugs  
**Command:** `/contribute`

1. Create a new branch for your changes.
2. Write code following the coding conventions above.
3. Use relative imports and snake_case filenames.
4. Add or update tests as needed.
5. Commit changes using the `fix:` prefix and a concise message.
6. Push your branch and open a pull request.

### Testing
**Trigger:** Before merging or after making changes  
**Command:** `/test`

1. Identify or create test files matching the pattern `*.test.ts`.
2. Run the test suite (framework is currently unknown; check project documentation or scripts).
3. Ensure all tests pass before merging.

## Testing Patterns

- Test files follow the `*.test.ts` pattern, indicating tests may be written in TypeScript.
- The testing framework is **unknown**; check for project scripts or documentation for details.
- Example test file name: `fetch_courses.test.ts`

## Commands
| Command      | Purpose                                  |
|--------------|------------------------------------------|
| /contribute  | Start the code contribution workflow     |
| /test        | Run the test suite                      |
```
