import CryptoKit
import Foundation

/// A tile is one frame of a companion's life, named by its own hash.
///
/// WHY A TILE AND NOT A ROW
/// A companion is not a record you overwrite; it is a life you append to.
/// Storing the whole companion as one blob means every morph rewrites the
/// past, and a past that gets rewritten cannot be checked. So each moment is
/// written once, addressed by the hash of its own bytes, and never touched
/// again. Morphing adds tiles. Nothing is ever edited in place.
///
/// The rules here are the RAPP rev-5 frame rules (`rapp/1`), kept deliberately
/// faithful so a tile written on this phone is verifiable by anything else in
/// the estate: canonical bytes, domain-separated addresses, an eleven-field
/// frame that is both a particle and a wave.

// MARK: - The value a tile can hold

/// The closed set of JSON values a payload may contain.
///
/// Closed on purpose. Canonicalization has to be total — every value must have
/// exactly one byte form — and floating point is where that promise dies
/// (`0.1 + 0.2`, `1e21`, `-0.0` all serialize differently across runtimes).
/// A payload that cannot be canonicalized cannot be addressed, so the type
/// system refuses it rather than the hash silently disagreeing later.
public enum TileJSON: Sendable, Equatable {
    case null
    case bool(Bool)
    case int(Int)
    case string(String)
    case array([TileJSON])
    case object([String: TileJSON])
}

public extension TileJSON {
    /// Convenience for the common payload shape.
    static func text(_ value: String) -> TileJSON { .string(value) }

    var stringValue: String? {
        if case .string(let value) = self { return value }
        return nil
    }

    var intValue: Int? {
        if case .int(let value) = self { return value }
        return nil
    }

    subscript(key: String) -> TileJSON? {
        if case .object(let map) = self { return map[key] }
        return nil
    }
}

// MARK: - Canonicalization

/// One value, one sequence of bytes (RFC 8785, over the subset above).
///
/// Sort object keys. No whitespace. Keep array order. Escape the way
/// JSON.stringify does. Two programs that disagree about which bytes represent
/// a value hash it differently, and every promise above this line breaks
/// silently — this is the one place that cannot be casual.
public enum Canonical {
    public static func bytes(_ value: TileJSON) -> Data { Data(string(value).utf8) }

    public static func string(_ value: TileJSON) -> String {
        switch value {
        case .null:
            return "null"
        case .bool(let flag):
            return flag ? "true" : "false"
        case .int(let number):
            return String(number)
        case .string(let text):
            return "\"\(escape(text))\""
        case .array(let items):
            // Array position is meaning; it is preserved exactly.
            return "[" + items.map(string).joined(separator: ",") + "]"
        case .object(let map):
            // Key order is not meaning; it is sorted away.
            let body = map.keys.sorted().map { key in
                "\"\(escape(key))\":\(string(map[key] ?? .null))"
            }
            return "{" + body.joined(separator: ",") + "}"
        }
    }

    static func escape(_ raw: String) -> String {
        var out = ""
        out.reserveCapacity(raw.count + 8)
        for character in raw.unicodeScalars {
            switch character {
            case "\"": out += "\\\""
            case "\\": out += "\\\\"
            case "\u{08}": out += "\\b"
            case "\u{0C}": out += "\\f"
            case "\n": out += "\\n"
            case "\r": out += "\\r"
            case "\t": out += "\\t"
            default:
                if character.value < 0x20 {
                    out += String(format: "\\u%04x", character.value)
                } else {
                    out.unicodeScalars.append(character)
                }
            }
        }
        return out
    }

    /// Read canonical (or any) JSON back into a `TileJSON`.
    ///
    /// Refuses non-integral numbers rather than rounding them: a value we
    /// cannot re-serialize byte-for-byte is a value whose address we cannot
    /// reproduce, and a tile that will not re-address is not a tile.
    public static func value(from data: Data) throws -> TileJSON {
        let object = try JSONSerialization.jsonObject(with: data, options: [.fragmentsAllowed])
        guard let value = convert(object) else {
            throw TileError.malformed("payload holds a value that cannot be canonicalized")
        }
        return value
    }

    private static func convert(_ object: Any) -> TileJSON? {
        switch object {
        case is NSNull:
            return .null
        case let number as NSNumber:
            if CFGetTypeID(number) == CFBooleanGetTypeID() { return .bool(number.boolValue) }
            guard number.doubleValue == number.doubleValue.rounded(),
                  let exact = Int(exactly: number.doubleValue) else { return nil }
            return .int(exact)
        case let text as String:
            return .string(text)
        case let items as [Any]:
            var mapped: [TileJSON] = []
            mapped.reserveCapacity(items.count)
            for item in items {
                guard let value = convert(item) else { return nil }
                mapped.append(value)
            }
            return .array(mapped)
        case let map as [String: Any]:
            var mapped: [String: TileJSON] = [:]
            for (key, item) in map {
                guard let value = convert(item) else { return nil }
                mapped[key] = value
            }
            return .object(mapped)
        default:
            return nil
        }
    }
}

// MARK: - Addressing

