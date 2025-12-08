# DATA DICTIONARY — Sumbong sa Pangulo: Flood Control Projects

**File(s):**
- `raw/Sumbong_sa_pangulo_FloodControl.csv` (or `.xlsx`)
- `cleaned/Sumbong_sa_pangulo_FloodControl_cleaned.csv` (optional, for teams)

**Brief description**

This dataset lists **flood-control related infrastructure projects** (e.g., river improvement, flood mitigation structures) with information on **location, implementing office, contract amounts, contractor, timeline, and possible contractor linkages**. It is intended for analyzing patterns and red flags in flood-control spending and implementation from a governance and anti-corruption perspective.

---

## 1. Table structure

| Column Name                   | Type      | Example                                                                                          | Description                                                                                                      | Notes / Caveats                                                                                           |
|------------------------------|-----------|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| `InfraYear`                  | integer   | `2018`                                                                                           | Infrastructure / funding year associated with the project.                                                       | Often aligns with GAA / funding year; may differ from completion year.                                   |
| `Region`                     | string    | `Region III`, `Region IV-B`                                                                      | Administrative region where the project is implemented.                                                          | Naming uses DBM/PSA region labels; some projects may be misclassified or later re-regioned.              |
| `Province`                   | string    | `BATAAN`, `OCCIDENTAL MINDORO`                                                                   | Province where the project is located.                                                                           | Can be blank for some records (e.g., national or cross-province items).                                  |
| `Municipality`               | string    | `Hermosa`, `Calintaan` (blank in some samples)                                                   | City/municipality of project location.                                                                           | May be empty or inconsistently spelled.                                                                  |
| `ImplementingOffice`        | string    | `Bataan 1st District Engineering Office`, `Mindoro Occidental District Engineering Office`       | DPWH (or other agency) unit responsible for project implementation.                                             | Use this to group by District Engineering Office (DEO).                                                  |
| `ProjectID`                  | string    | `P00222127LZ`                                                                                    | Unique project identifier from the source system.                                                                | Together with `ProjectComponentID` often uniquely identifies a contract package.                         |
| `Duplicates`                 | boolean   | `FALSE`                                                                                          | Indicates whether the record is flagged as a duplicate within the dataset.                                      | `TRUE` rows should be treated with caution or de-duplicated.                                            |
| `ProjectDescription`         | string    | `Almacen River Improvement Project, Hermosa and Orani, Bataan`                                   | High-level description or title of the overall project.                                                          | Free text; may contain abbreviations or multiple phases.                                                |
| `ProjectComponentID`         | string    | `P00222127LZ-CW1`                                                                                | Component or contract package identifier linked to the main project ID.                                         | Useful for distinguishing multiple packages under the same project.                                      |
| `ProjectComponentDescription`| string    | `Construction of Flood Mitigation Structure - Almacen River Improvement Project, …`              | Detailed description of the specific component / contract.                                                       | Often combines type of work + location; expect long text.                                               |
| `TypeofWork`                 | string    | `Construction of Flood Mitigation Structure`                                                     | Coded type of work as classified by the source agency.                                                           | Use to filter for specific types (e.g., construction vs rehab).                                         |
| `infra_type`                 | string    | `Flood Control Structures`                                                                       | Infrastructure type category.                                                                                    | For this dataset, most or all entries should be flood-control related.                                   |
| `Longitude`                  | numeric   | `120.54`, `120.98888`                                                                            | Longitude (decimal degrees) of project location.                                                                 | Coordinates may be approximate, centroids, or missing.                                                   |
| `Latitude`                   | numeric   | `14.82`, `12.43518`                                                                              | Latitude (decimal degrees) of project location.                                                                  | Useful for mapping and spatial clustering.                                                               |
| `ContractID`                 | string    | `18C00035`, `18EB0112`                                                                           | Contract reference or ID (often the DPWH contract code).                                                         | May encode year and DEO; format may vary by office.                                                      |
| `ApprovedBudgetForTheContract` | numeric | `143841300`                                                                                      | Approved Budget for the Contract (ABC) in Philippine Peso (PHP).                                                 | Check outliers; not inflation-adjusted.                                                                  |
| `ContractCost`               | numeric   | `136302210.20`, `52442670.04`                                                                    | Awarded contract amount in PHP.                                                                                  | Compare with ABC for potential red flags (over/under-bidding patterns).                                  |
| `CompletionYear`             | integer   | `2022`, `2023`                                                                                   | Year of project completion (actual or recorded).                                                                 | May refer to actual or recorded administrative completion; see date fields.                              |
| `Contractor`                 | string    | `TOKWING CONSTRUCTION, CORP.`, `FFJJ CONSTRUCTION`                                               | Name of winning contractor / supplier.                                                                           | Names may have variations (comma placement, abbreviations, “INC.” vs “INC”).                            |
| `InterRelatedContractor`     | string    | `Independent`                                                                                    | Flag summarizing whether the contractor has detected relationships with others.                                  | `Independent` means no flagged relationship; other values may indicate relations or groupings.          |
| `BasisSource`                | string    | `Independent` / `RelatedInDataset` values                                                        | High-level tag indicating how contractor relations were assessed or sourced.                                     | Wording depends on how contractor-network analysis was done.                                            |
| `RelatedInDataset`           | string    | `BELVIC ENTERPRISES & CONSTRUCTION / FFJJ CONSTRUCTION, ...`                                     | Text listing other contractors in the same relation cluster as detected within the dataset.                      | Very useful for contractor-network / cartel-like pattern analysis.                                       |
| `ObjectId`                   | integer   | `1246`, `3033`                                                                                   | Internal object identifier from the GIS / database layer.                                                        | Technical; mainly for linking back to original geodatabase.                                             |
| `Creator`                    | string    | `dpwh_view`                                                                                      | Username / process that created the record in the source system.                                                 | Typically constant; not analytically important.                                                          |
| `Editor`                     | string    | `dpwh_view`                                                                                      | Username / process that last edited the record.                                                                  | Typically constant.                                                                                      |
| `FundingYear`                | integer   | `2018`                                                                                           | Year tagged as funding year for the project.                                                                     | Often same as `InfraYear`, but not guaranteed; check for discrepancies.                                  |
| `LegislativeDistrict`        | string    | `BATAAN (FIRST LEGISLATIVE DISTRICT)`, `OCCIDENTAL MINDORO (LEGISLATIVE DISTRICT)`               | Congressional legislative district where the project is located.                                                 | Use for analysis by legislative representation.                                                          |
| `DistrictEngineeringOffice`  | string    | `Bataan 1st District Engineering Office`                                                         | District Engineering Office (DEO) implementing the project.                                                      | Key field for clustering by implementing unit.                                                           |
| `GlobalID`                   | string    | `94600588-731a-44a4-ab2b-4ef411d9bf52`                                                           | Globally unique identifier (GUID) from the geodatabase.                                                          | Primary key candidate; unique per record.                                                                |
| `CompletionDateActual`       | date      | `8/31/23`                                                                                        | Recorded actual completion date of the project.                                                                  | Could be blank, defaulted, or entered late.                                                              |
| `StartDate`                  | date      | `2/26/18`, `4/20/18`                                                                             | Start date of project implementation (usually NTP or equivalent).                                               | Use with `CompletionDateActual` for duration analysis.                                                   |
| `PresTerm`                   | string    | `Duterte`, `Marcos Jr.` (expected)                                                               | President’s term during which implementation started or was funded.                                              | Allows grouping by administration.                                                                       |
| `CompletionDateOriginal`     | date      | `8/30/23`, `11/21/18`                                                                            | Original targeted completion date of the project.                                                                | Compare with actual completion for delay/extension analysis.                                             |
| `CreationDate_date`          | datetime  | `4/8/25 0:00`                                                                                    | Date/time when the record was created in the GIS/database.                                                       | System metadata; may be in future relative to project dates (batch loading).                             |
| `EditDate_date`              | datetime  | `4/8/25 0:00`                                                                                    | Date/time when the record was last edited in the GIS/database.                                                   | System metadata; not the same as project completion.                                                     |
| `CompletionDateActualYear`   | integer   | `2023`, `2022`                                                                                   | Year extracted from `CompletionDateActual`.                                                                      | Useful for quick grouping when full dates are messy.                                                     |
| `StartDateYear`              | integer   | `2018`                                                                                           | Year extracted from `StartDate`.                                                                                | Use for cohorting projects by starting year.                                                             |

