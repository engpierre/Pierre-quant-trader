# Strategy Summary - Toronto Treasure Hunt
**Generated**: 2026-03-01
**Purpose**: Catalog all solving approaches (complete, incomplete, promising)

---

## STRATEGY CLASSIFICATION SYSTEM

- ✅ **COMPLETE**: Fully tested, results documented
- 🔄 **ACTIVE**: Currently being worked on
- ⏸️ **INCOMPLETE**: Started but paused/abandoned
- 💡 **PROPOSED**: Theory exists but not yet tested
- ❌ **DEAD**: Tested and eliminated

---

## PART 1: CIPHER DECODING STRATEGIES (Historical)

### ✅ Strategy 1: Book Cipher (English Article)
**Status**: COMPLETE → SOLVED
**Approach**: Ottendorf cipher using ROM mineral specimens 24-37 as key
**Result**: Successfully decoded to "From Here Follow the line through The financial Hub to find WHAT you Seek"
**Promise**: ✅ SOLVED - No further work needed
**Evidence**: Michelle field work at ROM confirmed mechanism

---

### ❌ Strategy 2: Alternative Book Ciphers
**Status**: COMPLETE → DEAD
**Tested variants**:
- Sentence → Word → First Letter (0% readable)
- Line/Paragraph → Word/Char (29 variations, all gibberish)
- French article text (same approaches, same result)
- External key texts (not found)

**Promise**: ❌ DEAD - ROM cipher was correct approach

---

## PART 2: LOCATION FINDING STRATEGIES (Current)

### 🔄 Strategy 3: Video Number Extraction & Analysis
**Status**: ACTIVE
**Completion**: ~70% (extraction done, interpretation incomplete)

**What's Complete**:
- ✅ Michelle manually extracted red line number sequence
- ✅ Peter automated number extraction from video frames
- ✅ Frequency analysis completed (883.26%, 552.93%, 392.35% appear multiple times)
- ✅ Temporal sequence documented

**What's Incomplete**:
- ❌ Interpretation of numbers (coordinates? stock data? addresses?)
- ❌ Significance of repeated numbers
- ❌ Connection to red line trajectory
- ❌ Grid position analysis

**Sub-approaches proposed**:

| Sub-Strategy | Status | Promise | Notes |
|-------------|--------|---------|-------|
| 3A: Direct lat/long coordinates | 💡 Proposed | MEDIUM | Numbers too large (>180), need transformation |
| 3B: TSX stock percentage matches | 💡 Proposed | **HIGH** | Thematically perfect, testable with historical data |
| 3C: Historical stock prices | 💡 Proposed | **HIGH** | Similar to 3B, different interpretation |
| 3D: UTM coordinate system | 💡 Proposed | MEDIUM | Mining-relevant but format doesn't match |
| 3E: Street addresses | ⏸️ Incomplete | LOW | Tested in active_theories/theory_street_addresses/ |
| 3F: Bus/transit stops | ⏸️ Incomplete | LOW | Tested in active_theories/theory_bus_stops/ |
| 3G: Chemical assay percentages | 💡 Proposed | MEDIUM | Mining-specific, requires expertise |
| 3H: Mining claim numbers | ⏸️ Incomplete | LOW | Tested in active_theories/theory_mining_claims/ |

**Overall Promise**: **HIGH** - Numbers are deliberately placed and extracted, must be significant
**Next Action**: Test strategies 3B and 3C first (TSX stock data research)

---

### 💡 Strategy 4: Capital Letter Pattern Analysis
**Status**: PROPOSED
**Pattern**: M-H-F-W-G-H-T-L-H-D-W-H-A-T-S-K (16 letters)

**Sub-approaches**:

| Sub-Strategy | Status | Promise | Notes |
|-------------|--------|---------|-------|
| 4A: Periodic table elements | 💡 Proposed | **HIGH** | M=Mg, H=H, F=F, W=W (tungsten), G=Ge, etc. Mining-relevant |
| 4B: Morse code | 💡 Proposed | MEDIUM | Video used Morse for "ROM", precedent exists |
| 4C: Grid reference system | 💡 Proposed | MEDIUM | Convert to numbers (A=1, B=2...), plot coordinates |
| 4D: Initials of locations | 💡 Proposed | LOW | Would need to guess locations first |
| 4E: Acrostic (read as phrase) | ⏸️ Incomplete | LOW | "MH FW GH TL HD WH ATS K" - no clear meaning |

