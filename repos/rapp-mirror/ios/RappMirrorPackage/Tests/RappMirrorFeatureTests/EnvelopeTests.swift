import Testing
@testable import RappMirrorFeature

@Suite("Envelope parsing matches the desktop mirror")
struct EnvelopeTests {
    @Test("plain text carries no markers and offers nothing")
    func plainText() {
        let e = EnvelopeParser.parse("Just an answer.")
        #expect(e.text == "Just an answer.")
        #expect(e.spoken == nil)
        #expect(e.holo == nil)
    }

    @Test("VOICE section becomes the spoken line and never leaks into the text")
    func voiceSection() {
        let e = EnvelopeParser.parse("Shown text |||VOICE||| Spoken line")
        #expect(e.text == "Shown text")
        #expect(e.spoken == "Spoken line")
        #expect(!e.text.contains("|||"))
    }

    @Test("HOLO options become portals with their prompt")
    func holoSection() {
        let raw = #"Pick one |||VOICE||| Which one? |||HOLO||| {"prompt":"Choose","options":[{"label":"Alpha","value":"a"},{"label":"Beta"}]}"#
        let e = EnvelopeParser.parse(raw)
        #expect(e.text == "Pick one")
        #expect(e.spoken == "Which one?")
        #expect(e.holo?.prompt == "Choose")
        #expect(e.holo?.options.count == 2)
        #expect(e.holo?.options.first?.send == "a")
        #expect(e.holo?.options.last?.send == "Beta")
    }

    @Test("malformed HOLO degrades to clean text instead of crashing")
    func malformedHolo() {
        let e = EnvelopeParser.parse("Answer |||VOICE||| said |||HOLO||| {not json at all")
        #expect(e.text == "Answer")
        #expect(e.spoken == "said")
        #expect(e.holo == nil)
    }

    @Test("OPTIONS quick form splits on pipes, dedupes, and strips bullets")
    func optionsQuickForm() {
        let e = EnvelopeParser.parse("Text |||OPTIONS||| 1. Alpha | - Beta | alpha | Gamma")
        let labels = e.holo?.options.map(\.label)
        #expect(labels == ["Alpha", "Beta", "Gamma"])
    }

    @Test("no more than six options ever reach the UI")
    func optionCap() {
        let e = EnvelopeParser.parse("T |||OPTIONS||| a|b|c|d|e|f|g|h")
        #expect(e.holo?.options.count == EnvelopeParser.maxOptions)
    }

    @Test("an over-long label is capped rather than overflowing a portal")
    func labelCap() {
        let long = String(repeating: "x", count: 200)
        let e = EnvelopeParser.parse("T |||OPTIONS||| \(long)")
        #expect(e.holo?.options.first?.label.count == EnvelopeParser.maxLabelLength)
    }

    @Test("HOLO wins over OPTIONS when a response carries both")
    func holoWins() {
        let raw = #"T |||OPTIONS||| a|b |||HOLO||| {"options":[{"label":"real"}]}"#
        let e = EnvelopeParser.parse(raw)
        #expect(e.holo?.options.map(\.label) == ["real"])
    }

    @Test("an empty VOICE section stays nil so the mirror says nothing")
    func emptyVoice() {
        let e = EnvelopeParser.parse("Text |||VOICE|||   |||OPTIONS||| a|b")
        #expect(e.spoken == nil)
        #expect(e.holo?.options.count == 2)
    }

    @Test("an empty response is handled without throwing")
    func emptyInput() {
        let e = EnvelopeParser.parse("")
        #expect(e.text.isEmpty)
        #expect(e.spoken == nil)
        #expect(e.holo == nil)
    }
}
