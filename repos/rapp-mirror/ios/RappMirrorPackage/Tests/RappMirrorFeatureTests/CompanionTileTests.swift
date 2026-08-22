import Foundation
import Testing
@testable import RappMirrorFeature

@Suite("A tile is addressed by its own bytes")
struct CompanionTileTests {
    @Test("object key order is sorted away, array order is kept")
    func canonicalOrdering() {
        let a = TileJSON.object(["b": .int(1), "a": .array([.int(3), .int(2)])])
        let b = TileJSON.object(["a": .array([.int(3), .int(2)]), "b": .int(1)])
        #expect(Canonical.string(a) == #"{"a":[3,2],"b":1}"#)
        #expect(Canonical.string(a) == Canonical.string(b))
        #expect(Canonical.string(.array([.int(1), .int(2)])) != Canonical.string(.array([.int(2), .int(1)])))
    }

    @Test("strings escape the way every other implementation escapes them")
    func canonicalEscaping() {
        #expect(Canonical.string(.string("a\"b\\c\nd\te")) == #""a\"b\\c\nd\te""#)
        let control = String(UnicodeScalar(UInt8(1)))
        #expect(Canonical.string(.string(control)) == "\"\\u0001\"")
    }

    @Test("the same value in two spaces gets two addresses")
    func domainSeparation() {
        let value = TileJSON.object(["x": .int(1)])
        let particle = TileAddress.of(space: TileAddress.particleSpace, value)
        let wave = TileAddress.of(space: TileAddress.waveSpace, value)
        #expect(particle != wave)
        #expect(particle.count == 64)
        #expect(particle == TileAddress.of(space: TileAddress.particleSpace, value))
    }

    @Test("a frame carries both of its addresses and verifies")
    func frameAddresses() throws {
        let frame = CompanionFrame.genesis(streamId: "rappid:@t/companion:abc", payload: .object(["text": .string("hello")]))
        #expect(frame.payloadHash != frame.frameHash)
        #expect(frame.seq == 0)
        #expect(frame.prev == nil)
        #expect(frame.tileId == frame.frameHash)
        try frame.verify()
    }

    @Test("all eleven fields are present, null where not applicable")
    func elevenFields() throws {
        let frame = CompanionFrame.genesis(streamId: "s", payload: .object([:]))
        guard case .object(let map) = frame.asJSON else { Issue.record("not an object"); return }
        #expect(Set(map.keys) == ["spec", "kind", "stream_id", "seq", "utc", "payload", "payload_hash", "frame_hash", "prev", "prev_wave", "sig"])
        #expect(map["prev"] == .null)
        #expect(map["sig"] == .null)
    }

    @Test("a tile round-trips through disk bytes")
    func roundTrip() throws {
        let original = CompanionFrame.genesis(streamId: "s", payload: .object(["text": .string("held the orb"), "n": .int(3)]))
        let restored = try CompanionFrame(tileBytes: original.tileBytes)
        #expect(restored == original)
    }

    @Test("editing a payload after minting is caught, not absorbed")
    func tamperedPayload() throws {
        let frame = CompanionFrame.genesis(streamId: "s", payload: .object(["text": .string("true")]))
        let edited = String(decoding: frame.tileBytes, as: UTF8.self)
            .replacingOccurrences(of: #""text":"true""#, with: #""text":"fake""#)
        #expect(edited != String(decoding: frame.tileBytes, as: UTF8.self))
        #expect(throws: TileError.self) {
            _ = try CompanionFrame(tileBytes: Data(edited.utf8))
        }
    }

    @Test("each frame links to the previous particle")
    func chainLinks() throws {
        let a = CompanionFrame.genesis(streamId: "s")
        let b = a.next(kind: .heard, payload: .object(["text": .string("hi")]))
        let c = b.next(kind: .spoke, payload: .object(["text": .string("hello")]))
        #expect(b.prev == a.payloadHash)
        #expect(c.prev == b.payloadHash)
        #expect(c.seq == 2)
        try c.verify()
    }

    @Test("utc is a fixed 24-byte millisecond stamp")
    func utcShape() throws {
        let stamp = UTCStamp.of(Date(timeIntervalSince1970: 1_755_786_565.071))
        #expect(stamp.count == 24)
        #expect(stamp.hasSuffix("Z"))
        #expect(stamp == "2025-08-21T14:29:25.071Z")
        #expect(UTCStamp.date(stamp) != nil)
    }

    @Test("a payload that cannot be canonicalized is refused, never rounded")
    func refusesUncanonicalizable() {
        #expect(throws: TileError.self) {
            _ = try Canonical.value(from: Data(#"{"x":0.1}"#.utf8))
        }
    }

    @Test("an identity is minted from entropy, never from its name")
    func identityIsMinted() {
        let first = CompanionIdentity.mint(uuid: UUID(uuidString: "11111111-1111-1111-1111-111111111111")!)
        let second = CompanionIdentity.mint(uuid: UUID(uuidString: "22222222-2222-2222-2222-222222222222")!)
        #expect(first != second)
        #expect(first.hasPrefix("rappid:@this-phone/companion:"))
        #expect(first.split(separator: ":").last?.count == 64)
        #expect(CompanionIdentity.mint() != CompanionIdentity.mint())
    }
}
