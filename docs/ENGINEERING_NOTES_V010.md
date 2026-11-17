# V010 engineering notes — integrated cable clips and topology-inspired components

The V009 long cable outriggers have been removed from both tapered arm links and replaced with **four compact alternating open U-shaped clips**. They are fused directly to the moving link bodies; a flexible cable has NOT been physically simulated.

## Dimensional design
- Arm pivot spacing retained at 35 mm, with the original four tool-free joints and left-side horizontal 4040 rail placement.
- Cable Ø3.2 mm nominal; U-seat Ø3.8 mm, radial clearance 0.30 mm, width 3.6 mm, outer radius 3.55 mm, throat 2.65 mm.
- Clip sides follow **−X,+X,−X,+X** in moving arm-local frames (two per arm).
- First link: (x=−15.5, y=−30 and −40, z=17.6) mm. Second link: (x=−15.5, y=−63.8 and −75, z=25.1) mm.
- Each clip has a *short side foot* terminating at x=−6.8 mm; there are no tall guide webs hanging beneath either arm.
- Scalloped M4 hand knobs keep the nominal Ø23 mm envelope and existing M4/captive nut datums. Six weight-relief bores; twelve peripheral grip recesses.
- Camera shell retains all board, bezel and wrist interfaces; four exterior sidewall pockets remove only 0.8 mm from nominal 3 mm sidewall.

## Verification scope
- Current local CAD reference passes 18 discrete joint configurations; the workflow regenerates and checks this on GitHub.
- Four new single-body watertight meshes, 30 assembly/reference entries, cable-arm nominal gap 0.30 mm, cable-to-knob minimum 3.909 mm and cable-to-rail minimum 3.802 mm in the sampled poses.
- The polyline consists of rigid cylindrical segments and does NOT simulate cable bend, strain, connector boot, sag, fatigue or continuously swept motion.
- The 2.65-mm snap opening is intentionally narrower than nominal jacket Ø3.2 mm, but the print's elasticity and realistic insertion force are UNVERIFIED. Run clip coupons and repeated insertions before use.

## Pending follow-up
The wrist adapter and 4040 clamp plate still use earlier geometry. A future topology-inspired shape review needs load cases, torque and stress concentration evaluation rather than cosmetic holes. Machine travel, fasteners, printer vibration, temperature and actual cable clearance need a physical acceptance gate.

[Actual V010 previews](../README.md) · [Validation record](validation_v010.json) · [Hardware BOM](BOM.csv)