---

## 2. Keys and uniqueness

- **Primary key candidate:**  
  - `GlobalID` (GUID, expected to be unique for each contract record).
- **Other useful identifiers:**
  - (`ProjectID`, `ProjectComponentID`, `ContractID`) — together can identify contract packages.
- **Duplicates:**
  - Rows where `Duplicates = TRUE` are flagged as potential duplicates and should normally be excluded or carefully reviewed.

---

## 3. Coverage and scope

- **Time period:**  
  - Example rows show `InfraYear` around 2018 and completion years 2022–2023.  
  - Exact min/max years should be checked by participants using summary statistics.

- **Geographic coverage:**  
  - Flood-control projects across multiple regions (e.g., Region III, Region IV-B), provinces and DEOs.

- **Thematic coverage:**  
  - Flood-control and river improvement related projects, under `infra_type = "Flood Control Structures"`.

---

## 4. Suggested use in the Policy Hackathon

Teams can use this dataset to:

- Map flood-control projects and identify **spatial clusters** of spending or delays.  
- Analyze **gaps between ABC and Contract Cost** across regions and contractors.  
- Examine **project durations** (from `StartDate` to `CompletionDateActual`) and detect systematic delays.  
- Investigate **contractor networks** using `InterRelatedContractor` and `RelatedInDataset` to see if a small group of firms dominates contracts in certain areas.  
- Compare project patterns across **Presidential terms**, **districts**, or **funding years** and link to policy/oversight questions.

When formulating problems and recommendations, teams should connect these patterns to **accountability, transparency, and integrity in public infrastructure spending.**
