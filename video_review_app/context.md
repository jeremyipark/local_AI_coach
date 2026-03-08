# Strength Training Context

This file contains domain knowledge for interpreting deadlift and trap bar deadlift exercise metrics.

**Current scope:** This document is currently scoped to trap bar deadlift analysis. Conventional and sumo deadlift may be added in the future. Until then, do not generalize interpretations beyond the trap bar context unless explicitly noted.

---

# General coaching principles

## Progressive overload
Progressive overload means gradually increasing the training demand over time.

This can happen through:
- more load
- more reps
- more sets
- better rep quality
- greater range of motion
- faster velocity at the same load
- improved consistency across reps
- better fatigue resistance

Progressive overload does **not** always mean adding weight every session. It can also mean:
- cleaner technique
- reduced breakdown
- improved bar speed
- better recovery between sessions
- more stable output across working sets

## Fatigue management
Fatigue management matters because performance can drop within a set, within a session, or across a training block.

Signs of fatigue may include:
- reduced peak velocity
- reduced mean velocity
- reduced power
- slower time to peak velocity
- longer rep duration
- increased positional breakdown
- increased back rounding
- shortened or inconsistent ROM if the lifter changes how they move

Fatigue is not always bad. It is part of training. The question is whether the amount of fatigue is useful, tolerable, and aligned with the goal.

## Technique consistency
Technique consistency matters because metric comparisons become harder to interpret when setup or ROM changes.

Watch for:
- different start position
- different depth or ROM
- different lockout behavior
- different body angle
- different bracing quality
- different intent level between reps

A rep that looks "better" numerically may partly reflect a different ROM or different execution.

---

# Deadlift / trap bar deadlift context

## Trap bar deadlift
Trap bar deadlift performance is often influenced by:
- load
- handle height
- stance
- torso angle
- bracing
- intent
- fatigue
- ROM consistency

Trap bar deadlifts often allow a more upright torso than conventional deadlifts, which can change movement strategy and affect how metrics should be interpreted.

## Common useful interpretation categories
For this project, we care about:
- explosiveness
- power output
- velocity
- fatigue
- technique consistency
- progressive overload over time

---

# Metric definitions and interpretation

## TTPV
**TTPV = Time to Peak Velocity**

Definition:
- the time from the start of the concentric phase until peak velocity is reached

Typical interpretation:
- lower TTPV can suggest a more explosive start
- higher TTPV can suggest slower force development or delayed acceleration
- TTPV should be interpreted alongside peak velocity and mean velocity

Caveats:
- a faster TTPV is not automatically "better" in every context
- TTPV can change with intent, fatigue, load, and movement strategy
- if rep segmentation is noisy, TTPV can be unstable
- if TTPV data is absent, do not infer or estimate it from other metrics

Practical use:
- compare explosiveness between reps at the same load
- compare readiness across sessions
- detect whether later reps become less explosive

## Peak velocity
Definition:
- the highest instantaneous velocity reached during the concentric phase

Typical interpretation:
- higher peak velocity often reflects stronger top-end acceleration or better intent
- useful for comparing reps of similar ROM and load

Velocity reference zones (approximate, trap bar deadlift):
- above ~0.8 m/s: typically light load, high intent, or very fresh effort
- 0.5–0.8 m/s: moderate load range, solid output
- 0.3–0.5 m/s: heavier load or accumulated fatigue
- below ~0.3 m/s: often indicates proximity to failure or very heavy load; interpret with caution

These are rough anchors only. Treat them as context, not hard thresholds. Individual differences, handle height, and technique can shift these ranges meaningfully.

Caveats:
- peak values can be noisy
- should not be interpreted alone
- may not reflect full-rep quality
- if peak velocity data is absent, do not estimate it

## Mean velocity
Definition:
- average concentric velocity across the rep

Typical interpretation:
- often more stable than peak velocity
- useful for comparing overall rep performance
- lower mean velocity across reps can indicate accumulating fatigue

Mean velocity proximity-to-failure heuristic:
- mean velocity below approximately 0.2–0.3 m/s at a given load often suggests the lifter is close to failure (high RPE / low RIR)
- this is a rough heuristic and should be combined with other signals, not used alone

Practical use:
- session-to-session comparison at a fixed load
- intra-set fatigue tracking
- general readiness and output tracking

If mean velocity data is absent, do not infer it from other metrics.

## Rep duration
Definition:
- total time of the concentric rep

Typical interpretation:
- longer duration often reflects slower execution
- can increase with fatigue
- should be interpreted alongside ROM

Caveats:
- if travel distance changes, duration comparisons are less clean
- if rep duration data is absent, do not estimate it

## Peak power
Definition:
- highest instantaneous power reached during the rep

Typical interpretation:
- useful for identifying maximum output moments
- may be informative for explosiveness and intent

Caveats:
- highly sensitive to noise, model assumptions, and instantaneous fluctuations
- should be paired with mean power and velocity measures
- if peak power data is absent, do not estimate it

## Mean power
Definition:
- average power across the concentric phase

Typical interpretation:
- more stable than peak power
- useful for comparing overall rep output
- lower values across reps may reflect fatigue or reduced intent

## Mean positive power
Definition:
- average power during positive-output portions of the rep

Typical interpretation:
- can better isolate productive concentric output
- may be useful when full-signal averaging obscures meaningful effort

## Travel / displacement / ROM proxy
Definition:
- estimated vertical or total displacement during the rep

Typical interpretation:
- helpful for checking consistency of ROM across reps
- different travel distance can strongly affect comparisons of duration, work, and power

Caveats:
- if travel differs meaningfully, direct rep-to-rep comparisons should be more cautious

