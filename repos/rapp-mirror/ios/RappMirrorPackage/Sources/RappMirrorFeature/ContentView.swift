import SwiftUI

/// The app's root. The mirror is a voice interface first — the card gallery
/// lives behind it, reachable from the header, not in front of it.
public struct ContentView: View {
    public init() {}

    public var body: some View {
        MirrorVUI()
    }
}

struct GalleryCard: Identifiable, Equatable {
    let id: String
    let spec: ForgeSpec
    let card: CardFace
    let shareURL: String

    init(spec: ForgeSpec, shareURL: String? = nil, inspectedCard: AgentCard? = nil) {
        self.spec = spec
        self.card = CardArt.mintCard(inspectedCard ?? spec.agentCard)
        self.shareURL = shareURL ?? ShareURL.encodeShareUrl(spec).url ?? "rapp://agent?v=1&n=\(spec.name)&d=damaged"
        self.id = "\(spec.className)-\(card.seed)"
    }

    static func damaged(url: String, error: String) -> GalleryCard {
        let finding = Finding(severity: .critical, id: "invalid", detail: error, line: 0, evidence: url)
        let card = AgentCard(ok: true, verdict: .dangerous, className: "DamagedCard", name: "Damaged Card", description: error, parameters: [], steps: ["1. Stop: do not install this card"], findings: [finding], lineCount: 0)
        let spec = ForgeSpec(name: "damaged", className: "DamagedCard", title: "Damaged Card", description: error, intent: "Reject a damaged card")
        return GalleryCard(id: "damaged-\(UUID().uuidString)", spec: spec, card: CardArt.mintCard(card), shareURL: url)
    }

    private init(id: String, spec: ForgeSpec, card: CardFace, shareURL: String) {
        self.id = id
        self.spec = spec
        self.card = card
        self.shareURL = shareURL
    }

    static let samples: [GalleryCard] = [
        GalleryCard(spec: ForgeSpec(
            name: "greeter",
            className: "GreeterAgent",
            title: "Greeter",
            description: "Greets a visitor",
            intent: "Say hello safely",
            steps: [ForgeStep(title: "Listen", detail: "Receive a name"), ForgeStep(title: "Reply", detail: "Say hello"), ForgeStep(title: "Smile", detail: "Keep it friendly")],
            parameters: [ForgeParameter(name: "name", description: "Who to greet", type: "string", required: true)]
        )),
        GalleryCard(spec: ForgeSpec(
            name: "weather",
            className: "WeatherAgent",
            title: "Weather Scout",
            description: "Checks the sky before you leave",
            intent: "Summarize weather for a city",
            steps: [ForgeStep(title: "Locate", detail: "Choose a city"), ForgeStep(title: "Fetch", detail: "Call a weather service"), ForgeStep(title: "Summarize", detail: "Explain the forecast")],
            parameters: [ForgeParameter(name: "city", description: "City name", type: "string", required: true)]
        ), inspectedCard: AgentCardInspector.inspectAgentSource(weatherSource)),
        GalleryCard(spec: ForgeSpec(
            name: "shell",
            className: "ShellAgent",
            title: "Shell Wisp",
            description: "Runs a local command",
            intent: "Demonstrate a card that needs human caution",
            steps: [ForgeStep(title: "Warn", detail: "Explain the requested command"), ForgeStep(title: "Run", detail: "Invoke a command only after consent")]
        ), inspectedCard: AgentCardInspector.inspectAgentSource(shellSource))
    ]

    private static let weatherSource = """
    from agents import BasicAgent
    import requests
    class WeatherAgent(BasicAgent):
        def __init__(self):
            self.name = "Weather Scout"
            self.metadata = {"description":"Checks the sky before you leave","properties":{"city":{"description":"City name"}},"required":["city"]}
            steps = ["1. Locate: Choose a city", "2. Fetch: Call a weather service", "3. Summarize: Explain the forecast"]
        def perform(self, city):
            return requests.get("https://example.com").text
    """

    private static let shellSource = """
    from agents import BasicAgent
    import subprocess
    class ShellAgent(BasicAgent):
        def __init__(self):
            self.name = "Shell Wisp"
            self.metadata = {"description":"Runs a local command","properties":{},"required":[]}
            steps = ["1. Warn: Explain the requested command", "2. Run: Invoke a command only after consent"]
        def perform(self):
            return subprocess.check_output(["whoami"])
    """
}
