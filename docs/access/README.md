# PolyLab Public Docs Source

This folder contains the source material for the public `/docs` section.

## Source of truth

- Public docs source pages live under [site](./site/).
- Generated static output is written to `frontend_deploy/docs/` and mirrored to `static/docs/`.
- The generator command is:

```bash
python scripts/build_public_docs.py
```

- To verify that generated output is up to date without rewriting files:

```bash
python scripts/build_public_docs.py --check
```

## Purpose

The public docs are written for scanner users and researchers, not for local development setup.

They should explain:

- how to use the scanner effectively
- how to interpret metrics and methodology
- where data freshness and holder logic can mislead
- what the upstream Polymarket sources are
- what PolyLab computes locally
- how the refresh/storage pipeline works
- what is still in progress

## Notes

- Keep public docs aligned with actual implementation behavior.
- Use one prominent implementation-status note on the docs home page plus one compact shared note in the docs layout.
- Prefer explicit implementation detail over vague product copy when the two are in tension.
