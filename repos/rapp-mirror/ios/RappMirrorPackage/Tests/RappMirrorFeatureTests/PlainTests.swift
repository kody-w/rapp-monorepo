import Testing
@testable import RappMirrorFeature

@Suite("Markdown never reaches the voice or the caption")
struct PlainTests {
    @Test("headings lose their hashes")
    func headings() {
        #expect(Plain.text("### Core Skills") == "Core Skills")
        #expect(Plain.text("# Title\n## Sub") == "Title\nSub")
    }

    @Test("bold and italic keep their words")
    func emphasis() {
        #expect(Plain.text("I'm the **RAPP Brainstem** here") == "I'm the RAPP Brainstem here")
        #expect(Plain.text("this is *important*") == "this is important")
        #expect(Plain.text("__very__ bold") == "very bold")
        #expect(Plain.text("***both***") == "both")
    }

    @Test("links are spoken as their text, never as a URL")
    func links() {
        #expect(Plain.text("see [the docs](https://example.com/x)") == "see the docs")
        #expect(!Plain.text("[a](http://b.example)").contains("http"))
    }

    @Test("code fences and inline code are not read out")
    func code() {
        #expect(Plain.text("run `npm test` now") == "run npm test now")
        #expect(Plain.text("before\n```\nrm -rf /\n```\nafter").contains("before"))
        #expect(!Plain.text("```\nsecret code\n```").contains("```"))
    }

    @Test("list markers are dropped but the items survive")
    func lists() {
        #expect(Plain.text("- one\n- two") == "one\ntwo")
        #expect(Plain.text("1. first\n2. second") == "first\nsecond")
    }

    @Test("a real brainstem answer comes out clean")
    func realAnswer() {
        let raw = """
        I'm the **RAPP Brainstem** — your local AI assistant. Here's what I can do:

        ### Core Skills
        - **Memory**: I remember things
        - **Agents**: I run `*_agent.py` files
        """
        let plain = Plain.text(raw)
        for marker in ["**", "###", "- ", "`"] {
            #expect(!plain.contains(marker), "\(marker) survived")
        }
        #expect(plain.contains("RAPP Brainstem"))
        #expect(plain.contains("Memory"))
    }

    @Test("spoken text flattens newlines into sentences")
    func spokenFlattens() {
        let said = Plain.spoken("Line one\nLine two")
        #expect(!said.contains("\n"))
        #expect(said.contains("Line one"))
        #expect(said.contains("Line two"))
    }

    @Test("spoken text does not double up punctuation")
    func spokenPunctuation() {
        #expect(!Plain.spoken("Done.\nNext").contains(".."))
    }

    @Test("a long answer is cut at a sentence, not mid-word")
    func spokenLimit() {
        let long = String(repeating: "This is a sentence. ", count: 80)
        let said = Plain.spoken(long, limit: 100)
        #expect(said.count <= 100)
        #expect(said.hasSuffix(".") || said.hasSuffix("…"))
    }

    @Test("plain text is left exactly as it is")
    func passthrough() {
        #expect(Plain.text("Just a sentence.") == "Just a sentence.")
    }

    @Test("an empty answer stays empty rather than throwing")
    func empty() {
        #expect(Plain.text("") == "")
        #expect(Plain.spoken("") == "")
    }
}
