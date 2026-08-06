# Requirements Traceability Matrix

## Vision goals

| ID | Derived vision goal |
| --- | --- |
| VG-01 | Repeatable, tailorable engagement practice |
| VG-02 | Evidence-supported, transparent conclusions |
| VG-03 | Symptoms-to-causes-to-options-to-recommendations reasoning |
| VG-04 | Reconciled executive/technical communication and actionable plans |
| VG-05 | Baseline-based follow-up and outcome learning |
| VG-06 | Human authority and governed recommendation-to-action |
| VG-07 | Modular, maintainable reusable consulting knowledge |
| VG-08 | Clear repository boundaries and traceable portfolio work |
| VG-09 | Confidentiality, minimization, and deliberate transfer |
| VG-10 | Bounded, reviewable AI and target execution |

## Matrix

“AC” references the acceptance criteria of the listed functional requirements.
`FT-*` identifiers reserve future test cases; they are specifications for the
test-design phase, not current test implementations.

| Vision | Business objective | Functional requirements | Nonfunctional requirements | Acceptance evidence | Future tests |
| --- | --- | --- | --- | --- | --- |
| VG-01 | BO-01 | FR-ENG-01–03, FR-EVD-03, FR-KM-01 | NFR-PERF-01, NFR-USA-01, NFR-DOC-01 | FR AC; tailored pilot completion and rationale | FT-ENG-01 core happy path; FT-ENG-02 tailoring contrast; FT-ENG-03 authority gap; FT-USA-01 asset discovery |
| VG-02 | BO-02 | FR-EVD-01–04, FR-ASMT-03, FR-ANL-01 | NFR-REL-01, NFR-AI-02, NFR-MNT-03 | Evidence/trace audit; unsupported-finding rejection | FT-EVD-01 provenance types; FT-EVD-02 contrary evidence; FT-EVD-03 insufficiency; FT-ASMT-01 false precision |
| VG-03 | BO-03 | FR-ASMT-01–03, FR-ANL-01–03, FR-REC-01 | NFR-TST-01, NFR-DOC-01 | End-to-end reasoning-chain review | FT-ANL-01 symptom/cause; FT-ANL-02 correlation warning; FT-ANL-03 options/status quo; FT-REC-01 transparent ranking |
| VG-04 | BO-03, BO-04 | FR-REC-01, FR-ROAD-01, FR-RPT-01 | NFR-ACC-01, NFR-USA-01, NFR-PORT-01 | Cross-audience reconciliation and roadmap completeness | FT-RPT-01 reconciled views; FT-RPT-02 contradiction rejection; FT-ROAD-01 ownership/dependency; FT-ACC-01 document audit |
| VG-05 | BO-05 | FR-ASMT-01, FR-FU-01 | NFR-REL-01, NFR-CFG-01 | Comparable baseline/follow-up review | FT-FU-01 comparable measure; FT-FU-02 changed context; FT-FU-03 missing baseline |
| VG-06 | BO-03, BO-04, BO-06 | FR-ENG-03, FR-DEC-01, FR-ROAD-01, FR-HO-01 | NFR-AUTO-02, NFR-AI-01 | Authority audit and governed handoff walkthrough | FT-DEC-01 approve/reject/defer; FT-DEC-02 unauthorized actor; FT-HO-01 complete package; FT-HO-02 no implicit authorization |
| VG-07 | BO-01, BO-05 | FR-KM-01–02 | NFR-MNT-01–03, NFR-SCL-01, NFR-DOC-01–02 | Catalog audit, change/deprecation review, scale corpus | FT-KM-01 publish asset; FT-KM-02 missing owner; FT-KM-03 deprecate/history; FT-SCL-01 catalog scale |
| VG-08 | BO-04, BO-06 | FR-HO-01, FR-EXE-01–02 | NFR-INT-01, NFR-DEP-01–02, NFR-AUTO-01–02 | Interface contract tests and boundary review | FT-INT-01 one target/task; FT-INT-02 incompatible contract; FT-INT-03 external outage; FT-EXE-01 wrong target |
| VG-09 | BO-02, BO-06 | FR-EVD-01–02, FR-HO-01, FR-KM-02, FR-SEC-01–02 | NFR-SEC-01–03, NFR-CMP-01, NFR-OBS-01 | Data-flow threat model and classification/transfer audit | FT-SEC-01 unknown classification; FT-SEC-02 minimum transfer; FT-SEC-03 destination-specific consent; FT-SEC-04 secret scan |
| VG-10 | BO-06 | FR-SEC-02, FR-EXE-01–02 | NFR-REL-02, NFR-OBS-01–02, NFR-TST-02, NFR-AI-01–02 | AI review audit and target execution regression suite | FT-AI-01 fabricated fact; FT-AI-02 provenance/review; FT-EXE-02 verify nonmutation; FT-EXE-03 revoked approval; FT-EXE-04 redelivery; FT-EXE-05 ambiguity/no merge |

## Interface and use-case coverage

| Artifact | Covered requirements | Future contract/scenario tests |
| --- | --- | --- |
| Interface-Organization-Control-Plane | FR-EXE-01–02; NFR-INT-01, NFR-OBS-01–02 | FT-CP-01 valid request/result; FT-CP-02 unsupported version; FT-CP-03 sanitized failure; FT-CP-04 rollback compatibility |
| Interface-Portfolio-Tasks | FR-HO-01, FR-EXE-01; NFR-AUTO-02 | FT-PT-01 handoff/ack; FT-PT-02 duplicate; FT-PT-03 state revoked; FT-PT-04 classification conflict |
| Interface-Slugger | FR-HO-01, FR-SEC-02; NFR-INT-01 | FT-SLG-01 boundary review; future provider/consumer tests only after contract validation |
| UC-01–03 | FR-ENG, FR-EVD, FR-ASMT | FT-E2E-01 framed assessment with limitation |
| UC-04–07 | FR-ANL, FR-REC, FR-DEC, FR-RPT, FR-ROAD, FR-HO, FR-FU | FT-E2E-02 reasoning through follow-up; FT-E2E-03 rejected recommendation |
| UC-08–10 | FR-KM, FR-SEC, FR-EXE | FT-E2E-04 safe lesson; FT-E2E-05 bounded AI execution |

## Traceability maintenance rules

1. No mandatory requirement may be accepted without a vision/business link,
   acceptance criterion, planned positive test, and planned negative test.
2. A test result SHALL record requirement ID, baseline/contract version, fixture
   or scenario, environment, outcome, evidence link, date, and reviewer.
3. Changes to a vision goal, BO, FR, NFR, interface, or acceptance criterion SHALL
   update affected rows in the same change.
4. Coverage does not prove fitness: stakeholder validation and professional
   review remain necessary.
