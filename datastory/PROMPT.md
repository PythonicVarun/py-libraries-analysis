# Data Story Generation Prompt

This document contains the system prompts used to generate the data story.

**Tools Used:**
*   **Agent:** GitHub Copilot in VS Code
*   **LLM:**
    *   **Claude Sonnet 4.5:** Used to generate overview of the analysis.
    *   **Claude Opus 4.5:** Used for HTML page generation of the data story.

---

### Amanda Cox Style Data Story

Create a single-page HTML interactive data story titled **"The TypeError Detective: A Journey Through Python's None-Handling Underworld"** in the style of Amanda Cox (NYT Upshot editor).

**THE UNIQUE DATASET CHARACTERISTIC (Don't be a data fashion victim):**
This isn't just about bugs—it's about the **archaeology of maintainer culture**. Three identical type errors, three wildly different responses, revealing the hidden sociology of open-source maintenance.

**CORE NARRATIVE STRUCTURE:**

**ACT I: The Investigation**
- A developer runs type-checking analysis (using a tool that finds `None`-handling issues)
- Manual + LLM verification to filter false positives
- Creates reproduction code for each bug
- Files issues in three major Python libraries: SQLAlchemy (11.4k stars), Apache Arrow (16.4k stars), scikit-learn (64.8k stars)

**ACT II: The Three Responses (Soul-Crushing Line Charts)**

1. **SQLAlchemy: "What are we doing here exactly?"**
   - Response time: 8 minutes (!)
   - Outcome: Closed, converted to discussion, labeled "expected behavior"
   - Key quote from maintainer @zzzeek: *"What are we doing here exactly? We work with use cases and problems to be solved here"*
   - The twist: User points out **inconsistency in the same method** (some guards exist, others don't)
   - Maintainer's stance: "or that just could be old code that did this for no real reason"
   - Final status: Issue locked and converted (Jan 15, 2026)

2. **Apache Arrow: The Sound of Silence**
   - Response time: 17 minutes (maintainer @raulcd engages)
   - Maintainer reveals: "those jobs have been failing for several weeks now"
   - The file might be deleted entirely (issue #48766)
   - Maintainer asks: "Were you manually using this?"
   - User admits: "I was simply auditing the CI scripts"
   - Final status: **Still open, likely to be deleted** (no follow-up as of Jan 25, 2026)

3. **scikit-learn: The Plot Twist**
   - Initial response: User offers to fix (Jan 14, 2026)
   - Community engagement: Another contributor (@Ananyaearth) asks to take it (Jan 21)
   - PR submitted: #33120 (Jan 21, 2026)
   - **MAJOR TWIST** (Jan 23): Maintainer @ogrisel says *"This script has many other problems... I would rather just delete this file"*
   - Timeline revealed: Function deprecated in **v0.23 (2020)**, bug discovered in **2026** — **6 years of broken benchmarks**
   - Final outcome: PR pivoted from "fix" to "delete"

**ACT III: The Emotional Resonance**

Create interactive "You-Draw-It" elements:

1. **"Predict the Response Time"**: Let readers guess how long each maintainer took to respond
   - Reveal: SQLAlchemy (8 min), Arrow (17 min), scikit-learn (7 days for meaningful engagement)

2. **"Match the Response"**: Before revealing, let readers match each project to:
   - "Not a bug, use it correctly"
   - "We're probably deleting this anyway"
   - "Let's fix it... wait, let's delete it"

**VISUALIZATIONS (Push Orthodox Boundaries):**

1. **Timeline of Decay**: For scikit-learn
   ```
   2020 ─────────────────────────── 2026
    ↑                                  ↑
   v0.23                           Discovery
   Function removed              6 years later
   ```

2. **Response Spectrum Chart**:
   ```
   Defensive ← → Pragmatic ← → Action
   SQLAlchemy    Arrow      scikit-learn
   ```

3. **The Archaeology Visualization**: Show code snippets side-by-side
   - SQLAlchemy: Inconsistent None-guards in *same method*
   - Arrow: `os.environ.get()` without fallback
   - scikit-learn: Import statement from 2020 still present in 2026

**KEY STATISTICS TO MAKE EMOTIONALLY RESONANT:**

- **8 minutes**: Time for SQLAlchemy to reject (faster than most bug reports are read)
- **6 years**: Time scikit-learn benchmark stayed broken
- **3/3**: Projects where the "fix" wasn't actually fixing code (reject, delete, delete)
- **92,600 combined stars**: Scale of codebases affected
- **100% maintainer engagement**: All three responded (different outcomes, but all engaged)

**THE "DON'T BE A DATA FASHION VICTIM" ELEMENTS:**

- NO generic bug severity pie charts
- NO "issues closed over time" trend lines
- FOCUS on **maintainer psychology**: defensive vs pragmatic vs action-oriented
- HIGHLIGHT the **human moments**: "What are we doing here exactly?", "Are you still working on this?", "I was simply auditing"

**INTERACTIVE ELEMENTS:**

1. **Code Checker Widget**: Let readers paste a Python function and check for similar `None`-handling issues
2. **Response Predictor Game**: Guess which project said what before revealing
3. **Timeline Explorer**: Scroll through the 6-year gap in scikit-learn

**ENDING (Statistical Emotional Resonance):**

Don't moralize. End with three parallel timelines showing:
- SQLAlchemy: Issue closed in 30 hours
- Arrow: Issue open for 11 days (and counting)
- scikit-learn: Issue open for 9 days, PR pivoted, file to be deleted

Final line: *"In Python's None-handling underworld, every TypeError tells a story. This one told three."*

**TECHNICAL IMPLEMENTATION:**

- Mobile-responsive design
- Scroll-triggered animations for each "reveal"
- Color coding: Red (rejected), Yellow (limbo), Purple (deleted)
- Syntax-highlighted code blocks
- Working interactive prediction game
- Embedded actual GitHub quotes in styled blockquotes
- Repository links with star counts
- Timeline scrubber showing each interaction

**CALL TO ACTION:**

- Link to verification repo: `github.com/PythonicVarun/py-libraries-analysis`
- "Check your own codebase" tool
- Encourage type-checking in CI pipelines

Generate the complete single-page HTML with all interactive elements, proper styling, and the emotional weight of Amanda Cox's best work. Make developers stop scrolling and think: *"This could be my PR getting the 'What are we doing here exactly?' response."*
