# Product

## Register

product

## Users

GLICOVIA is primarily for patients and general users who need to understand saliva-based glucose monitoring without specialist dashboard literacy. Secondary users include researchers, supervisors, or care-adjacent reviewers who need enough clinical and device context to trust the reading, spot anomalies, and decide what to do next.

Users may be checking health data under mild anxiety, in everyday environments, or during a guided screening/research flow. The interface should make values, categories, device state, and next actions legible without turning the experience into a technical operations console.

## Product Purpose

GLICOVIA presents saliva glucose measurements, predicted blood glucose output, clinical categories, device status, subject/sample history, ingestion, predictions, and analytics in a clear monitoring suite.

Success means a non-expert can quickly understand their current reading and status, while a reviewer can still verify data quality, model context, and anomalies without digging through clutter.

## Brand Personality

Approachable, clear, trustworthy.

The product should feel calm and health-literate: serious enough for health data, but not cold, intimidating, or overloaded. Copy should explain what matters in plain language, avoid alarmist phrasing, and keep clinical precision visible where it supports trust.

## Anti-references

- Not a generic startup SaaS dashboard; avoid decorative gradients, excessive shadows, and marketing-style metric spectacle.
- Not a cluttered hospital EMR; avoid dense, noisy panels where every field competes equally.
- Not a specialist-only analytics tool; avoid unexplained model jargon where patient-facing clarity is needed.
- Not decorative motion; motion must communicate state, progress, or feedback.

## Design Principles

1. Lead with patient comprehension: prioritize the current reading, category, meaning, confidence, and next action over raw instrumentation.
2. Keep clinical trust visible: show data quality, device state, anomaly context, and model/version details where they help users trust the result.
3. Reduce cognitive load: organize information into obvious layers so general users can scan first and reviewers can inspect second.
4. Use restraint as a safety feature: avoid visual effects that make health information feel promotional or less credible.
5. Make states explicit: loading, empty, error, warning, offline, syncing, and abnormal readings should have clear language and consistent visual treatment.

## Accessibility & Inclusion

WCAG AA is required because the product handles health-related data. Body text and controls must meet contrast requirements, focus states must be visible, and color must never be the only indicator of clinical category, warning, or device status.

Reduced motion is the default posture. Animations should be subtle, functional, and avoid unnecessary choreography; all motion must respect `prefers-reduced-motion`.
