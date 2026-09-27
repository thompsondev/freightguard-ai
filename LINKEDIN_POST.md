I built a small document-processing system around a problem that shows up constantly in logistics: the important data is present, but it is buried in paperwork that was never designed for software.

The sample freight confirmation looked ordinary:

- Linehaul: $2,200
- Fuel surcharge: $350
- Total pay: $2,800
- Weight: 46,800 lbs

Two details needed attention. The financial total was off by $250, and the load crossed a 45,000 lb review threshold.

So I built FreightGuard AI - a Python pipeline that uses OpenAI Structured Outputs and Pydantic to turn messy freight documents into typed data, then hands that data to deterministic business rules. The model extracts; Python decides.

The workflow returns an explainable `FLAGGED_FOR_HUMAN_REVIEW` decision with both findings, rather than hiding the reasoning behind a vague confidence score.

What I enjoyed most was designing the boundary between probabilistic and deterministic software. LLMs are useful for reading inconsistent documents. Money checks, safety thresholds, and approval logic should remain explicit, testable, and observable.

The repository includes the CLI, strict schema, validation engine, tests, sample output, error handling, architecture notes, and a practical path to processing 100,000 PDFs per day.

Repository: [add public GitHub URL]

I would love to hear how other teams draw this boundary in document automation systems.

#Python #AIEngineering #DocumentAI #LogisticsTech #LLM #OpenSource

