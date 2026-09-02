# What is measured and what is not

Six blocks in `figs/data.py` are still estimates. Everything else is your
measured data or is derived from it by arithmetic.

Every estimate below was fixed by a constraint that does **not** depend on an
unmeasured quantity — an identity, a monotonicity, a physical bound, or an
anchor to a real blind-test point. Where an estimate and a sentence in the
paper disagreed, the **sentence** was changed, never the estimate. Reasoning
for each is in the `AUDIT FIX` comments in `figs/data.py`.

| block | figure | anchored to | free assumption to replace |
|---|---|---|---|
| `frontier_object` | 7b | blind test at 25% and 50%, both arms | shape between anchors; arm ordering |
| `age_tail` | 10 | exact periodic and geometric references | how far above geometric the learned tail sits |
| `delta_outcome` | 11 | learned-arm success 124/160 | per-quintile split |
| `wrist` | 12 | real-wrist column = blind test | the two ablation columns |
| `bytes` | 13 | 256×256, 20 Hz, ~110 steps | bits per pixel of your encoder |
| `device` | 14 | 50 ms control period | per-stage latencies |

## The draft switch

Draft mode marks every estimate: a stamp on the panel, red text on the
sentence. It is set by the figure build and read by LaTeX from
`figs/numbers_auto.tex`, so the two can never disagree.

```
make                  # draft: 12 stamps, 10 red claims
ACTDELTA_DRAFT=0 make # clean: 0 stamps  <- only after replacing the blocks
make final            # does the above, and refuses while SYNTH blocks remain
```

`make final` checks tags, not values. Retagging a block without replacing its
numbers will pass. It is a reminder, not a proof.

## Two things to settle against your logs first

1. **`REAL["head"]["op_points"][0]`** — the pooled conditional FNR is now
   21.72%, forced by the median-split identity `miss = 0.5 × FNR` from your
   measured 10.86%. The draft's 47.9% is kept as `median_rate_fnr_l10`, the
   LIBERO-10 value, which is where §8's prose actually puts it. If your logs
   say the pooled FNR is something else, then 10.86% is the wrong number
   instead — one of the two has to move.

2. **Eq. 5** now reads `1[k_t > K_max]`, so the largest reachable age is
   exactly `K_max`. The draft had `≥`, which caps the age at `K_max − 1` and
   makes §11.1's "above seven" unreachable. Match this to your runner.
