# nl-to-sql-generator — interview questions and answers

[README](README.md) · [Project architecture](PROJECT_ARCHITECTURE.md)

Answers below use this repository’s files and implementation. They distinguish existing behavior from suggested extensions; source links let you verify each walkthrough.

## 1. What problem does nl-to-sql-generator address, and what can you demonstrate?

Map a question onto a read-only SELECT. Writes are refused.

I would demonstrate the linked implementation or examples and distinguish that evidence from any planned production features. Start with [`README.md`](README.md).

## 2. How is this repository organized?

- [`src/nl2sql/main.py`](src/nl2sql/main.py): Implementation or supporting configuration.
- [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py): Implementation or supporting configuration.
- [`requirements.txt`](requirements.txt): Implementation or supporting configuration.
- [`src/nl2sql/__init__.py`](src/nl2sql/__init__.py): Implementation or supporting configuration.
- [`tests/test_sql.py`](tests/test_sql.py): Executable checks and regression examples.
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml): GitHub Actions job definitions.
- [`README.md`](README.md): Project explanations or operating notes.

[PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) contains the component diagram and the implementation walkthrough.

## 3. Can you walk through `generate` and explain the decision it makes?

The main walkthrough here is `generate(question)` in [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py#L9).

```python
def generate(question):
    if not isinstance(question, str) or not question.strip():
        raise InputError("question is empty")
    lowered = question.lower()
    if any(word in lowered for word in FORBIDDEN):
        raise InputError("write statements are refused")
    for needle, sql in TABLES.items():
        if needle in lowered:
            return {"sql": sql, "read_only": True}
    raise InputError("no table mapping for that question")
```

The implementation calls `InputError`, `TABLES.items`, `any`, `isinstance`, `question.lower`, `question.strip`. In an interview, trace those calls in execution order using a fixture input.

## 4. What input validation and failure behavior are implemented?

Explicit failure paths include:

- `HTTPException(status_code=422, detail=str(exc))` in [`src/nl2sql/main.py`](src/nl2sql/main.py#L17).
- `InputError('no table mapping for that question')` in [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py#L18).
- `InputError('question is empty')` in [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py#L11).
- `InputError('write statements are refused')` in [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py#L14).

I would test both the condition that reaches each exception and the caller that translates it. An explicit raise does not mean every malformed input or dependency failure is handled.

## 5. Which test would you use to demonstrate correctness?

[`tests/test_sql.py`](tests/test_sql.py#L7) contains `test_select_and_refuse_write`:

```python
def test_select_and_refuse_write():
    payload = client.post("/generate", json={"question": 'errors by service'}).json()
    assert "FROM errors" in payload["sql"]
    assert payload["read_only"] is True
    assert client.post("/generate", json={"question": "delete old rows"}).status_code == 422
```

This is a concrete regression example from the repository. Its assertions establish that case; they do not establish behavior for every input or under production load.

## 6. What HTTP interface does the code expose?

- `GET /healthz` → `healthz` in [`src/nl2sql/main.py`](src/nl2sql/main.py#L8).
- `POST /generate` → `post_generate` in [`src/nl2sql/main.py`](src/nl2sql/main.py#L13).

These are literal decorators. Application/router prefixes, authentication, and middleware must be checked in the corresponding setup code.

## 7. Where does state live, and what happens with multiple workers?

Module-level containers include `TABLES` in [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py).

These containers belong to a Python process. Inspect which are constant fixtures and which are mutated. Mutable process state needs an explicit shared-storage or synchronization strategy before multiple workers can provide consistent behavior.

## 8. How would another engineer reproduce your walkthrough?

Start from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

These commands follow repository manifests; environment setup and command results still need to be checked on the target machine.

## 9. What does automation verify, and what does it not prove?

Inspect [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for triggers, permissions, and job commands. I would name the checks that those definitions run and show the latest run separately. A workflow definition alone does not establish a successful deployment, security review, or production SLO.

## 10. How would you present this project in a Forward Deployed Engineer interview?

Start with the user and operational problem described in [`README.md`](README.md). Explain one constraint that changes the implementation, show the linked code or example, and walk through a success case and a failure case. Agree on a measurable acceptance criterion before expanding the solution, and leave a handoff with data boundaries and rollback ownership. Any proposed production or business metric should be identified as a target until measured.

## 11. What is the input-to-output contract of `generate`?

In [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py#L9), `generate(question)` receives the inputs. The function computes these intermediate values:

- `lowered = question.lower()`

Its result is defined by:

- `{'sql': sql, 'read_only': True}`

## 12. Which decision rules or boundary conditions should an interviewer challenge?

The implementation in [`src/nl2sql/sqlgen.py`](src/nl2sql/sqlgen.py#L9) branches on:

- `not isinstance(question, str) or not question.strip()`
- `any((word in lowered for word in FORBIDDEN))`
- `needle in lowered`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.
