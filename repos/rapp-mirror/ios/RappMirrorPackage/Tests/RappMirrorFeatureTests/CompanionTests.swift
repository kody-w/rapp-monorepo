import Foundation
import Testing
@testable import RappMirrorFeature

@Suite("A companion is the fold of its tiles")
struct CompanionTests {
    private func scratch() -> URL {
        let url = URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent("companion-tests-\(UUID().uuidString)", isDirectory: true)
        try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }

    private func life(_ kinds: [CompanionFrameKind], streamId: String = "s") -> [CompanionFrame] {
        var frames: [CompanionFrame] = []
        for kind in kinds {
            if let head = frames.last {
                frames.append(head.next(kind: kind, payload: .object([:])))
            } else {
                frames.append(CompanionFrame.genesis(kind: kind, streamId: streamId))
            }
        }
        return frames
    }

    @Test("an empty life is an egg")
    func emptyIsEgg() {
        let form = CompanionForm.fold(streamId: "s", frames: [])
        #expect(form.stage == .egg)
        #expect(form.frames == 0)
        #expect(form.lastUTC == nil)
    }

    @Test("stages come at their thresholds and never go backwards", arguments: [
        (1, CompanionStage.hatchling), (4, .hatchling), (5, .fledgling),
        (19, .fledgling), (20, .adept), (59, .adept), (60, .apex), (200, .apex),
    ])
    func stageThresholds(count: Int, expected: CompanionStage) {
        let form = CompanionForm.fold(streamId: "s", frames: life(Array(repeating: .heard, count: count)))
        #expect(form.stage == expected)
    }

    @Test("the dominant kind decides the element")
    func dominantElement() {
        let forged = CompanionForm.fold(streamId: "s", frames: life([.forged, .forged, .forged, .heard]))
        #expect(forged.element == .ember)
        let met = CompanionForm.fold(streamId: "s", frames: life([.met, .met, .met, .woke]))
        #expect(met.element == .stone)
    }

    @Test("the same tiles fold to the same form on any device")
    func foldIsDeterministic() {
        let frames = life([.woke, .heard, .spoke, .met])
        let first = CompanionForm.fold(streamId: "s", frames: frames)
        let second = CompanionForm.fold(streamId: "s", frames: frames)
        #expect(first == second)
        #expect(first.seed == second.seed)
    }

    @Test("the face holds still within a stage and re-mints when it morphs")
    func artMorphsOnlyOnMorph() {
        let two = CompanionForm.fold(streamId: "s", frames: life(Array(repeating: .heard, count: 2)))
        let three = CompanionForm.fold(streamId: "s", frames: life(Array(repeating: .heard, count: 3)))
        let six = CompanionForm.fold(streamId: "s", frames: life(Array(repeating: .heard, count: 6)))
        #expect(two.seed == three.seed)
        #expect(two.art == three.art)
        #expect(six.stage != two.stage)
        #expect(six.seed != two.seed)
    }

    @Test("two companions with different identities never wear the same face")
    func identityChangesTheFace() {
        let mine = CompanionForm.fold(streamId: "rappid:@a/companion:1", frames: life([.heard, .heard]))
        let yours = CompanionForm.fold(streamId: "rappid:@b/companion:2", frames: life([.heard, .heard]))
        #expect(mine.seed != yours.seed)
        #expect(mine.stage == yours.stage)
    }

    @Test("a run of nothing but stalls is worn, not hidden")
    func stallsShow() {
        let cursed = CompanionForm.fold(streamId: "s", frames: life([.heard, .stalled, .stalled, .stalled]))
        #expect(cursed.rarity == .cursed)
        #expect(cursed.element == .void)
        let recovered = CompanionForm.fold(streamId: "s", frames: life([.stalled, .stalled, .stalled, .spoke]))
        #expect(recovered.rarity != .cursed)
    }

    @MainActor
    @Test("recording appends a tile, refolds, and survives a relaunch")
    func recordPersists() async throws {
        let root = scratch()
        let companion = Companion(streamId: "rappid:@t/companion:aa", store: TileStore(root: root))
        await companion.record(.woke)
        await companion.recordUtterance(.heard, text: "where to?")
        #expect(companion.frames.count == 2)
        #expect(companion.form.stage == .hatchling)
        #expect(companion.lastError == nil)

        // A second companion over the same store is the same companion.
        let relaunched = Companion(streamId: "rappid:@t/companion:aa", store: TileStore(root: root))
        await relaunched.load()
        #expect(relaunched.frames.count == 2)
        #expect(relaunched.form == companion.form)
        #expect(relaunched.frames.last?.payload["text"]?.stringValue == "where to?")
    }

    @MainActor
    @Test("a morph is announced with the stage it left")
    func morphIsAnnounced() async throws {
        let companion = Companion(streamId: "s", store: TileStore(root: scratch()))
        #expect(companion.morphedFrom == nil)
        await companion.record(.woke)
        #expect(companion.morphedFrom == .egg)
        #expect(companion.form.stage == .hatchling)
        for _ in 0..<4 { await companion.record(.heard) }
        #expect(companion.morphedFrom == .hatchling)
        #expect(companion.form.stage == .fledgling)
    }

    @MainActor
    @Test("what a companion remembers is scrubbed and capped")
    func utterancesAreScrubbed() async throws {
        let companion = Companion(streamId: "s", store: TileStore(root: scratch()))
        let frame = await companion.recordUtterance(.heard, text: "my api_key: hunter2 and a very long tail " + String(repeating: "x", count: 400))
        let stored = frame.payload["text"]?.stringValue ?? ""
        #expect(!stored.contains("hunter2"))
        #expect(stored.count <= 280)
        #expect(frame.payload["length"]?.intValue ?? 0 > 280)
    }

    @MainActor
    @Test("newest tiles come first for the grid")
    func newestFirst() async throws {
        let companion = Companion(streamId: "s", store: TileStore(root: scratch()))
        await companion.record(.woke)
        await companion.record(.heard)
        await companion.record(.spoke)
        #expect(companion.newestFirst.map(\.seq) == [2, 1, 0])
    }
}
