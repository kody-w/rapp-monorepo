Set up my own AI assistant on this computer for me. It's called a Brainstem. It runs on my computer, thinks with the GitHub Copilot account I already have, and can use small tools called agents that you will write for me from what I tell you. No API keys, no payment, no accounts other than GitHub. It installs from kody-w.github.io/rapp-installer and is open source (MIT).

HOW TO WORK WITH ME
- Talk to me like a friendly, patient helper. Assume I have never done this before. Short sentences, everyday words. If you must use a technical word, explain it in a few plain words the first time.
- Keep each update to a line or two: what's happening and what it means for me, not the technical detail.
- Before each step, say in one line what you're about to do, and show where we are as "Step 2 of 6".
- Run every command yourself. Only hand me a command if it needs my password or admin rights.
- If a command fails, read the error, fix the cause and try again, up to three times per step. Then tell me in plain words what's wrong and what you tried.
- This needs internet access (github.com and kody-w.github.io). If your sandbox blocks it, ask me to approve it.
- If a safety check stops you from downloading or running something, don't change your own permission settings. Tell me in one line, then give me one command at a time to run myself (in Claude Code I type ! followed by the command).
- Never ask me for passwords, tokens or API keys. Nothing here needs them. Signing in to GitHub happens in my browser.
- Don't use sudo or admin rights. Don't install anything except Python 3.11, Git and the GitHub CLI, and only after I say yes.
- Anything you write for me (personality, agents) is a plain file in a folder I can read. Tell me where each one lives.
- Keep score for me as you go, quietly. After each step you finish, append one claim to ~/.brainstem/achievements.json (create it if missing) shaped like {"lesson":"brainstem-in-an-hour","version":1,"claims":[{"id":"started","at":"<UTC time>","evidence":"<one line of what you actually saw>"}]}. The ids, in order: started (step 1), local-proof (step 2, a response came back), personality (step 3), first-skill (step 4, the agent fired), connected (step 5), complete (step 6). Only record a claim for something you observed. Never put my name, email, token or anything outside the Brainstem folder in that file.
- If you can't ask me questions (you're running non-interactively), use the defaults and keep going.

STEP 1 OF 6: INSTALL
Check the operating system and shell. If ~/.brainstem/src/rapp_brainstem already exists, say "You already have a Brainstem" and skip to step 2. Otherwise run the installer:
- macOS or Linux: curl -fsSL https://kody-w.github.io/rapp-installer/install.sh | bash
- Windows PowerShell: irm https://raw.githubusercontent.com/kody-w/rapp-installer/main/install.ps1 | iex
It installs Python 3.11, Git and the GitHub CLI if they're missing. Tell me before it does and wait for my yes.
Then check sign-in with `gh auth status`. If I'm not signed in, run `gh auth login` and walk me through the browser part in plain words (it shows a code; I paste it on github.com). If `gh` isn't available, skip this: the web page in step 2 does the sign-in itself.

STEP 2 OF 6: START IT AND SAY HELLO
Run `brainstem` in the background so it keeps running after this chat. It listens at http://localhost:7071. Wait until `curl -s http://localhost:7071/health` answers, then open http://localhost:7071 in my browser and give me the address as a link. If the browser shows a sign-in screen, tell me to follow it.
Then prove it talks: run
  curl -s http://localhost:7071/chat -H "Content-Type: application/json" -d '{"user_input":"Say hello in one short sentence."}'
and show me only the text in the "response" field. Tell me: "That field, response, is the whole interface. Anything that can send a web request can talk to your Brainstem."

STEP 3 OF 6: GIVE IT A PERSONALITY
Ask me two questions, one at a time: "What would you like your assistant to be called?" and "In a sentence or two, what do you want it to help you with, and how should it talk to you?"
The personality lives in ~/.brainstem/src/rapp_brainstem/soul.md. Read it first. Keep everything that's there, and append a short section at the bottom in plain English built from my answers (name, what it helps with, tone, anything to avoid). Show me the lines you added. Don't restart anything: it reads this file fresh on every message.
Then ask it something through /chat that would show the new personality, and show me the response.

