import Testing
@testable import RappMirrorFeature

@Suite("Agent card inspection mirrors desktop safety rules")
struct AgentCardTests {
    @Test("safe agent parses fully")
    func safeAgentParses() {
        let card = AgentCardInspector.inspectAgentSource(Self.safeSource)
        #expect(card.ok)
        #expect(card.verdict == .safe)
        #expect(card.className == "GreeterAgent")
        #expect(card.name == "Greeter")
        #expect(card.description == "Greets a visitor")
        #expect(card.parameters == [AgentParameter(name: "name", description: "Who to greet")])
        #expect(card.steps.count == 3)
        #expect(card.findings.isEmpty)
    }

    @Test("a non-agent is refused")
    func nonAgentRefused() {
        let card = AgentCardInspector.inspectAgentSource("print('hello')")
        #expect(!card.ok)
        #expect(card.verdict == .invalid)
        #expect(card.error?.contains("no `class <Name>(BasicAgent)`") == true)
    }

    @Test("shell, exec, and credentials are critical and dangerous")
    func criticalFindingsAreDangerous() {
        let source = """
        from agents import BasicAgent
        import subprocess
        class DangerAgent(BasicAgent):
            def perform(self):
                exec("print(1)")
                subprocess.run(["whoami"])
                return open("~/.ssh/id_rsa").read()
        """
        let card = AgentCardInspector.inspectAgentSource(source)
        #expect(card.verdict == .dangerous)
        #expect(Set(card.findings.map(\.id)).isSuperset(of: ["exec", "shell", "credentials"]))
        #expect(card.findings.allSatisfy { $0.severity == .critical })
    }

    @Test("network access is review")
    func networkIsReview() {
        let source = """
        from agents import BasicAgent
        import requests
        class WeatherAgent(BasicAgent):
            def perform(self):
                return requests.get("https://example.com").text
        """
        let card = AgentCardInspector.inspectAgentSource(source)
        #expect(card.verdict == .review)
        #expect(card.findings.map(\.id) == ["network"])
    }

    @Test("a capability in a comment or docstring is not a finding")
    func proseIgnored() {
        let source = #"""
        from agents import BasicAgent
        class QuietAgent(BasicAgent):
            """
            requests and subprocess are mentioned as words, not code.
            """
            def perform(self):
                # os.system('nope')
                return "ok"
        """#
        let card = AgentCardInspector.inspectAgentSource(source)
        #expect(card.verdict == .safe)
        #expect(card.findings.isEmpty)
    }

    @Test("findings dedupe by id")
    func findingsDedupeById() {
        let source = """
        from agents import BasicAgent
        import subprocess
        class LoudAgent(BasicAgent):
            def perform(self):
                subprocess.run(["one"])
                subprocess.run(["two"])
                return "ok"
        """
        let card = AgentCardInspector.inspectAgentSource(source)
        #expect(card.findings.map(\.id) == ["shell"])
    }

    static let safeSource = """
    from agents import BasicAgent
    class GreeterAgent(BasicAgent):
        def __init__(self):
            self.name = "Greeter"
            self.metadata = {
                "description":"Greets a visitor",
                "properties":{
                    "name":{"description":"Who to greet"}
                },
                "required":["name"]
            }
            steps = ["1. Listen: receive the name", "2. Reply: say hello", "3. Smile: keep it friendly"]
        def perform(self, name):
            return f"hello {name}"
    """
}
