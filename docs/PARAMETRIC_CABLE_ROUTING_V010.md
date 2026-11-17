# Parametric cable routing / circular arc geometry

V010's previous cable polyline had global-local outboard waypoints at `x=-27 mm`, and `cable_reference()` returned individual, sharply joined cylindrical solids. The route now comes from named parameters in `config.py` and `route_nodes()`, transformed separately by the **camera wrist, pitch, second arm, first arm and stationary rail** kinematic frames.

The bend generator calculates the turn angle `theta`, with tangent setback `d = r * tan(theta/2)`. It creates exact circular `makeThreePointArc` edges between tangent line segments, then sweeps a single circular cross-section across the continuous wire. To prevent neighboring rounds consuming the same straight segment, each setback is limited to `cable_bend_cutback_fraction * min(adjacent_leg_lengths)`. It fails on degenerate cable paths and records the **actual drawn minimum arc radius** rather than quietly claiming the configured target radius.

The four clip centers remain on the original arm-local bore datums. Deliberate cable service turns around the three moving interfaces clear the knob regions, but their cable-flex suitability and their detailed full-motion collision behavior are still **unverified**. The configured cable diameter, connector exit, wrist loop clearance, strain, and minimum tolerable flex radius require real harness measurement and print testing.

Run `python tests/test_cable_arcs.py`, `python src/build.py all` and inspect `docs/validation_v010.json`. This is **CAD reference only**, not physical cable compliance.
