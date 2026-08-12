# Defect Metrics Definition

These initial metrics support consulting learning, not individual performance scoring. The goal is **not** to suppress or artificially reduce defect counts. The goal is earlier, more reliable detection with shorter escape distance and less rework. Report the observation window, filters, count, and denominator with every result.

## Ordered SDLC phases

Use this zero-based order for `origin`-to-detection calculations:

| Index | Phase |
| ---: | --- |
| 0 | `requirements` |
| 1 | `architecture-design` |
| 2 | `implementation` |
| 3 | `unit-verification` |
| 4 | `integration-verification` |
| 5 | `acceptance-review` |
| 6 | `release-production` |
| 7 | `retrospective` |

Map interface design to `architecture-design`, configuration creation to `implementation`, and documentation to the phase in which that document was authored or approved. Leave phase-dependent metrics blank when origin cannot yet be supported by evidence.

## Core metrics

### Total Defects Found

Count distinct `defect_id` values detected in the reporting window. Count only evidence-backed discrepancies; investigations with no discrepancy and rows with `status = invalid` are excluded.

### Upstream Defects Found

Count defects whose `origin` is `requirement`, `architecture-design`, `interface-integration`, or authoritative `documentation-context`, rather than implementation or verification. Report count and percentage of total defects.

### Defect Escape Distance

The number of phase boundaries crossed before detection:

`escape_distance = index(detected_phase) - index(origin_phase)`

Zero means detection in the phase of origin. Do not use negative values; re-evaluate the classification instead. Report distribution and median as well as the mean so outliers remain visible.

### Ambiguity Defects

Count defects with type `ambiguity`, `scope-boundary-ambiguity`, `architectural-ambiguity`, or a documented materially ambiguous interface/contract cause. Rate is that count divided by Total Defects Found for the same window. Mere lack of familiarity is not ambiguity.

### AI-Correct / Specification-Wrong Defects

Count rows where `ai_correct_spec_wrong = true`. Use true only when evidence shows that AI output reasonably and faithfully followed the supplied authoritative specification or architecture, yet that source was itself defective. Do not use it merely because AI-generated code is wrong, a prompt omitted available authority, or the implementation selected an unreasonable interpretation.

### AI Context Corrections

Count rows where `ai_context_update_required = true` after the affected repository's authoritative requirement or architecture was resolved. This records required corrections, not every editorial change to `AI_CONTEXT.md`. A non-defect journal discovery may be reported separately with a linked change; do not fabricate a defect solely to count it.

### Rework Actual

Total decimal person-hours spent diagnosing, correcting, verifying, and reconciling the defect. Keep `rework_actual_hours` numeric. Prefer measured time; when it is conservatively estimated, set `rework_actual_is_estimate = true` and state the method in notes.

### Rework Avoided

Conservative estimated person-hours of additional downstream correction avoided because detection occurred before a later phase. Keep the numeric estimate in `rework_avoided_estimate_hours`; the column name makes its estimated nature explicit. Never present it as measured savings. State the assumed later phase and basis in notes. Leave blank when no defensible estimate exists.

## Distributions

### Detection Method Distribution

Group counts and percentages by `detection_method`. Initial controlled values are:

- `human-implementation-review`
- `human-pr-review`
- `chatgpt-architecture-review`
- `codex`
- `github-actions-ci`
- `unit-testing`
- `integration-testing`
- `e2e-acceptance-testing`
- `retrospective-audit`

Choose the method that first produced sufficient evidence, not every method that later confirmed it.

### Detection Phase Distribution

Group counts and percentages by `detected_phase` using the ordered phase names above. Compare like-for-like reporting windows to see whether discovery moves earlier. Interpret higher counts alongside coverage and escape distance: more early findings may indicate better detection, not worsening quality.