**Overall Promise**: **HIGH** - Capitals are deliberately preserved in cipher output, likely secondary clue
**Next Action**: Test Strategy 4A first (periodic table elements, especially tungsten W)

---

### 💡 Strategy 5: "Croesus min (1914)" Typo Analysis
**Status**: PROPOSED
**Verified Fact**: Article line 13 typo confirmed - "Croesus min" instead of "mine"

**Sub-approaches**:

| Sub-Strategy | Status | Promise | Notes |
|-------------|--------|---------|-------|
| 5A: "min" = minutes (coordinates) | 💡 Proposed | **HIGH** | 43°19'14"N or 43°19.14'N in Toronto area |
| 5B: "min" = minimum distance | 💡 Proposed | MEDIUM | Connection to 5km constraint? |
| 5C: "min" = mineralogy code | 💡 Proposed | LOW | "min" not standard mineral abbreviation |
| 5D: "1914" as bearing angle | 💡 Proposed | MEDIUM | 191.4° or 19.14° from starting point |
| 5E: "1914" as coordinate seconds | ⏸️ Incomplete | MEDIUM | Friend proposed 78°55'19.14"W (Fort Erie) |

**Overall Promise**: **HIGH** - Only intentional typo in entire article, must be significant
**Next Action**: Test Strategy 5A (coordinate minutes) - plot locations and check for landmarks

---

### 💡 Strategy 6: Geometric Line Following
**Status**: PROPOSED
**Basis**: Cipher says "From Here Follow the line through The financial Hub"

**Sub-approaches**:

| Sub-Strategy | Status | Promise | Notes |
|-------------|--------|---------|-------|
| 6A: CN Tower → Bay Street line | 💡 Proposed | **HIGH** | Video "HERE" at CN Tower (0:53), extend through financial district |
| 6B: ROM → TSX line | ❌ Rejected by Marc | LOW | Marc/Michelle determined "Here" ≠ ROM |
| 6C: Richmond St. W → East line | 💡 Proposed | **HIGH** | "From Here" = 122 Richmond St. W. (article line 2) |
| 6D: Yonge Street baseline | 💡 Proposed | MEDIUM | Red line goes "up" CN Tower = north along Yonge? |
| 6E: Historical mining district trail | 💡 Proposed | MEDIUM | Follow sequence of mining offices/exchanges |

**Overall Promise**: **HIGH** - Most literal interpretation of cipher instruction
**Next Action**: Test Strategy 6A (CN Tower triangulation) - calculate bearing and plot waypoints

---

### ⏸️ Strategy 7: Distance-Based Circle Search
**Status**: INCOMPLETE
**Location**: active_theories/theory_distance_rom/

**What's Complete**:
- ✅ Calculated waypoints at various distances from ROM
- ✅ Generated CSV of coordinates
- ✅ Identified landmarks at each distance

**What's Incomplete**:
- ❌ Marc rejected ROM as starting point (should recalculate from CN Tower or 122 Richmond)
- ❌ No clear mechanism for which distance/direction is correct

**Overall Promise**: LOW - Shotgun approach without clear direction mechanism
**Salvage**: Recalculate circles from CN Tower at 5-10km distances

---

### 💡 Strategy 8: Historical Building Research
**Status**: PROPOSED
**Basis**: "The financial Hub" (capital H) = specific building, not general area

**Candidates**:

| Building | Address | Era | Mining Connection | Distance from 122 Richmond |
|---------|---------|-----|------------------|---------------------------|
| Northern Miner HQ | 122 Richmond St. W | 1929-present | **Direct** (article line 2) | 0m (starting point?) |
| Old Toronto Stock Exchange | 234 Bay St | 1937-1983 | Mining stocks traded | ~300m ❌ (too close) |
| Standard Stock Exchange (historical) | Unknown | 1896-1934 | Junior mining shares | Research needed |
| First Canadian Place | 100 King St W | 1975 | Modern financial center | ~400m ❌ (too close) |
| Royal Bank Plaza | 200 Bay St | 1976 | Mining finance | ~350m ❌ (too close) |

**Overall Promise**: **HIGH** - Article emphasizes specific addresses, buildings are verifiable
**Next Action**: SCOUT research - locate historical Standard Stock Exchange building (merged with TSX in 1934)

