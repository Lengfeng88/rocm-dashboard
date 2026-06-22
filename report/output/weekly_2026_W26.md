## Weekly Engineering Health Report (2026-06-22)

## Executive Summary
Overall engineering health is mixed. Issue closure rates remain high across all repos, but CI is critically broken in two key repos. Bus factor risk is elevated in rocSPARSE. PR cycle times are generally healthy.

## Key Findings
- **Issues**: 10 open issues total across 6 repos. HIP has 7 open (avg resolve 556 days). MIOpen has 3 open (avg 392 days). All other repos have 0 open.
- **PRs**: 47 open PRs total. HIP leads with 30 open (avg cycle 10.4 days). rocBLAS has 0 open PRs with fastest cycle (2.2 days).
- **CI**: HIP had 22 runs, 0 passed (0% pass rate). rccl had 48 runs, 12 passed (25% pass rate). Both have severe failures.
- **Bus Factor**: rocSPARSE top 3 contributors account for 84.9% of commits. rocFFT at 53.3%, rocBLAS 45.4%, rccl 43.2%, HIP 40.7%, MIOpen 33.9%.

## Risk Flags 🚨
- **CI Critical Failure**: HIP CI has 0% pass rate (22/22 failed). rccl CI at 25% pass rate (36/48 failed). Both require immediate investigation.
- **Bus Factor High**: rocSPARSE (84.9% top3) is dangerously concentrated. Single contributor loss could halt development.
- **HIP Issue Backlog**: 7 open issues with average 556-day resolution time indicates chronic triage delays.

## Recommendations
1. **CI Recovery**: Escalate HIP and rccl CI failures to DevOps. Assign dedicated engineers to diagnose and fix within 48 hours.
2. **Bus Factor Mitigation**: For rocSPARSE, require code reviews from at least 2 engineers and document critical knowledge areas.
3. **HIP Issue Triage**: Reduce open issues by 50% this month. Assign priority labels and set 30-day resolution targets.

## Positive Signals ✅
- **Zero Open Issues**: rocBLAS, rocFFT, rocSPARSE, rccl all have 0 open issues.
- **Fast PR Cycles**: rocBLAS (2.2 days), rocSPARSE (3.5 days), rocFFT (4.1 days) show excellent throughput.
- **High Merge Volume**: MIOpen (2,242 merged PRs), HIP (2,147), rccl (1,661) demonstrate strong output.