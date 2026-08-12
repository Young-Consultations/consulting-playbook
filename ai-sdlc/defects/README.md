# Defect Ledger

The [CSV ledger](defect-ledger.csv) is the quantitative source of truth for evidence-backed AI-SDLC defects. A defect is a discrepancy between intended and actual requirements, architecture, interfaces, configuration, workflows, tests, documentation, or implementation. Do not create an entry when an investigation finds no discrepancy.

## Recording a defect

1. Confirm evidence and assign a stable `defect_id`.
2. Classify `origin` and `type` using the [taxonomy](defect-taxonomy.md).
3. Use the controlled values and calculations in the [metrics definition](metrics-definition.md).
4. Add one CSV row; quote fields containing commas, quotes, or line breaks using standard CSV escaping.
5. For an investigation needing narrative detail, copy the [defect template](DEFECT-TEMPLATE.md) and link it from the ledger evidence or notes.

Use ISO 8601 dates (`YYYY-MM-DD`), repository names such as `owner/repository`, URLs or repository-relative paths for references, booleans `true`/`false`, and decimal hours for effort. Leave unknown values blank rather than inventing precision. Update the existing row when status or resolution changes.