---

### 💡 Strategy 9: PDAC Convention Center Grid
**Status**: PROPOSED
**Basis**: Article extensively discusses PDAC (lines 22-24), Metro Toronto Convention Centre

**Approach**:
- Obtain PDAC floor plan or booth numbering system
- Map video grid numbers to convention center layout
- Identify significant booth/location

**Challenges**:
- Convention center layout changes annually
- Booth numbers not permanently documented
- Video grid may not match physical layout

**Overall Promise**: MEDIUM - Strong thematic connection but execution uncertain
**Next Action**: Research if PDAC has permanent exhibits or memorials at convention center

---

### ❌ Strategy 10: "Shotgun" Approach (Article Location Check)
**Status**: DEAD (too many competitors will do this)
**Approach**: Visit every location mentioned in article

**Article locations**:
- 122 Richmond St. W. (Northern Miner HQ) ❌ <5km
- Bay Street (financial district) ❌ <5km
- Front Street (convention area) ❌ <5km
- Metro Toronto Convention Centre ❌ <5km
- High Park area ✅ ~7km (POSSIBLE)
- Royal Ontario Museum ✅ ~3km ❌ (too close)

**Overall Promise**: LOW - Other hunters will check obvious locations first
**Exception**: High Park may be worth investigating (less obvious, mentioned in article)

---

## PART 3: HALLUCINATED STRATEGIES (Friend's Theories)

### ❌ Strategy 11: "Dana Cipher" Location Decoding
**Status**: DEAD - **DOES NOT EXIST**

**What friend claimed**:
- "Dana cipher" produces "creek bend" and "old oak tree" instructions
- "Six paces" instruction
- "25-1" sector codes

**Reality**:
- ❌ No "Dana cipher" in puzzle materials
- ❌ Decoded cipher says "From Here Follow the line..." (no creek/oak/paces)
- ⚠️ "25-1" exists in codes.txt but as cipher input (Calcite, 1st character), not output

**Overall Promise**: NONE - Fundamental misunderstanding of puzzle
**Lesson**: Verify all "clues" against source materials before building theories

---

## PART 4: STRATEGY PRIORITY MATRIX

### 🔥 **HIGHEST PRIORITY (Test Immediately)**

| Strategy | Reason | Resources Needed | Estimated Effort |
|----------|--------|------------------|------------------|
| **5A: Croesus min = Coordinates** | Only typo in article, human-solvable | Map plotting | 1-2 hours |
| **6A: CN Tower Triangulation** | Video evidence (0:53), cipher literal | Bearing calculation, map | 2-3 hours |
| **6C: Richmond St. as Starting Point** | Article line 2, explicit address | Historical research | 2-4 hours |
| **3B: Red Line = TSX Stock Data** | Perfect thematic fit | TSX historical database | 4-6 hours |
| **4A: Capitals = Periodic Table** | Mining-relevant, elegant | Element research | 2-3 hours |

**Recommendation**: Assign **Peter** to test 5A and 6A (computational). Assign **Scout** to research 6C and 3B (requires databases).

---

### ⚠️ **MEDIUM PRIORITY (Test if High Priority Fails)**

| Strategy | Reason | Blockers |
|----------|--------|----------|
| **3C: Red Line = Stock Prices** | Similar to 3B, different mechanism | Same data source as 3B |
| **6D: Yonge Street Baseline** | Clever use of Toronto geography | Need direction disambiguation |
| **9: PDAC Grid System** | Strong thematic connection | Floor plan availability |
| **4B: Capitals = Morse Code** | Video precedent (ROM in Morse) | Need encoding key |

---

### ⏸️ **LOW PRIORITY (Revisit Later)**

| Strategy | Reason | Why Deprioritized |
|----------|--------|-------------------|
| **7: Distance Circles** | No clear direction mechanism | Shotgun approach |
| **3D: UTM Coordinates** | Mining-relevant format | Numbers don't fit format well |
| **10: Article Location Check** | Simple, verifiable | Others will do this first |
| **4C: Capitals = Grid Reference** | Generic approach | No specific grid system identified |

---

## PART 5: STRATEGIC RECOMMENDATIONS

