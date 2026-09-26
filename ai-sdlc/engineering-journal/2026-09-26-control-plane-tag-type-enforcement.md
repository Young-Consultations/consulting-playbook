# Engineering Journal: control-plane tag-type enforcement

**Date:** 2026-09-26  
**Defect:** DEF-0052  
**Affected repository:** `Young-Consultations/.github`  
**Detection:** automated PR review of publication-attestation PR #79

## What happened

The controlled release procedure requires each published control-plane
`ai-sdlc-vX.Y.Z` tag to be annotated. Candidate PR #78 merged at
`afe09d320268581bc83021cbfc80bf2a0f0bff91`, after which
`ai-sdlc-v2.4.5` was created at that exact commit. Publication-attestation PR
#79 initially recorded the release as published and all exact-head checks were
green.

Copilot review then identified that the Git ref API returned
`object.type: commit`, proving the tag was lightweight rather than annotated.
The release identity pointed to the correct commit, but it did not satisfy the
documented release policy.

## Why the existing gates missed it

The release checks treated "resolves to the reviewed commit" as sufficient
evidence. The lifecycle test used `git rev-list`, target compatibility resolved
the receiver tag to a commit, and Runtime Preflight dereferenced either
lightweight or annotated tags. None of those checks asserted the required tag
object type.

This was an enforcement gap between the authoritative release procedure and
the executable release evidence.

## Repair

PR #79 now adds three fail-closed checks:

1. the release lifecycle test requires
   `git cat-file -t refs/tags/<release>` to return `tag`;
2. the release-aware target verifier requires the published control-plane ref
   object to have type `tag` and then verifies its dereferenced commit matches
   the attested commit;
3. deployed Runtime Preflight rejects a lightweight control-plane release tag.

After the change, exact-head CI fails for the current 2.4.5 tag as intended:
Target Compatibility reports
`published control-plane release tag must be annotated`, and the lifecycle
test reports `commit` instead of `tag`.

## Release decision

PR #79 remains blocked and was converted back to draft. The tag discrepancy
must be resolved through the controlled release process or an explicit
release-owner variance must be recorded before publication attestation can
merge. The source consumer remains on 2.4.4 and no new REAL execution is
authorized.

## SDLC learning

A release policy stated only in documentation is not a release gate. Immutable
identity evidence must validate both *what commit a reference reaches* and any
required properties of the reference itself. For control-plane release tags,
tag type is part of the release contract, not merely Git metadata.
