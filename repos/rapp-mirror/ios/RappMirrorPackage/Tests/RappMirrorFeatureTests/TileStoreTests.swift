import Foundation
import Testing
@testable import RappMirrorFeature

@Suite("The tile store keeps a past that cannot be edited in place")
struct TileStoreTests {
    private func scratch() -> URL {
        let url = URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent("tile-store-tests-\(UUID().uuidString)", isDirectory: true)
        try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }

    @Test("a frame stored twice occupies one tile and appears once")
    func dedupe() async throws {
        let store = TileStore(root: scratch())
        let frame = CompanionFrame.genesis(streamId: "s", payload: .object(["text": .string("once")]))
        let first = try await store.put(frame)
        let second = try await store.put(frame)
        #expect(first == second)
        let stats = await store.stats()
        #expect(stats.tiles == 1)
        #expect(try await store.chain("s").count == 1)
    }

    @Test("a life reads back oldest first, with every tile verified")
    func chainReadsBack() async throws {
        let store = TileStore(root: scratch())
        let a = CompanionFrame.genesis(streamId: "s")
        let b = a.next(kind: .heard, payload: .object(["text": .string("hi")]))
        let c = b.next(kind: .spoke, payload: .object(["text": .string("hello")]))
        for frame in [a, b, c] { _ = try await store.put(frame) }
        let chain = try await store.chain("s")
        #expect(chain.map(\.seq) == [0, 1, 2])
        #expect(chain.map(\.kind) == [.woke, .heard, .spoke])
        #expect(try await store.head("s")?.frameHash == c.frameHash)
    }

    @Test("a tile whose bytes were swapped no longer answers to its name")
    func swappedBytesRefused() async throws {
        let root = scratch()
        let store = TileStore(root: root)
        let real = CompanionFrame.genesis(streamId: "s", payload: .object(["text": .string("real")]))
        let impostor = CompanionFrame.genesis(streamId: "s", payload: .object(["text": .string("impostor")]))
        let id = try await store.put(real)

        // Overwrite the file with another perfectly valid frame: every hash
        // inside it checks out, and it is still not the tile that was asked for.
        let path = root.appendingPathComponent("tiles").appendingPathComponent("\(id).tile")
        try impostor.tileBytes.write(to: path)

        await #expect(throws: TileError.self) {
            _ = try await store.tile(id)
        }
    }

    @Test("a tile filled with garbage is named as malformed, not returned")
    func garbageRefused() async throws {
        let root = scratch()
        let store = TileStore(root: root)
        let frame = CompanionFrame.genesis(streamId: "s")
        let id = try await store.put(frame)
        let path = root.appendingPathComponent("tiles").appendingPathComponent("\(id).tile")
        try Data("not a frame at all".utf8).write(to: path)
        await #expect(throws: Error.self) {
            _ = try await store.tile(id)
        }
    }

    @Test("a spliced history is refused at the seq where it breaks")
    func splicedHistoryRefused() async throws {
        let store = TileStore(root: scratch())
        let a = CompanionFrame.genesis(streamId: "s")
        // Self-consistent frame, correct seq, wrong ancestor: the frame verifies
        // and the chain still must not.
        let spliced = CompanionFrame(
            kind: .spoke, streamId: "s", seq: 1, utc: UTCStamp.of(),
            payload: .object(["text": .string("inserted")]),
            prev: String(repeating: "de", count: 32)
        )
        try spliced.verify()
        _ = try await store.put(a)
        _ = try await store.put(spliced)
        await #expect(throws: TileError.self) {
            _ = try await store.chain("s")
        }
    }

    @Test("orphan tiles are pruned, referenced tiles are not")
    func prunesOrphans() async throws {
        let root = scratch()
        let store = TileStore(root: root)
        let kept = CompanionFrame.genesis(streamId: "s")
        _ = try await store.put(kept)
        let orphan = CompanionFrame.genesis(streamId: "other", payload: .object(["text": .string("orphan")]))
        let tiles = root.appendingPathComponent("tiles")
        try orphan.tileBytes.write(to: tiles.appendingPathComponent("\(orphan.frameHash).tile"))

        let removed = try await store.prune()
        #expect(removed == 1)
        #expect(try await store.chain("s").count == 1)
        let stats = await store.stats()
        #expect(stats.tiles == 1)
    }

    @Test("a damaged index rebuilds from the tiles rather than losing the life")
    func rebuildsDamagedIndex() async throws {
        let root = scratch()
        let first = TileStore(root: root)
        let a = CompanionFrame.genesis(streamId: "s")
        let b = a.next(kind: .spoke, payload: .object(["text": .string("still here")]))
        _ = try await first.put(a)
        _ = try await first.put(b)

        try Data("{ this index is ruined".utf8).write(to: root.appendingPathComponent("index.json"))

        let reopened = TileStore(root: root)
        let chain = try await reopened.chain("s")
        #expect(chain.count == 2)
        #expect(chain.last?.payload["text"]?.stringValue == "still here")
    }

    @Test("forgetting a life takes its tiles with it")
    func forget() async throws {
        let store = TileStore(root: scratch())
        let a = CompanionFrame.genesis(streamId: "s")
        _ = try await store.put(a)
        try await store.forget("s")
        #expect(try await store.chain("s").isEmpty)
        let stats = await store.stats()
        #expect(stats.tiles == 0)
    }
}