### For **COORDINATOR (You)**:
1. ✅ Assign Peter to test **Strategy 5A** (Croesus coordinates) - quick computational task
2. ✅ Assign Peter to test **Strategy 6A** (CN Tower triangulation) - calculate bearing to Bay St, plot waypoints
3. ✅ Assign Scout to research **Strategy 3B** (TSX historical stock data) - match video percentages to companies
4. ✅ Assign Scout to research **Strategy 6C** (122 Richmond St. history) - find historical mining finance buildings

### For **MARC (Human Lead)**:
- **CRITICAL CLARIFICATION NEEDED**: Confirm interpretation of video 0:53 "HERE" = CN Tower
- Can you access TSX historical mining stock database?
- Should we focus on coordinate theories (5A, 3D) or landmark theories (6A, 6C, 8)?
- Is Michelle available for single-location field verification if we converge on strong candidate?

### For **THOMAS (Skeptic)**:
- Continue monitoring for logical leaps and hallucinations
- Before Peter tests any theory, verify clue basis against FACTS.md

### For **FRANK (Fact Keeper)**:
- Add to FACTS.md: "Croesus min (1914)" confirmed as only typo in article
- Update video analysis: Confirm 0:53 timestamp as "HERE" emphasis
- Track which theories have been tested vs proposed

---

## PART 6: EXECUTION PLAN (Next 48 Hours)

### Phase 1: Quick Computational Tests (1-2 hours)
**Assign to Peter:**
1. Plot coordinates: 43°19'14"N, 79°??"W (Strategy 5A)
2. Calculate CN Tower → Bay Street bearing, extend 5-10km (Strategy 6A)
3. Convert capital letters to atomic numbers (Strategy 4A)

### Phase 2: Database Research (2-4 hours)
**Assign to Scout:**
1. TSX historical data: Search for 883.26%, 552.93%, 392.35% (Strategy 3B)
2. Research 122 Richmond St. W history and nearby mining buildings (Strategy 6C)
3. Tungsten connections in Toronto (Strategy 4A/18)

### Phase 3: Synthesis (1 hour)
**Coordinator:**
1. Review Peter's coordinate plots - any promising landmarks?
2. Review Scout's findings - any company names or addresses match?
3. Cross-reference results from Phases 1 and 2
4. Prepare field verification request for Michelle if strong candidate emerges

### Phase 4: Iterate or Pivot (TBD)
- If high-priority strategies fail → test medium priority
- If computational approaches fail → consider field reconnaissance at High Park
- If stuck >1 hour → **CONSULT MARC**

---

## PART 7: LESSONS LEARNED

### ✅ **What's Working**:
1. **Team coordination**: Frank (facts) → Ernest (ideas) → Thomas (filter) → Peter (test) works well
2. **Systematic testing**: Document everything in active_theories/ folders
3. **Video analysis**: Michelle's manual extraction yielded concrete data
4. **Hallucination detection**: Thomas caught "Dana cipher" fabrication early

### ⚠️ **What Needs Improvement**:
1. **Verify clues before building theories**: Friend's locations were based on invented content
2. **Don't reuse cipher inputs as location clues**: "25-1" was part of decoding, can't reuse
3. **Stay grounded in source material**: Constantly check against FACTS.md
4. **Avoid "treasure hunt movie" logic**: Real puzzles are more elegant than "six paces from oak tree"

### ❌ **What to Avoid**:
1. **Mixing treasure hunts**: Video content from other hunts is contamination
2. **Arbitrary number manipulation**: Need clear justification for coordinate transformations
3. **Over-speculation on article text**: Not every phrase is a clue
4. **Ignoring constraints**: Treasure must be >5km from office AND in Toronto

---

## APPENDIX: Strategy Testing Template

When testing a new strategy, use this format:

```markdown
## Strategy [Number]: [Name]
**Status**: [PROPOSED/ACTIVE/COMPLETE]
**Assigned**: [Peter/Scout/Coordinator/Marc]
**Started**: [Date]
**Completed**: [Date or "In Progress"]

### Hypothesis
[What you're testing and why]

### Clue Basis
[Which verified clues support this theory]

### Method
[Step-by-step approach]

### Expected Output
[What would constitute success]

### Results
[What you found]

### Verdict
[PURSUE/DEPRIORITIZE/REJECT with reasoning]

### Next Steps
[If promising, what to do next; if dead, what to try instead]
```

---

**END OF STRATEGY SUMMARY**

**Last Updated**: 2026-03-01
**Next Review**: After Peter/Scout complete Phase 1-2 tasks
