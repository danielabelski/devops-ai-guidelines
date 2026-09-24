## 4. Record a Test Case Your Agent Will Face

*Turn one solved incident into a test you can run again, with the situation on one
side and the known answer on the other.*

The checkout incident is over. The service is healthy, the logs will soon roll away,
and the database pool is back to normal. If we leave the facts in production, we lose
the case.

This chapter saves it as a *scenario*: one recorded situation plus an answer key. By
the end, you can load the file, inspect both sides, and reject an incomplete record.
We won't run the agent yet. First we need a case worth replaying.

### What we are building

A scenario has two jobs that must not be mixed:

- The **situation** recreates what the agent could have seen during the incident.
- The **answer key** records what we learned after the incident was solved.

![A scenario split into a situation for the agent and an answer key for the grader](./images/scenario-anatomy.svg)

Read the figure from the center. Both sides belong to one case, but they have
different readers. The alert and recorded tool responses will go to the agent. The
true cause and grading rules will go to the grader in Chapter 7. Chapter 6 will turn
the dotted boundary into a code boundary.

This split matters because incident truth often arrives late. During an outage, an
engineer sees alerts, logs, metrics, and recent changes. After the fix, the team knows
which signal was proof and which one only looked suspicious. A useful test case keeps
both views.

There is a third part, outside both views: *validity metadata*. It says when and for
which version of the system this case still applies. The agent does not need it, but
the runner must check it before replay.

### Step 1: choose a solved case

Start with an incident that has a confirmed cause. "We think it was the database"
isn't enough. You need evidence strong enough that another engineer would reach the
same answer.

For our case, the timeline is clear:

| Time | Event | Meaning |
|---|---|---|
| 14:02 | A deploy changes `DB_MAX_CONNECTIONS` from 50 to 5 | Candidate cause |
| 14:03 | Checkout latency crosses two seconds | Customer impact begins |
| 14:03 | All five connections are busy and 40 requests wait | The pool is exhausted |
| 14:06 | Payment-provider latency rises from 90 ms to 180 ms | Real, but too late to cause the incident |

The deploy and pool status prove the cause together. The payment-provider line is a
good distraction because it is believable but contradicted by the order of events.

> **Warning:** Don't create answer keys from unresolved incidents. A disputed answer
> turns the benchmark into a test of one author's opinion.

### Record what makes this case valid

A frozen incident can become a bad test without its file changing. If checkout stops
using this database pool, the old case may still pass while testing a system that no
longer exists. Record assumptions that someone can check against the *current*
system, not just a date:

```json
"validity": {
  "owner": "checkout on-call",
  "recorded_at": "2026-09-12",
  "review_by": "2026-12-12",
  "assumptions": {
    "topology": "checkout-db-pool-v1",
    "runbook": "checkout-latency-v2",
    "tool_contract": "incident-tools-v1"
  }
}
```

The owner reviews the case by `review_by`, even when no known dependency has changed.
The three named versions are examples, not facts the recording can verify on its own.
Chapter 5 compares them with a manifest supplied from outside the case. If a version
differs, the case expires before it can return a green score. Keep historical cases
for old systems if useful, but do not count them as current coverage.

### Step 2: record the situation

Create the Chapter 4 folder and open
`scenarios/checkout-latency.json`. The first half is the situation:

```json
{
  "id": "checkout-latency-after-pool-change",
  "situation": {
    "alert": {
      "service": "checkout-service",
      "message": "checkout-service p95 latency > 2s",
      "started_at": "14:03"
    },
    "tool_responses": {
      "get_metrics": { "service": "checkout-service", "...": "..." },
      "get_logs": { "service": "checkout-service", "...": "..." },
      "get_deploys": { "service": "checkout-service", "...": "..." },
      "get_db_status": { "service": "checkout-service", "...": "..." }
    }
  }
}
```

The abbreviated values above keep the page readable; the file in the chapter folder
contains every response. Record the values the real tools returned, not a summary of
them. Chapter 5 will serve these values through replay tools, so their shape needs to
match what the agent already expects.

Record enough context to make the case understandable on its own:

- Give the scenario a stable `id`. Reports and benchmarks will use it later.
- Keep the original alert, including its service and start time.
- Save one response per tool that the agent may call.
- Keep misleading signals. Removing them makes the test easier than the real job.
- Remove secrets and personal data before the file enters source control.
- Record an owner and the system assumptions whose change would invalidate the case.

### Step 3: write the answer key

The second half records the truth and the rules for this one case:

