#!/usr/bin/env python3
"""E2E driver: real ingest from the live static-API commons + real AOAI answers.

Runs the exact production path (Assistant.run -> tool call -> KnowledgeCompanion ->
grounded compose) locally with LocalFileStorageManager, against live raw URLs and a
live Azure OpenAI deployment. Not a mocked test — this is the evidence run.

Usage:
    python tests/e2e_knowledge_companion.py            # full run (retrieval + LLM)
    python tests/e2e_knowledge_companion.py --dry      # retrieval only, no LLM
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Local-mode config BEFORE imports. Point these at YOUR Azure OpenAI resource
# (az login first if the resource uses Entra ID auth).
os.environ.setdefault("USE_CLOUD_STORAGE", "false")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")
if "--dry" not in sys.argv and not os.environ.get("AZURE_OPENAI_ENDPOINT"):
    sys.exit("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT_NAME to run the full E2E "
             "(or use --dry for retrieval-only, no LLM needed).")
os.environ.setdefault("ASSISTANT_NAME", "S4HANA Knowledge Companion")
os.environ.setdefault(
    "CHARACTERISTIC_DESCRIPTION",
    "knowledge companion for the S/4HANA transformation program",
)

QUESTIONS = [
    "Who is responsible for the Finance workstream, and who covers if they're out?",
    "Who owns the Procure-to-Pay process?",
    "Which resources are available for the change management and training stream?",
    "I have a data migration blocker that's been open for a week - who do I escalate to, and who is their backup?",
]


def dry_run():
    from agents.knowledge_ingest_agent import KnowledgeIngestAgent
    from agents.knowledge_companion_agent import KnowledgeCompanionAgent

    ingest = KnowledgeIngestAgent()
    print("== INGEST ==")
    print(ingest.perform(action="refresh"))
    companion = KnowledgeCompanionAgent()
    for q in QUESTIONS:
        print(f"\n== RETRIEVAL: {q}")
        result = json.loads(companion.perform(question=q))
        for p in result.get("passages", []):
            print(f"  [{p['rank']}] {p['source']} › {p['section']} (score-ranked)")


def full_run():
    from function_app import Assistant, load_agents_from_folder

    agents = load_agents_from_folder()
    assert "KnowledgeCompanion" in agents and "KnowledgeIngest" in agents, \
        f"knowledge agents not loaded: {list(agents)}"

    # Fresh ingest so the run exercises the live commons.
    print("== INGEST ==")
    print(agents["KnowledgeIngest"].perform(action="refresh"))

    for q in QUESTIONS:
        assistant = Assistant(agents)
        answer, voice, logs = assistant.run(q, [{"role": "user", "content": q}])
        print(f"\n{'=' * 72}\nQ: {q}\n{'-' * 72}")
        print(answer)
        print(f"[voice] {voice}")
        print(f"[agents used] {logs.splitlines()[0][:120] if logs else 'NONE - NOT GROUNDED!'}")


if __name__ == "__main__":
    if "--dry" in sys.argv:
        dry_run()
    else:
        full_run()
