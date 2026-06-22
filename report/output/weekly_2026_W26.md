## Executive Summary
Overall ROCm library health is mixed: issue closure rates remain high across all repos, but CI pass rates are critically low for rccl and hip. Bus factor risks are elevated in rocSPARSE and rocFFT, while PR cycle times are generally healthy.

## Key Findings
- **ROCm/hip**: 7 open issues (avg 556 days to close), 30 open PRs (avg 10.4 days cycle), CI pass rate 0.0% (0/1 runs passed).
- **ROCm/MIOpen**: 3 open issues (avg 392 days), 6 open PRs (avg 12.9 days), bus factor 33.7% (lowest risk).
- **ROCm/rccl**: 0 open issues, 7 open PRs (avg 7.1 days), CI pass rate 23.4% (11/47 passed), bus factor 41.4%.
- **ROCm/rocSPARSE**: 0 open issues, 1 open PR (avg 3.5 days), bus factor 81.3% (highest risk).
- **ROCm/rocFFT**: 0 open issues, 3 open PRs (avg 4.1 days), bus factor 52.7%.
- **ROCm/rocBLAS**: 0 open issues, 0 open PRs (avg 2.2 days cycle), bus factor 45.0%.

## Risk Flags 🚨
1. **CI failures in rccl and hip**: rccl pass rate 23.4% (36/47 runs failed); hip pass rate 0.0% (0/1 passed). Both block release confidence.
2. **Bus factor crisis in rocSPARSE**: top 3 contributors own 81.3% of commits—single point of failure risk.
3. **Aging issues in hip**: 7 open issues with average 556 days to close indicates chronic triage delays.

## Recommendations
1. **Immediate CI investigation**: rccl and hip teams must prioritize CI pipeline fixes this week. Escalate to DevOps if needed.
2. **Knowledge transfer for rocSPARSE**: schedule cross-training sessions to reduce bus factor from 81.3% to below 60% within 30 days.
3. **Issue triage for hip**: assign dedicated engineer to resolve or close the 7 open issues; target 30-day resolution.

## Positive Signals ✅
- **Zero open issues** in rccl, rocSPARSE, rocFFT, and rocBLAS—strong closure discipline.
- **Fast PR cycle times**: rocBLAS averages 2.2 days, rocSPARSE 3.5 days, rocFFT 4.1 days—excellent throughput.