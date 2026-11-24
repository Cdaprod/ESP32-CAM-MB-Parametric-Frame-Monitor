# V010 engineering notes — structural revision

## Structural load-path and clip-access revision

Current active CadQuery geometry, STEP/STL exports and Orca project. Historical V004/V006 files are preserved.

Starting at the camera and proceeding toward the rail:

1. Enclosure: replace the 5 × 6.3 mm tab (31.5 mm² nominal section, only 0.8 mm floor overlap) with a 14 × 5.8 mm leaf (81.2 mm²) and a 12 mm-wide rear-wall buttress rising to Z=16, with R1.5 concave root blending. This adds a second, higher attachment into the wall without filling the board cavity or USB aperture. The rising buttress starts outside the wrist wheel envelope.
2. Wrist: widen the wrist-end spine to 10.7 mm, taper to the pitch mating side, enlarge the pitch ear from R7.5 to R9.5, and continue the underside heel into both journal regions. Extend bore and nut-insertion cuts through the added material while preserving pivot axes and the wrist nut seat. The pitch ear grows to 6.3 mm thickness; its nut seat moves outward by 2 mm, increasing the bearing floor from 0.85 to 2.85 mm and using an M4×25 pitch bolt.
3. Pitch arm: a 12 mm-wide triangular heel reaches 19 mm into the arm and ties the upright to the link, rather than concentrating load through its short rectangular toe. Existing pivot centers, bores and clamping faces remain.
4. First arm: retain its continuous center spine and rounded slot ends, with groove length revised for cable entry. Its 35 mm pivot spacing and 7.5 mm thickness remain.
5. Extrusion: add paired 3 mm heel ribs outside the M5 counterbores; retain the rail-bearing face and separate metal T-nut clamping. A local front-face wheel relief prevents rubbing. Publish the revised mount as V010; preserve V004 exports.

The base and elbow wheels formerly intersected the printed arms by 1.5 mm. They now have 0.5 mm nominal face clearance. Their modeled bolt lengths change to M4×30 and M4×25 respectively, with metal nut datums preserved; verify actual bolt engagement/protrusion on hardware.

Cable clips: first-arm center spacing 13 mm, second-arm spacing 14 mm. With 4.5 mm pad widths, clear gaps are 8.5 and 9.5 mm, versus 0.7 and 1.5 mm previously. Entry/exit anchors and both grooves are adjusted to keep the curved cable reference off the reinforced pads. The cable is seated into the alternating open mouths; physical insertion force, bending and retention remain untested.

Verification now includes seven solid-volume witnesses along these roots, board/USB and pivot-bore exclusion checks, and printed-body intersection checks at all 18 sampled poses. These checks establish modeled material continuity and sampled clearance, not fatigue life or a load rating.

The Orca project uses explicit side orientations for the enclosure and pitch/wrist parts, rather than largest-convex-face orientation. The mounting plate rests on its rail-bearing face; the first link, knobs and bezel lie flat. Automatic supports remain enabled for unavoidable suspended features. Settings increase to five walls and 40% infill. The installed PLA profile is retained as a prototype setting; temperature, creep, layer adhesion and support removal must be assessed with the actual material. Physical clip coupons, joint torque tests, camera-mass load tests and unpowered printer-travel inspection remain required before claiming break resistance.


## Current CAD acceptance

- Eight unique printed designs: valid single BREP solids, watertight positive-volume STL meshes, CAD/mesh volume agreement within 0.5%.
- Seven solid-volume root witnesses pass; board cavity, USB aperture and six pivot-bore probes are clear.
- Eighteen sampled poses: printed bodies do not interpenetrate; the cable has 0.30 mm minimum modeled arm-channel clearance, 3.650 mm minimum wheel clearance and 4.147 mm rail clearance.
- The pitch upright uses a single conservative convex clearance silhouette over 15 camera-box poses, rather than notched cuts for each pose. The lower boss and broad front heel carry the load around that clearance.
- All four pivot centers are preserved. The first two arm pivot spacings remain 35 mm. Metal clamp faces and T-slot datums are retained.
- The saved native 3MF contains 11 separate, grounded objects, with 12 mm minimum projected-hull spacing and checked orientation heights. Six current V010 designs and two inherited designs make up the eight unique printed parts.

The cable route is a reference, not a flexible-body simulation; minimum drawn radius remains about 2 mm in some transitions. Clip spacing improves insertion access but does not establish cable-jacket strain, insertion force, retention or fatigue life. The 18 poses and conservative local keepout are not an exhaustive continuous four-axis proof. No structural FEA or physical load rating is claimed.


## Offline slicing evidence

OrcaSlicer 2.5.0-rc successfully sliced the complete updated 11-piece plate with the installed Neptune 2 0.4 mm / Panchroma PLA Matte settings, five walls, 40% infill and automatic normal supports. Estimated total: **7h 29m 10s, 74.51 g**. Maximum part height: 36 mm. Support and support-interface toolpaths are present. Independent support/interface layers can differ from the nominal 0.20 mm object-layer setting. G-code remains temporary analysis output; no printer was contacted or operated.

Verified project SHA-256: `19fb47ab22bd86dc924b51bfbb1c50c592a30434bf69292e7bfe04e610478364`.

Project verification also compares each saved object mesh volume with its current STL and checks the eight-design BOM multiplicities, so CI rejects a project that silently retains older meshes or drops/duplicates a part.
