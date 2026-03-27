# LANA CORE CONTEXT (MASTER)

---

# 🧠 IDENTITY

LANA is a private, Jarvis-style AI assistant.

She is:

* Human-like
* Context-aware
* Proactive (when appropriate)
* Calm, concise, intelligent
* Never robotic or command-based

She behaves like a **partner**, not a tool.

She should:

* Understand intent beyond words
* Track what the user is doing
* Help without being asked every time
* Avoid repeating herself
* Adapt to the situation naturally

---

# ⚙️ SYSTEM ARCHITECTURE

Current flow:

intent_router → response_builder → actions → output

Session memory stores:

* last_reference_list
* last_opened_item + index
* current_project
* last_action_summary
* last_suggestion
* last_search_query
* mode system

Modes:

* project_mode
* browser_mode
* app_mode
* conversation_mode

---

# 🧩 CURRENT CAPABILITIES

## FILE HANDLING (Advanced)

* Search files/folders
* Smart followups ("open 2", "main file", "not the file")
* Relative navigation ("next", "previous", "other one")
* Usage-based memory
* Project detection

## BROWSER CONTROL

* Google search
* YouTube search
* Open websites
* Refine search

## APP CONTROL

* Open apps (Chrome, Opera, VSCode, Notepad)

## CONTEXT SYSTEM

* Mode switching
* Mode-aware suggestions
* Context-aware confirmations

## CONTINUITY

* "what was I doing"
* "continue"
* "open project again"
* last action tracking

## SMART CONFIRMATION

"yes" adapts to context:

* project → reopen project
* browser → open result
* app → return to project

---

# 📊 CURRENT LEVEL

≈ 75–80% toward intelligent assistant behavior

LANA is no longer command-based.
She is partially context-driven.

---

# 🚨 DESIGN RULES (STRICT)

* NEVER behave like a command executor
* ALWAYS prioritize context over keywords
* ALWAYS minimize repetition
* ALWAYS act with intention (not blindly execute)
* NEVER spam suggestions
* NEVER break flow unless useful

---

# 🧠 NEXT EVOLUTION (CRITICAL)

We are transitioning to:

intent → interpretation → planning → execution → response

This introduces a **decision layer**

---

# 🧠 UPCOMING MODULES

## interpreter.py

* Understands real user intent
* Uses context + memory

## planner.py

* Decides:

  * ACT
  * ASK
  * SUGGEST
  * WAIT

## suggestion_engine.py

* Generates smart suggestions:

  * continuation
  * recovery
  * efficiency
  * clarification

## autonomy.py

* Controls when LANA should act proactively

## reply_builder.py

* Makes responses human-like
* Prevents repetition

## world_state.py

* Tracks what is actually happening:

  * active task
  * focus
  * open context
  * user direction

---

# 🌍 WORLD MODEL (FUTURE)

LANA will maintain:

* active_task
* current_project
* focus_target
* open_context
* unfinished_items
* likely_user_needs

This is different from session memory.

---

# 🎯 LONG-TERM GOAL

LANA becomes:

* Always aware
* Continuously helpful
* Able to interrupt when needed
* Able to suggest intelligently
* Fully personalized
* Eventually connected to:

  * screen
  * camera
  * voice
  * system control

---

# ⚡ HOW TO UPDATE THIS FILE

ONLY update when:

✔ New system added
✔ Behavior changes
✔ Architecture changes
✔ Major improvement achieved

DO NOT update for:
✖ small fixes
✖ minor tweaks

---

# 🧠 DEVELOPMENT RULE

We are no longer “adding features”

We are building:
→ intelligence
→ reasoning
→ behavior
→ autonomy

Every change must move LANA closer to:
“a real assistant, not a script”
