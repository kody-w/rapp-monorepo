import SwiftUI

/// The mirror on iPhone.
///
/// This is the whole product: a living orb you hold to talk to, and the choices
/// it offers orbiting it as portals. Everything else — agent cards, the inbox,
/// diagnostics — is somewhere behind it, because the interface *is* the voice.
public struct MirrorVUI: View {
    @State private var phase: MirrorPhase = .idle
    @State private var prompt = "Where to?"
    @State private var portals: [HoloOption] = MirrorVUI.openingPortals
    @State private var lastSaid = ""
    @State private var transcript: [ChatTurn] = []
    @State private var engine: BrainstemHealth?
    @State private var notice: String?
    @State private var cardsSheet: CardsSheet?
    @State private var muted = false

    /// What the cards sheet is showing.
    ///
    /// Driving it with an item rather than a bool is not a style choice: with
    /// `.sheet(isPresented:)` the content closure is built from state captured
    /// before the same update sets it, so a scanned card presented the gallery
    /// with `arrived` still nil. The value has to travel *with* the
    /// presentation.
    enum CardsSheet: Identifiable {
        case gallery
        case arrived(GalleryCard)

        var id: String {
            switch self {
            case .gallery: "gallery"
            case .arrived(let card): card.id
            }
        }

        var card: GalleryCard? {
            if case .arrived(let card) = self { return card }
            return nil
        }
    }

    @State private var voice = Voice()
    /// The companion this phone is carrying. Every turn below adds a tile to
    /// it, so the thing you talk to is also the thing that remembers.
    @State private var companion = Companion()
    @State private var showTiles = false
    private let client: BrainstemClient
    private let sessionId = "ios-\(UUID().uuidString.prefix(8))"

    static let openingPortals = [
        HoloOption(label: "What can you do"),
        HoloOption(label: "Show me a task"),
        HoloOption(label: "What is RAPP"),
    ]

    public init(brainstemURL: URL = BrainstemSettings.storedURL) {
        client = BrainstemClient(baseURL: brainstemURL)
    }

    public var body: some View {
        ZStack {
            VUI.background.ignoresSafeArea()

            VStack(spacing: 0) {
                header
                Spacer(minLength: 0)
                stage
                Spacer(minLength: 0)
                footer
            }
        }
        .task {
            await voice.requestPermission()
            await refreshEngine()
            await companion.load()
            await companion.record(.woke, ["engine": .string(engine?.ok == true ? "reachable" : "unreachable")])
        }
        .onOpenURL(perform: openCard)
        .sheet(item: $cardsSheet) { sheet in AgentCardsSheet(arrived: sheet.card) }
    }

    /* ── chrome ─────────────────────────────────────────────────────── */

    private var header: some View {
        HStack(alignment: .center) {
            engineDot
            Spacer()
            Button {
                muted.toggle()
                if muted { voice.hush() }
            } label: {
                Image(systemName: muted ? "speaker.slash.fill" : "speaker.wave.2.fill")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(VUI.ink.opacity(0.7))
                    .frame(width: 40, height: 40)
                    .background(VUI.card, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
            }
            .accessibilityIdentifier("mute")
            .accessibilityLabel(muted ? "Unmute the mirror" : "Mute the mirror")

            Button { cardsSheet = .gallery } label: {
                Image(systemName: "rectangle.stack")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(VUI.ink.opacity(0.7))
                    .frame(width: 40, height: 40)
                    .background(VUI.card, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
            }
            .accessibilityIdentifier("open-cards")
            .accessibilityLabel("Agent cards")

            Button { showTiles = true } label: {
                Image(systemName: "square.grid.2x2.fill")
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(VUI.ink.opacity(0.7))
                    .frame(width: 40, height: 40)
                    .background(VUI.card, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
            }
            .accessibilityIdentifier("open-companion")
            .accessibilityLabel("Companion tiles")
        }
        .padding(.horizontal, 20)
        .padding(.top, 6)
        // Presented from the header rather than the root: two sheets on one
        // view fight over the same presentation slot, and the loser silently
        // never appears.
        .sheet(isPresented: $showTiles) { CompanionTilesView(companion: companion) }
    }

    private var engineDot: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(engine?.ok == true ? Color(red: 0.204, green: 0.827, blue: 0.6) : VUI.dim)
                .frame(width: 9, height: 9)
            Text(engineLabel)
                .font(.system(size: 12))
                .foregroundStyle(VUI.dim)
        }
        // The dot and its words are one fact, not two: a screen reader should
        // say "brainstem connected, 12 agents", never announce a bare circle.
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("engine-state")
        .accessibilityLabel("Brainstem \(engineLabel)")
    }

    private var engineLabel: String {
        guard let engine else { return "reaching for the brainstem…" }
        if engine.ok {
            return "\(engine.model ?? "connected") · \(engine.agents.count) agents"
        }
        return engine.error ?? "no brainstem"
    }

    /* ── the stage: prompt, portals, orb ────────────────────────────── */

    private var stage: some View {
        VStack(spacing: 10) {
            Text(prompt)
                .font(.system(size: 25, weight: .semibold))
                .foregroundStyle(VUI.ink)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)
                .accessibilityIdentifier("prompt")

            ZStack {
                Orb(phase: phase) { pressed in
                    pressed ? beginHold() : endHold()
                }
                PortalRing(options: portals) { pick($0) }
                    .allowsHitTesting(phase != .listening)
            }
            .frame(height: 430)
            .animation(.spring(response: 0.45, dampingFraction: 0.82), value: portals.map(\.label))
        }
    }

