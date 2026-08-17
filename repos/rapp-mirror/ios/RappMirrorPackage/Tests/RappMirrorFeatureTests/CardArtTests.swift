import Testing
@testable import RappMirrorFeature

@Suite("Card art is deterministic and cross-platform")
struct CardArtTests {
    @Test("same agent mints the identical card twice")
    func identicalTwice() {
        let agent = AgentCardInspector.inspectAgentSource(Samples.greeter)
        #expect(CardArt.mintCard(agent) == CardArt.mintCard(agent))
    }

    @Test("different agents differ")
    func differentAgentsDiffer() {
        let greeter = CardArt.mintCard(AgentCardInspector.inspectAgentSource(Samples.greeter))
        let weather = CardArt.mintCard(AgentCardInspector.inspectAgentSource(Samples.weather))
        #expect(greeter.seed != weather.seed)
        #expect(greeter.dex != weather.dex)
    }

    @Test("identity is identical across all styles")
    func identityDoesNotDependOnStyle() {
        let agent = AgentCardInspector.inspectAgentSource(Samples.greeter)
        let base = CardArt.mintCard(agent, styleId: "prism")
        for style in CardStyleRegistry.credits() {
            let face = CardArt.mintCard(agent, styleId: style.id)
            #expect(face.seed == base.seed)
            #expect(face.trust == base.trust)
            #expect(face.rarity == base.rarity)
            #expect(face.element == base.element)
            #expect(face.dex == base.dex)
            #expect(face.moves == base.moves)
        }
    }

    @Test("every style emits non-empty finite-valued shapes")
    func stylesAreDrawable() {
        let agent = AgentCardInspector.inspectAgentSource(Samples.greeter)
        for style in CardStyleRegistry.credits() {
            let face = CardArt.mintCard(agent, styleId: style.id)
            #expect(!face.art.shapes.isEmpty)
            #expect(face.art.shapes.flatMap(\.numericValues).allSatisfy { $0.isFinite })
        }
    }

    @Test("cross-platform identity matches the TypeScript fixtures")
    func typescriptFixtures() {
        let fixtures: [(String, UInt32, Int, Rarity, Element, String)] = [
            (Samples.greeter, 2_839_900_352, 100, .rare, .spirit, "016 / 151"),
            (Samples.weather, 3_415_989_795, 88, .uncommon, .aether, "148 / 151"),
            (Samples.shell, 3_457_533_502, 65, .cursed, .ember, "131 / 151"),
        ]
        for (source, seed, trust, rarity, element, dex) in fixtures {
            let face = CardArt.mintCard(AgentCardInspector.inspectAgentSource(source))
            #expect(face.seed == seed)
            #expect(face.trust == trust)
            #expect(face.rarity == rarity)
            #expect(face.element == element)
            #expect(face.dex == dex)
        }
    }
}

enum Samples {
    static let greeter = """
    from agents import BasicAgent
    class GreeterAgent(BasicAgent):
        def __init__(self):
            self.name = "Greeter"
            self.metadata = {"description":"Greets a visitor","parameters":{"name":{"description":"Who to greet"}},"required":["name"]}
            steps = ["1. Listen: receive the name", "2. Reply: say hello", "3. Smile: keep it friendly"]
        def perform(self, name):
            return f"hello {name}"
    """

    static let weather = """
    from agents import BasicAgent
    import requests
    class WeatherAgent(BasicAgent):
        def __init__(self):
            self.name = "Weather Scout"
            self.metadata = {"description":"Checks the sky","properties":{"city":{"description":"City name"}},"required":["city"]}
            steps = ["1. Locate: choose city", "2. Fetch: call weather service"]
        def perform(self, city):
            return requests.get("https://example.com").text
    """

    static let shell = """
    from agents import BasicAgent
    import subprocess
    class ShellAgent(BasicAgent):
        def __init__(self):
            self.name = "Shell Wisp"
            self.metadata = {"description":"Runs a local command","properties":{},"required":[]}
            steps = ["1. Run: invoke a command"]
        def perform(self):
            return subprocess.check_output(["whoami"])
    """
}
