# References & Standards Positioning

**Status:** Supporting reference index for the v1 architecture package.  
This file does not replace the normative specs.

## Standards / vocabularies
- ISO 19157-1:2023 — geographic data quality; core quality/evaluation foundation.
- ISO 19111:2019 + applicable published amendments — referencing by coordinates; CRS/coordinate-operation concepts.
- EPSG Geodetic Parameter Dataset — authoritative registry used with pinned versions.
- ISO 19112:2019 — spatial referencing by geographic identifiers; useful for gazetteer/reference semantics, not automatic truth.
- ISO 19115-1:2014 + applicable amendments — metadata concepts; use conceptually/adapters, do not hard-bind the domain model to XML.
- ISO 19131:2022 — data product specification/intended purpose; business tolerances remain project policy.
- ISO/TS 19158:2012 — conditional ongoing supplier/acquisition QA reference; not the core basis for one-time off-the-shelf data QA.
- ISO 19160-3:2020 — address data quality profile; optional Address Profile only.
- ISO 19156:2023 — observations/measurements/samples; map only where source semantics genuinely fit.
- OGC Simple Feature Access Part 1: Common Architecture v1.2.1 (OGC 06-103r4) — geometry/simple-feature concepts.
- W3C PROV-DM — W3C Recommendation, provenance data model.
- W3C PROV-O — W3C Recommendation, OWL ontology for PROV.
- W3C DQV — W3C Working Group Note; useful vocabulary for quality Dimension/Metric/Measurement/Policy.
- ISO 19157-3 — treat as under development until formally published; TopPrism uses a namespaced, versioned internal Measure Registry meanwhile.

## Selected literature used as design context
- Goodchild, M. F., & Li, L. (2012). Assuring the quality of volunteered geographic information. *Spatial Statistics*, 1, 110–120.
- Barron, C., Neis, P., & Zipf, A. (2014). A Comprehensive Framework for Intrinsic OpenStreetMap Quality Analysis. *Transactions in GIS*, 18, 877–895.
- Senaratne, H. et al. (2017). A review of volunteered geographic information quality assessment methods. *International Journal of Geographical Information Science*, 31(1), 139–167.
- Devillers, R., Bédard, Y., Jeansoulin, R., & Moulin, B. (2007). Fitness-for-use / spatial data quality information analysis work in *IJGIS*.
- Zandbergen, P. A. (2008). Positional Accuracy of Spatial Data: Non-Normal Distributions and a Critique of the National Standard for Spatial Data Accuracy. *Transactions in GIS*, 12, 103–130.
- Xu, Y., Lewis, E., & Guan, W. (2019). China map integration / GCJ-02 context. *ISPRS International Journal of Geo-Information*, 8(12), 567.
- Dong, X. L., Berti-Équille, L., & Srivastava, D. (2009). Integrating Conflicting Data: The Role of Source Dependence.
- Truth-discovery literature — useful for source dependence/conflicting claims, but not adopted as v1 runtime truth fusion.
- Human-in-the-loop / active-learning literature — supports selective human intervention and informative sample selection; it does not prove SSI's particular governance contract.
- Safe/offline reinforcement-learning literature — motivates constrained, conservative policy optimization; RL is P2 research in SSI and never owns hard Gate authority.

## Claim discipline
The architecture uses standards and papers as:
- normative conceptual references;
- design precedents;
- terminology checks;
- risk warnings.

It must not claim that a paper proves a TopPrism detector, FTR bound, source truth or business threshold unless the exact evaluation evidence exists.