    /* ── footer: what was just said ─────────────────────────────────── */

    private var footer: some View {
        VStack(alignment: .leading, spacing: 8) {
            if let notice {
                Text(notice)
                    .font(.system(size: 12.5))
                    .foregroundStyle(VUI.pink)
                    .accessibilityIdentifier("notice")
            }
            if !heardOrSaid.isEmpty {
                Text(heardOrSaid)
                    .font(.system(size: 14))
                    .foregroundStyle(VUI.ink.opacity(0.82))
                    .lineLimit(4)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(14)
                    .background(VUI.card, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                    .shadow(color: VUI.ink.opacity(0.08), radius: 18, y: 10)
                    .accessibilityIdentifier("transcript")
            }
        }
        .padding(.horizontal, 20)
        .padding(.bottom, 18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .animation(.easeOut(duration: 0.25), value: heardOrSaid)
    }

    private var heardOrSaid: String {
        phase == .listening ? voice.partial : lastSaid
    }

    /* ── the loop ───────────────────────────────────────────────────── */

    private func beginHold() {
        guard phase == .idle || phase == .speaking else { return }
        voice.hush()
        notice = nil
        voice.startListening()
        if case .unavailable(let why) = voice.hearing {
            notice = why
            portals = MirrorVUI.wayForward(from: portals)
            if !portals.isEmpty && prompt == "Hold to talk" { prompt = "Where to?" }
            return
        }
        phase = .listening
    }

    /// A mirror that cannot hear and offers nothing is a brick.
    ///
    /// The stage is deliberately left empty when an answer carries no options,
    /// because the next move is to speak. If speech is refused — no language
    /// pack, permission denied — that same empty stage becomes a dead end with
    /// no way out, so the opening portals come back.
    static func wayForward(from portals: [HoloOption]) -> [HoloOption] {
        portals.isEmpty ? openingPortals : portals
    }

    private func endHold() {
        guard phase == .listening else { return }
        let heard = voice.stopListening()
        phase = .idle
        guard !heard.isEmpty else {
            // Silence is still an answer, and it must be acknowledged. A hold
            // that ends with nothing on screen is indistinguishable from a
            // broken microphone.
            notice = "I didn't catch that — hold the orb, speak, then let go."
            return
        }
        notice = nil
        Task { await send(heard) }
    }

    private func pick(_ option: HoloOption) {
        Task { await send(option.send) }
    }

    private func send(_ text: String) async {
        phase = .thinking
        lastSaid = text
        transcript.append(ChatTurn(role: "user", content: text))

        await companion.recordUtterance(.heard, text: text)

        let result = await client.chat(text, history: transcript, sessionId: sessionId)
        guard result.ok, let raw = result.response else {
            // Honest failure, in the interface itself — never a silent stall.
            let why = result.error ?? "the brainstem did not answer"
            // The failure is a tile too. A life with the stalls deleted is a
            // portrait, and the companion's whole job is to be a record.
            await companion.recordUtterance(.stalled, text: why)
            notice = why
            phase = .idle
            return
        }

        transcript.append(ChatTurn(role: "assistant", content: raw))
        let envelope = EnvelopeParser.parse(raw)
        await companion.recordUtterance(.spoke, text: Plain.text(envelope.text), extra: ["model": .string(result.model ?? "unknown")])
        // The brainstem answers in markdown; a voice interface must never show
        // `###` in a glanced-at caption or read `**` aloud.
        lastSaid = Plain.text(envelope.text)
        if let holo = envelope.holo {
            prompt = holo.prompt ?? prompt
            portals = holo.options
        } else {
            portals = []
            prompt = "Hold to talk"
        }

        let spoken = Plain.spoken(envelope.spoken ?? envelope.text)
        if muted || spoken.isEmpty {
            phase = .idle
        } else {
            phase = .speaking
            voice.speak(spoken)
            // The synthesiser has no async completion here; return to rest once
            // it stops rather than pretending to still be speaking.
            Task {
                while voice.isSpeaking { try? await Task.sleep(for: .milliseconds(180)) }
                if phase == .speaking { phase = .idle }
            }
        }
    }

    private func refreshEngine() async {
        engine = await client.health()
    }

    /// A scanned or tapped card. It decodes into a review card — nothing is
    /// installed, on either platform.
    ///
    /// The decoded spec is the point: showing the gallery without it means you
    /// scan someone's card and are shown somebody else's.
    private func openCard(_ url: URL) {
        let decoded = ShareURL.decodeShareUrl(url.absoluteString)
        if decoded.ok, let spec = decoded.spec {
            cardsSheet = .arrived(GalleryCard(spec: spec, shareURL: url.absoluteString))
            Task { await companion.record(.met, ["card": .string(spec.title), "class": .string(spec.className)]) }
            notice = nil
        } else {
            let why = decoded.error ?? "that card could not be read"
            // A card that cannot be read still gets a card, so the reason is
            // somewhere you can look at rather than a vanishing toast.
            cardsSheet = .arrived(GalleryCard.damaged(url: url.absoluteString, error: why))
            notice = why
        }
    }
}
