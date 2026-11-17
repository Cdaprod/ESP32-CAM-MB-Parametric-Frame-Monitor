# V007 candidate — two-arm cable guide correction

The user identified that both V004-inherited saddles are on the wrong side of the arms relative to the V006 USB route.

`src/build_v007.py` reconstructs both link bodies and moves the guide bores to local **X = -27 mm**, coincident with the V006 cable reference path. The first arm guide is at **Y = -39, Z = 19 mm**; the second is at **Y = -74, Z = 27 mm**. The two M4 arm joint axes and V006 four-joint wrist assembly are preserved.

**Status: SOURCE CANDIDATE ONLY — NOT A RELEASE.** The original V006 STEP, STL, renders and 13-pose clearance numbers remain unchanged and must **not** be represented as validating this candidate. A 3.2 mm nominal cable in a 3.8 mm bore gives 0.3 mm nominal radial clearance, pending print and cable measurement.

## Required acceptance before promotion

1. Run `python src/build_v007.py` with CadQuery installed; inspect generated first/second arm STLs and assembled STEP.
2. Verify the V006 cable segments actually pass through the bores in all sampled poses, and check cable-to-knob, cable-to-rail and cable-to-arm distances **excluding intentional guide contact**.
3. Verify guide support doesn't interfere with adjacent joints or hardware; add realistic flexible loops and check minimum bend radius.
4. Regenerate geometry-derived preview PNGs, V007 manifest, BOM, validation JSON and fit register.
5. Only after successful validation, update VERSION, README, release pointer and CI from V006 to V007.

The prior release remains available for reproducibility. This source change alone does not establish collision-free cable routing or physical print readiness.
