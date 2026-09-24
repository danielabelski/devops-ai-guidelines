<!-- Cover -->

<h1 align="center" style="border-bottom: none">
  <img alt="The Versus SRE Agent" src="https://cdn.jsdelivr.net/gh/VersusControl/devops-ai-guidelines@main/07-evaluating-ai-agents/images/evaluating-ai-agents.svg" width="300">
</h1>

<div align="center">

**GUIDE**

# Evaluating AI Agents

### How to Measure and Improve Any Tool-Using Agent — Using a DevOps Incident Agent as the Running Example

*Everyone can build an agent now; almost no one can prove theirs is getting better. This book teaches the missing skill — scoring an agent against recorded cases whose answers you already know — built end to end on a DevOps and SRE incident agent, and ready to point at your own.*

</div>

---

<!-- Table of Contents -->

## Contents

**0. [Introduction](#introduction)** — Why every team can build an agent but few can
grade one, the one idea that fixes it, and why we learn the skill on a DevOps incident
agent you'll measure from cover to cover.

**1. [Build the AI Agent This Book Runs On](#1-build-the-ai-agent-this-book-runs-on)**
Build the tiny incident-diagnosis agent, run it once, and hit the wall the whole
book is about: a confident answer, and no way to tell if it was right.

**2. [How Do You Evaluate an Agent?](#2-how-do-you-evaluate-an-agent)**
Why an agent is harder to grade than a function, the two things you can actually
grade (the answer and the path to it), and how to scope what you'll measure before
you measure anything. Ends with the smallest grader that works — and the agent that
cheats it.

**3. [The Harness We're Going to Build](#3-the-harness-were-going-to-build)**
The map of the whole book on one page: five parts, how they fit together, and which
chapter builds each. Read this and every chapter after it has an obvious place to sit.

**4. [Record a Test Case Your Agent Will Face](#4-record-a-test-case-your-agent-will-face)**
Freeze one case into a scenario file: the situation the agent is dropped into, and a
separate answer key holding the true cause, the evidence that proves it, the planted
distraction, and the step budget. Record its owner, review date, and assumptions too.

**5. [Replay That Case to Your Agent](#5-replay-that-case-to-your-agent)**
Swap the agent's live data sources for recorded ones of the exact same shape. The
agent investigates a frozen scene after a validity check rejects cases that no
longer represent the current system.

**6. [Keep the Answer Away from the Agent](#6-keep-the-answer-away-from-the-agent)**
Enforce the wall between the two parts of a scenario instead of trusting yourself to
respect it. Why this anti-cheat is the most important rule in the design.

**7. [Score It with Hard Gates](#7-score-it-with-hard-gates)**
Check the cause with a structured answer, confirm the required tools were actually
called, check what happened with the distraction, and enforce the step budget. Keep
"never saw it" distinct from "saw it and rejected it."

**8. [Judge the Explanation with Jev](#8-judge-the-explanation-with-jev)**
Run a real OpenAI agent, then require TypeSafe's Jev model through Cloudflare to
judge what the hard gates cannot read in its explanation. Neither check can turn a
failure in the other green. Ten simulations change one agent setting at a time to
show how both grades guide a better agent.

**9. [Turn Scores into a Benchmark](#9-turn-scores-into-a-benchmark)**
Score only active cases, report expired and historical cases separately, and compare
the same pinned set before claiming the agent improved.

**10. [Close the Loop: Every Miss Becomes a Test](#10-close-the-loop-every-miss-becomes-a-test)**
Turn a real miss into a reviewed scenario with an owner and assumptions; replace or
retire cases when topology, runbooks, or tool contracts change.

**11. [Gate Your Agent in CI](#11-gate-your-agent-in-ci)**
Gate both agent quality on valid cases and suite health: stale cases, missing current
coverage, and unreviewed exclusions must not produce a green build.

**[Additional Resources](#additional-resources)**