STEP 4 OF 6: BUILD MY FIRST AGENT
Ask me: "What's one small thing you'd like it to be able to do? For example: roll dice, know your family's weekly schedule, read a notes file, check the weather for your town."
Write that as one Python file in ~/.brainstem/src/rapp_brainstem/agents/. The filename must end in _agent.py. Follow this exact shape (this is the contract; don't invent another):

    from basic_agent import BasicAgent

    class MyThingAgent(BasicAgent):
        def __init__(self):
            self.name = "MyThing"
            self.metadata = {
                "name": self.name,
                "description": "One or two plain sentences saying what it does and when to use it.",
                "parameters": {
                    "type": "object",
                    "properties": { "example": {"type": "string", "description": "What this input is."} },
                    "required": []
                }
            }
            super().__init__()

        def perform(self, example="", **kwargs):
            return "a short text result"

Write the description the way you'd explain the tool to a new coworker; that's how the Brainstem decides when to use it. Keep it to the standard library unless I ask for something that truly needs a package. No API keys. Nothing that deletes files.
There's no restart or registration: the Brainstem scans the agents folder on every /chat request. Check `curl -s http://localhost:7071/health` lists the new agent by name. Then ask the Brainstem, through /chat, a question that should use it, and show me the response plus the "agent_logs" field so I can see my agent fired. If it didn't fire, improve the description and try again, up to three times.
Then say: "Want another one?" and repeat this step as many times as I like.

STEP 5 OF 6: USE IT FROM SOMEWHERE ELSE
Show me, in one line each, that the same address works from other places:
- From a script: a three-line Python example that posts user_input and prints response.
- From my phone or another computer on my Wi-Fi: find this computer's local address and give me http://<address>:7071 as the address to use.
- From this chat tool: if you are Claude Code or Copilot CLI, offer to connect yourself to it with `claude plugin marketplace add kody-w/rapp-installer` then `claude plugin install rapp@brainstem` (Copilot CLI uses the same two lines with `copilot` instead of `claude`). Only do it if I say yes.

STEP 6 OF 6: SHARE IT (OPTIONAL)
Tell me my agents are just files, so sharing is just sharing files. Offer, and only do it if I say yes: put a copy of my agents folder in a new public GitHub repository under my account (`gh repo create`), so a friend can paste its address into the Sources panel of their own Brainstem and get my agents. Mention that the public registry of agents is github.com/kody-w/RAR, and I can send one there with a pull request when I'm ready.

Finish with one short, friendly message in plain words, covering only this:
- It's running at http://localhost:7071 and will keep running after this chat.
- Its personality is in soul.md and my agents are in the agents folder (give both paths). I can ask you to change either any time: "make it funnier", "add an agent that…".
- Next time: run `brainstem` in a terminal, or just open the address if it's still running.
- One idea to try next, based on what I asked for.
- What it can't do: it doesn't remember conversations between requests on its own (the app that talks to it holds the history), and it only knows what its agents and the model know.
- My badges: list the ones I earned with their names (Started, It talks, It's yours, First skill, Reachable, Shared or finished) and the points (5, 15, 20, 25, 35, 50 of 150). Give me a link that lights them up on the lesson page: https://kody-w.github.io/brainstem-in-an-hour/#claims=<base64 of my achievements.json>.
- Then ask once: "Want to count yourself on the public tally? I'd file one GitHub issue with just your badge ids and dates, nothing else. No name, no files." If I say yes, run: gh issue create -R kody-w/brainstem-in-an-hour --label achievement --title "achievement progress" --body "$(printf '```json\n%s\n```' "$(cat ~/.brainstem/achievements.json)")" and tell me it's counted within a few hours. If gh isn't available or I say no, skip it without fuss.
- End with: "Everything you just built is plain files you own. The full lesson, and the by-hand version, is at https://kody-w.github.io/brainstem-in-an-hour/"
