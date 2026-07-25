# Historical Project: "Alpha" E-Commerce Replatform (Lessons Learned)

Methodology used: Hybrid (Waterfall governance + Agile execution).
Duration: 5 months. Team size: 8.

Lessons learned:
- Underestimated third-party payment gateway integration by ~40% - add a fixed
  1.5x multiplier to estimated_duration() for tasks mentioning "integration"
  with an external vendor.
- Resource bottleneck on QA in the final two sprints; recommend allocating a
  dedicated QA resource from Sprint 1, not just before UAT.
- Weekly Teams status updates (vs. bi-weekly) correlated with earlier
  detection of schedule slippage in the retrospective survey.

Risk log highlights: payment gateway compliance review (materialized, +2 weeks
delay), key engineer unavailability during a critical sprint (materialized,
mitigated via contractor reassignment approved by PM within 24h).
