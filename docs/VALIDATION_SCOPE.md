# V008 verification scope

**CAD-only prototype, not a physically qualified printer-mounted device.**

The new unified build generates a 30-entry assembly, two corrected watertight arm STLs, and three geometry-derived PNG renders. The validation checks 13 *selected* poses of four manually adjustable joints (base, elbow, pitch and wrist), not the entire four-dimensional joint space.

| CAD observation | V008 result |
|---|---:|
| Selected articulated poses | 13 / 13 pass |
| Both arm cable guides align with the nominal lead | 2 / 2 |
| Nominal cable outside diameter | 3.2 mm |
| Guide through-bore diameter | 3.8 mm |
| Nominal radial clearance through either guide | 0.30 mm |
| Minimum cable-to-knob distance | 7.132 mm |
| Minimum cable-to-4040 distance | 3.802 mm |
| New watertight print parts | 2 / 2 |

**Not yet demonstrated:** continuous 4-DOF collision-free operation; cable connector boot and bend radius; dynamic sag, torsion and strain relief; printed guide/web stiffness or fatigue; real 4040 slot and M5 T-nut engagement; actual camera stack; the printer's full movement envelope; heat, torque, UV and vibration safety.

Physical acceptance requires actual dimensions in the [V008 fit register](PHYSICAL_FIT_REGISTER_V008.csv), a printed cable-guide coupon, and a powered-off complete machine-travel and harness clearance test before any operational installation.

[Latest CAD report](validation_v008.json) · [Engineering notes](ENGINEERING_NOTES_V008.md).