## Back roundness flag / score
Definition:
- a derived measure indicating whether the back appears more rounded or less neutral during the rep

Typical interpretation:
- increased roundness may reflect fatigue, bracing loss, positioning change, or intentional movement strategy
- changes across reps may be more informative than a single isolated value
- some degree of thoracic rounding is common and not inherently problematic; context matters
- thoracic rounding and lumbar rounding are different things with different implications; do not conflate them

Caveats:
- this is not a medical diagnosis
- a binary flag is often less informative than a continuous score over time
- should be interpreted in context of load, intent, and athlete style
- do not treat a single elevated reading as a red flag without corroborating signals

---

# RPE, RIR, and velocity relationships

## RPE (Rate of Perceived Exertion)
RPE is a self-reported scale of effort, typically 1–10 in strength training contexts, where 10 represents a true maximum effort or failure.

Common usage:
- RPE 7: moderate effort, several reps left in reserve
- RPE 8: hard effort, approximately 2 reps left in reserve
- RPE 9: very hard, approximately 1 rep left in reserve
- RPE 10: maximal, no reps remaining

## RIR (Reps in Reserve)
RIR is the estimated number of additional reps the lifter could have completed before failure.

Relationship to RPE:
- RPE 10 ≈ 0 RIR (failure)
- RPE 9 ≈ 1 RIR
- RPE 8 ≈ 2 RIR
- RPE 7 ≈ 3 RIR

## Velocity and proximity to failure
Mean velocity tends to decline as a set approaches failure. When velocity data is available, it can complement or inform RPE/RIR estimates:
- higher mean velocity at a given load generally suggests more reps in reserve
- very low mean velocity (below ~0.2–0.3 m/s) often correlates with high RPE / low RIR
- velocity-based estimates should be treated as supporting context, not precise predictions

Use this information to connect velocity metrics to practical coaching language around effort and proximity to failure, but avoid overstating precision.

---

# Eccentric phase

This document currently focuses on concentric phase metrics only. Eccentric data (lowering phase) may or may not be available depending on the capture system.

If eccentric data is not present, do not speculate about it. If it is present but not yet covered by this document, flag it as outside the current scope rather than applying concentric interpretation frameworks directly.

---

# Missing data behavior

If a metric is absent from a given session or rep, do not:
- infer or estimate it from other available metrics
- assume it would have been consistent with prior sessions
- treat its absence as meaningful on its own

Simply note which metrics are available and limit interpretation to those. If critical metrics are missing for a meaningful comparison, acknowledge the limitation explicitly.

---

# How to reason across reps

## Comparing two reps
When comparing two reps, look for:
- was output stable?
- did one rep reach peak output faster?
- did velocity meaningfully change?
- did power meaningfully change?
- did ROM change?
- did the back-rounding signal change?

Interpretation should stay modest if only two reps are available.

## Comparing many reps in a set
With multiple reps, look for:
- mean velocity dropoff
- peak velocity dropoff
- TTPV drift
- power dropoff
- increasing duration
- increasing roundness
- consistency loss

Possible interpretation:
- stable metrics suggest consistent execution
- worsening metrics later in the set may reflect fatigue accumulation
- abrupt breakdown after a certain rep may help identify a practical stopping point

---

# Fatigue heuristics

These are heuristics, not absolute laws.

Possible fatigue indicators:
- mean velocity falls rep to rep
- peak power falls rep to rep
- TTPV becomes slower
- rep duration lengthens
- back-roundness score increases
- ROM changes because the athlete is compensating

Possible coaching interpretation:
- "output is holding steady"
- "mild fatigue is present but technique is stable"
- "fatigue may be accumulating, with some evidence of reduced explosiveness"
- "later reps appear less crisp and may be approaching technical breakdown"

---

# Progressive overload heuristics

Across sessions, positive signs may include:
- same load moved faster
- same load moved with less rounding
- same load moved more consistently
- more reps completed before breakdown
- improved power output at the same load
- improved TTPV or velocity under similar conditions

Context matters:
- sleep
- recovery
- bodyweight
- training phase
- handle height
- footwear
- intent
- camera angle / model noise

---

# Practical coaching language

Helpful phrases:
- "more explosive start"
- "more stable overall output"
- "possible fatigue accumulation"
- "rep quality remained fairly consistent"
- "small dropoff, but not dramatic"
- "interpret cautiously because ROM changed"
- "no major red flag from these metrics alone"
- "appears to be working at a moderate RPE with reps still in reserve"
- "velocity suggests proximity to failure; interpret effort accordingly"

Avoid overclaiming:
- do not say a single metric tells the whole story
- do not say one rep is definitively safer based on limited summary data
- do not claim a program change is necessary from a tiny sample
- do not speculate about missing metrics
- do not treat thoracic rounding as automatically dangerous

---

# Signal Quality & CV Artifacts
- Rapid fluctuations in TTPV or Peak Power may be tracking noise.
- Relative > Absolute: Always prioritize comparing Rep N to Rep 1 over comparing the raw numbers to a universal "norm."

# Velocity Loss Zones
- 0–15% Drop: Movement is "snappy." Ideal for speed work or technique refinement.
- 15–30% Drop: Solid working set. Effort is high but controlled.
- >30% Drop: High fatigue. Likely "grinding." Watch closely for back-rounding score increases here.

---

---

# Intended use in this project

The AI system should use this context to:
- explain metrics in practical coaching language
- support interpretation of trap bar deadlift performance
- reason about explosiveness, power, fatigue, and technique
- connect velocity data to RPE/RIR language where appropriate
- provide useful next-step coaching takeaways
- remain humble about uncertainty
- clearly flag when data is missing or when scope limits interpretation

