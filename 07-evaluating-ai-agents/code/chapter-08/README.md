# Chapter 8 - Real Agent and Required Jev Judge

This folder is self-contained. OpenAI chooses the next recorded incident tool; Jev
evaluates the finished explanation through Cloudflare Workers AI. Both services
need credentials for the full run. The tools replay synthetic incidents, not
production data. Three cases use the same checkout-service tools with different
causes: `pool` (deploy), `dependency` (payment provider), and `capacity` (workers).

1. Activate `ai-agent` (Python 3.10 or newer) and install
   [requirements.txt](requirements.txt) in this folder:

   ```bash
   conda activate ai-agent
   python -m pip install -r requirements.txt
   ```

2. Fill the existing ignored `.env` using [.env.example](.env.example) as the
   field guide. Use your OpenAI API key in `OPENAI_API_KEY`, and the Workers AI
   account ID and API token in `CLOUDFLARE_ACCOUNT_ID` and
   `CLOUDFLARE_API_TOKEN`. The default OpenAI model is `gpt-4.1-mini`.
   `JEV_MODEL` names the Jev model to call.
   Never commit `.env` or paste keys into a scenario or the book.

3. Start with [run_agent.py](run_agent.py), which needs only the OpenAI key:

   ```bash
   python run_agent.py
   ```

   It prints the agent's *actual* answer, selected tool calls, structured cause,
   citations, rejected signals, and steps. No score or Jev call happens here.

4. Compare the three different causes using [run_cases.py](run_cases.py):

   ```bash
   python run_cases.py --runs 1
   ```

   This writes every answer and hard gate to ignored `case-results.json`.
   These are not complete grades because this command does not call Jev.
   Use `python run_agent.py --case dependency` or `--case capacity` to inspect
   one case. The default is `pool`.

5. Compare three *alert phrasings of the pool case*, two runs each, using
   [run_trials.py](run_trials.py):

   ```bash
   python run_trials.py --runs 2
   ```

   Only the alert message changes. Every attempt, including errors and failed
   hard gates, goes into ignored `trial-results.json`. The summary alone is not
   proof that a wording generalizes to other incidents. This does not call Jev.

6. Run [run_judge.py](run_judge.py) with both providers configured:

   ```bash
   python run_judge.py
   ```

   This makes a **new** OpenAI run, prints its answer, then loads the hidden answer
   and sends an approved summary to Jev. The two commands can produce different
   answers. Judge failures, low-confidence responses, and hard-gate failures
   never print a pass and exit nonzero.

   Add `--case dependency` or `--case capacity` to select the other cases.
   `python run_cases.py --judge --runs 1` records all three complete evaluation
   attempts in ignored `case-judge-results.json`.

7. Run the numbered simulations in
   [scenarios/simulations](scenarios/simulations) with
   [run_simulations.py](run_simulations.py):

   ```bash
   python run_simulations.py
   ```

   Each `checkout-latency-NN.json` changes one thing: the agent instructions,
   the step budget, the alert wording, or the incident cause. The run prints
   each answer, its hard gates, and Jev's scores, then a summary table. It
   writes ignored `simulation-results.json`. Use `--only checkout-latency-01`
   to run one simulation, or `--no-judge` to skip Jev.

8. The [test files](test_agent.py) use mocked OpenAI and Jev responses. They do
   not use either key and do not prove model accuracy:

   ```bash
   python -m unittest discover -p 'test_*.py'
   ```

`config.py` reads `.env` without overriding already configured environment
variables. `agent.py` owns the OpenAI function-call loop, `replay.py` supplies
recorded read-only tools, `grade.py` applies Chapter 7's hard gates, and
`jev_judge.py` owns the grader-only Cloudflare request. The case expires on
`2026-12-12`; review its assumptions before extending that date. This local
example's `CURRENT_SYSTEM` is a demo inventory, not live topology validation.