/// `H(space, v) = SHA256(space ‖ 0x0A ‖ canonical(v))`
///
/// The space tag is part of what gets hashed, so a payload address can never
/// equal a frame address can never equal an identity — even when the bytes
/// underneath are identical. Cross-space collision is not unlikely here; it is
/// unrepresentable.
public enum TileAddress {
    public static let particleSpace = "rapp/1:particle"
    public static let waveSpace = "rapp/1:wave"
    public static let rappidSpace = "rapp/1:rappid"

    public static func of(space: String, _ value: TileJSON) -> String {
        var hasher = SHA256()
        hasher.update(data: Data(space.utf8))
        hasher.update(data: Data([0x0A]))
        hasher.update(data: Canonical.bytes(value))
        return hex(hasher.finalize())
    }

    public static func ofBytes(space: String, _ payload: Data) -> String {
        var hasher = SHA256()
        hasher.update(data: Data(space.utf8))
        hasher.update(data: Data([0x0A]))
        hasher.update(data: payload)
        return hex(hasher.finalize())
    }

    static func hex(_ digest: SHA256Digest) -> String {
        digest.map { String(format: "%02x", $0) }.joined()
    }
}

// MARK: - Errors

public enum TileError: Error, Equatable, CustomStringConvertible {
    case malformed(String)
    case addressMismatch(expected: String, recomputed: String)
    case particleMismatch(expected: String, recomputed: String)
    case brokenLink(seq: Int, expectedPrev: String?, found: String?)

    public var description: String {
        switch self {
        case .malformed(let why):
            "this tile is not a frame: \(why)"
        case .addressMismatch(let expected, let recomputed):
            "tile \(expected.prefix(12))… does not hash to its own name (got \(recomputed.prefix(12))…)"
        case .particleMismatch(let expected, let recomputed):
            "payload was edited after minting (payload_hash \(expected.prefix(12))… vs \(recomputed.prefix(12))…)"
        case .brokenLink(let seq, let expectedPrev, let found):
            "chain breaks at seq \(seq): expected prev \(expectedPrev?.prefix(12).description ?? "null"), found \(found?.prefix(12).description ?? "null")"
        }
    }
}

// MARK: - Frame kinds

/// What a companion frame records.
///
/// Additive only, and never renamed: a kind is load-bearing in tiles already
/// written to disk. Adding a case is a molt; renaming one is a transplant that
/// orphans every tile that used the old name.
public enum CompanionFrameKind: String, Sendable, Codable, CaseIterable {
    case woke = "companion.woke"
    case heard = "companion.heard"
    case spoke = "companion.spoke"
    case met = "companion.met"
    case forged = "companion.forged"
    /// The brainstem did not answer. Recorded, because a life with the
    /// failures deleted is a portrait, not a record.
    case stalled = "companion.stalled"

    public var glyph: String {
        switch self {
        case .woke: "sunrise.fill"
        case .heard: "waveform"
        case .spoke: "bubble.left.fill"
        case .met: "rectangle.stack.fill"
        case .forged: "hammer.fill"
        case .stalled: "exclamationmark.triangle.fill"
        }
    }

    public var label: String {
        switch self {
        case .woke: "woke"
        case .heard: "heard"
        case .spoke: "spoke"
        case .met: "met"
        case .forged: "forged"
        case .stalled: "stalled"
        }
    }

    /// Which way this kind pulls the companion's form as it accumulates.
    public var affinity: Element {
        switch self {
        case .woke: .spirit
        case .heard: .aether
        case .spoke: .aether
        case .met: .stone
        case .forged: .ember
        case .stalled: .void
        }
    }
}

// MARK: - The frame

/// One moment in a companion's life: eleven fields, always all eleven.
///
/// `payload_hash` is the **particle** — the address of what happened, and the
/// link the next frame points back to. `frame_hash` is the **wave** — the
/// address of this exact record, envelope and all, which is also this tile's
/// filename. One object, two addresses, and you never choose when you emit.
public struct CompanionFrame: Sendable, Equatable, Identifiable {
    public static let spec = "rapp/1"

    public let kind: CompanionFrameKind
    public let streamId: String
    public let seq: Int
    public let utc: String
    public let payload: TileJSON
    public let payloadHash: String
    public let frameHash: String
    public let prev: String?
    public let prevWave: String?
    public let sig: String?

    /// The tile's name is its wave: these exact bytes.
    public var id: String { frameHash }
    public var tileId: String { frameHash }

    public init(
        kind: CompanionFrameKind,
        streamId: String,
        seq: Int,
        utc: String,
        payload: TileJSON,
        prev: String? = nil,
        prevWave: String? = nil,
        sig: String? = nil
    ) {
        self.kind = kind
        self.streamId = streamId
        self.seq = seq
        self.utc = utc
        self.payload = payload
        self.prev = prev
        self.prevWave = prevWave
        self.sig = sig
        let particle = TileAddress.of(space: TileAddress.particleSpace, payload)
        self.payloadHash = particle
        self.frameHash = TileAddress.of(
            space: TileAddress.waveSpace,
            Self.envelope(
                kind: kind, streamId: streamId, seq: seq, utc: utc,
                payload: payload, payloadHash: particle, prev: prev, prevWave: prevWave
            )
        )
    }

