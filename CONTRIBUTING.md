# Contributing to Mercury MCP

Mercury is an independent research project. I welcome contributions but want to keep the scope and quality bar clear.

## How to get involved (pick a level)

### Level 1: Try it + tell me what broke (5 min)

Install Mercury MCP, point your Claude Code / Cursor at it, try a few of the example prompts in `examples/example-prompts.md`. If anything breaks, doesn't make sense, or you have a use case in mind, open an Issue. The most helpful feedback right now is "I tried X and got Y, expected Z".

### Level 2: Add a new model observation (1-3 hours)

Mercury currently has 23 models in v0.1. If you have an LLM I haven't observed and the hardware to run it, you can contribute new Tier-A or Tier-B observations.

Open an Issue first with the model you want to add. I will share the observation script and tell you the data format. We will merge the new model after I verify the data passes basic sanity checks.

### Level 3: Methodology contribution (open-ended)

I am actively working through a methodology question: when does Tier-A "universal anchor" reflect real residual stream features versus tokenizer artifacts? See the LessWrong shortform discussion or the Paper A draft.

If you have ideas, prior work, or want to design a control experiment, open an Issue or start a Discussion. This is the area where outside collaboration is most valuable to me right now.

### Level 4: Paper co-authorship

I am writing several papers based on Mercury data. If you are interested in co-authoring, this requires substantive contribution to either: new observations, methodology design, theoretical framing, or experimental analysis.

Open a Discussion or email me at abbychen981008@gmail.com with: your background, ORCID if you have one, which paper you want to contribute to, and the specific contribution you propose. We agree on scope before any writing starts.

## What I do not need right now

- Generic "you should add X feature" issues without specific use case
- Cosmetic PRs (formatting, typos in single sentences). Save the round trip
- Long-term commitment offers ("let me run Mercury for you") at this stage

## Project values

Three things I optimize for:

1. **Reproducibility**: every claim ties to a public Zenodo DOI or GitHub commit
2. **Self-correction**: when methodology is wrong, fix it in public (see Tier-A vs Tier-B caveat in README)
3. **Outsider-accessible**: built on consumer hardware. PRs that require GPU clusters get deprioritized

## Code & data license

- Code: MIT
- Data (observation JSONs): CC-BY-4.0
- Contributors retain copyright of their contributions and agree to license them under the same terms

## Contact

- Issues + Discussions: preferred for everything project-related
- Email: abbychen981008@gmail.com for paper co-authorship or sensitive matters
- Scholar profile: https://scholar.google.com/citations?user=wrTR3VMAAAAJ

## Maintainer

norika (Chen Ho Yiing), Independent Researcher, Taiwan
ORCID: 0009-0006-6816-9891

I will respond to Issues and Discussions within 7 days. If urgent, mention me directly in a comment.