```json
"answer_key": {
  "true_category": "deploy",
  "true_cause": "The 14:02 deploy reduced DB_MAX_CONNECTIONS from 50 to 5, exhausting the connection pool.",
  "required_evidence": ["get_deploys", "get_db_status"],
  "distraction": "payment-provider latency increased at 14:06",
  "max_steps": 5
}
```

Each field answers a grading question:

| Field | Question it answers |
|---|---|
| `true_category` | Did the agent classify the cause correctly? |
| `true_cause` | What actually happened? |
| `required_evidence` | Which tool results prove it? |
| `distraction` | Which believable wrong lead should it reject? |
| `max_steps` | How much investigation is reasonable for this case? |

The answer key should describe one acceptable result, not prescribe every sentence
the agent must write. We compare the structured category exactly in Chapter 7. We
leave judgment about the prose to Chapter 8.

The step budget also belongs to the case, not to the agent. This case needs five
actions to inspect metrics, logs, deploys, and pool status before concluding. A broad
dependency failure may need more. One global budget would make easy cases too loose
and hard cases impossible.

### Step 4: see how recording works

Recording is a small editing process, not an automated dump of production.

![A solved live incident becomes a reviewed and sanitized scenario file](./images/recording-workflow.svg)

The middle review is where most of the value is added. Raw telemetry tells you what
happened at the time. The incident review tells you what mattered. Sanitizing removes
data that should not enter a test repository. Only then do you save the situation and
answer key together.

A recorder could automate collection later. Keep the review step even then. A tool
can collect logs; it cannot decide by itself that the payment-provider line is the
right distraction or that five steps is a fair budget.

### Step 5: load and validate the file

The loader turns loose JSON into named records:

```python
@dataclass(frozen=True)
class Situation:
    alert: Dict[str, str]
    tool_responses: Dict[str, Any]


@dataclass(frozen=True)
class AnswerKey:
    true_category: str
    true_cause: str
    required_evidence: List[str]
    distraction: str
    max_steps: int


@dataclass(frozen=True)
class Validity:
  owner: str
  recorded_at: str
  review_by: str
  assumptions: Dict[str, str]


@dataclass(frozen=True)
class Scenario:
    id: str
  validity: Validity
    situation: Situation
    answer_key: AnswerKey
```

`Validity` holds the owner, dates, and assumptions shown above. `frozen=True` stops
code from replacing a loaded record field by accident; nested dictionaries can still
be changed, so replay returns copies. The loader also checks required fields and
rejects a step budget below one. This small validation catches broken records without
hiding the format behind a large framework; it does not prove the case is still current.

Run the check from the chapter folder:

```bash
cd devops-ai-guidelines/07-evaluating-ai-agents/code/chapter-04
python check_scenario.py
```

```text
Scenario:          checkout-latency-after-pool-change
Review by:         2026-12-12
Assumptions:       topology, runbook, tool_contract
Alert:             checkout-service p95 latency > 2s
Recorded tools:    get_metrics, get_logs, get_deploys, get_db_status
True category:     deploy
Required evidence: get_deploys, get_db_status
Step budget:       5
```

That output is an inventory, not a score or a live validity check. It shows the
inputs, known answer, and assumptions that later chapters need.

### A failure worth catching early

Suppose someone records the alert and logs but forgets `required_evidence`. The agent
can still run, and a category-only grader can still pass it. Weeks later, nobody can
tell whether the agent diagnosed the pool change or guessed "deploy."

The loader rejects that scenario when it enters the suite:

```text
ValueError: answer_key is missing: required_evidence
```

Failing at load time is better than publishing a score based on an incomplete case.

### Where else this applies

The schema stays the same when the job changes. Only the values differ.

| Agent | Situation | Answer key |
|---|---|---|
| Support | Ticket, account state, policy lookups | Correct resolution, required policy, misleading detail |
| SQL | Question, schema, recorded query results | Expected result, required tables, query budget |
| Code fixing | Issue, repository state, test output | Correct behavior, required test, unrelated failure |
| Research | Question and recorded sources | Supported answer, required sources, false lead |

### Summary

- A scenario is one reusable test case with a situation and an answer key.
- Record raw tool responses in the same shape the live tools return.
- Keep realistic distractions; don't clean the case until it becomes trivial.
- Write the answer key only after the cause is confirmed and reviewed.
- Validate every scenario before it enters the benchmark.
- Record the system assumptions and review date that determine when it expires.

Next: turn the recorded responses into tools the unchanged agent can call.