    /// Rebuild a frame from fields that already carry their hashes (disk read).
    private init(
        kind: CompanionFrameKind, streamId: String, seq: Int, utc: String, payload: TileJSON,
        payloadHash: String, frameHash: String, prev: String?, prevWave: String?, sig: String?
    ) {
        self.kind = kind
        self.streamId = streamId
        self.seq = seq
        self.utc = utc
        self.payload = payload
        self.payloadHash = payloadHash
        self.frameHash = frameHash
        self.prev = prev
        self.prevWave = prevWave
        self.sig = sig
    }

    /// The wave pre-image: every field except the wave itself and the signature.
    static func envelope(
        kind: CompanionFrameKind, streamId: String, seq: Int, utc: String,
        payload: TileJSON, payloadHash: String, prev: String?, prevWave: String?
    ) -> TileJSON {
        .object([
            "spec": .string(spec),
            "kind": .string(kind.rawValue),
            "stream_id": .string(streamId),
            "seq": .int(seq),
            "utc": .string(utc),
            "payload": payload,
            "payload_hash": .string(payloadHash),
            "prev": prev.map(TileJSON.string) ?? .null,
            "prev_wave": prevWave.map(TileJSON.string) ?? .null,
        ])
    }

    /// The whole frame, all eleven fields present — `null` where not applicable,
    /// never omitted, because a missing key and a null key hash differently.
    public var asJSON: TileJSON {
        guard case .object(var map) = Self.envelope(
            kind: kind, streamId: streamId, seq: seq, utc: utc,
            payload: payload, payloadHash: payloadHash, prev: prev, prevWave: prevWave
        ) else { return .null }
        map["frame_hash"] = .string(frameHash)
        map["sig"] = sig.map(TileJSON.string) ?? .null
        return .object(map)
    }

    /// The bytes this tile is stored as.
    public var tileBytes: Data { Canonical.bytes(asJSON) }

    /// Recompute both addresses. A frame that verifies, verifies forever.
    public func verify() throws {
        let particle = TileAddress.of(space: TileAddress.particleSpace, payload)
        guard particle == payloadHash else {
            throw TileError.particleMismatch(expected: payloadHash, recomputed: particle)
        }
        let wave = TileAddress.of(
            space: TileAddress.waveSpace,
            Self.envelope(
                kind: kind, streamId: streamId, seq: seq, utc: utc,
                payload: payload, payloadHash: payloadHash, prev: prev, prevWave: prevWave
            )
        )
        guard wave == frameHash else {
            throw TileError.addressMismatch(expected: frameHash, recomputed: wave)
        }
    }

    /// Decode a tile from disk and verify it before anyone can act on it.
    public init(tileBytes data: Data) throws {
        let value = try Canonical.value(from: data)
        guard case .object(let map) = value else {
            throw TileError.malformed("a frame is a JSON object")
        }
        guard map["spec"]?.stringValue == Self.spec else {
            throw TileError.malformed("spec is not \(Self.spec)")
        }
        guard
            let rawKind = map["kind"]?.stringValue,
            let kind = CompanionFrameKind(rawValue: rawKind)
        else {
            throw TileError.malformed("unknown kind \(map["kind"]?.stringValue ?? "(missing)")")
        }
        guard
            let streamId = map["stream_id"]?.stringValue,
            let seq = map["seq"]?.intValue,
            let utc = map["utc"]?.stringValue,
            let payload = map["payload"],
            let payloadHash = map["payload_hash"]?.stringValue,
            let frameHash = map["frame_hash"]?.stringValue
        else {
            throw TileError.malformed("a frame is missing one of its eleven fields")
        }
        self.init(
            kind: kind, streamId: streamId, seq: seq, utc: utc, payload: payload,
            payloadHash: payloadHash, frameHash: frameHash,
            prev: map["prev"]?.stringValue, prevWave: map["prev_wave"]?.stringValue,
            sig: map["sig"]?.stringValue
        )
        try verify()
    }

    /// The next frame in this life, chained to this one.
    public func next(kind: CompanionFrameKind, payload: TileJSON, at date: Date = Date()) -> CompanionFrame {
        CompanionFrame(
            kind: kind,
            streamId: streamId,
            seq: seq + 1,
            utc: UTCStamp.of(date),
            payload: payload,
            prev: payloadHash
        )
    }

    /// The first frame of a life.
    public static func genesis(
        kind: CompanionFrameKind = .woke,
        streamId: String,
        payload: TileJSON = .object([:]),
        at date: Date = Date()
    ) -> CompanionFrame {
        CompanionFrame(kind: kind, streamId: streamId, seq: 0, utc: UTCStamp.of(date), payload: payload)
    }
}

/// `2026-08-21T14:29:25.071Z` — fixed width, milliseconds, always Z.
public enum UTCStamp {
    public static func of(_ date: Date = Date()) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
        return formatter.string(from: date)
    }

    public static func date(_ stamp: String) -> Date? {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"
        return formatter.date(from: stamp)
    }
}
