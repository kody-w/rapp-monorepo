import Foundation
import Observation

/// How far along a companion is. Morphing is a change of stage.
public enum CompanionStage: String, Sendable, Codable, CaseIterable, Comparable {
    case egg, hatchling, fledgling, adept, apex

    /// Frames required to reach this stage.
    public var threshold: Int {
        switch self {
        case .egg: 0
        case .hatchling: 1
        case .fledgling: 5
        case .adept: 20
        case .apex: 60
        }
    }

    public var title: String {
        switch self {
        case .egg: "Egg"
        case .hatchling: "Hatchling"
        case .fledgling: "Fledgling"
        case .adept: "Adept"
        case .apex: "Apex"
        }
    }

    public static func forFrames(_ count: Int) -> CompanionStage {
        allCases.last { count >= $0.threshold } ?? .egg
    }

    public static func < (lhs: CompanionStage, rhs: CompanionStage) -> Bool {
        lhs.threshold < rhs.threshold
    }
}

/// What the tiles add up to right now.
///
/// A pure fold over the frames — same tiles in, same form out, on any device.
/// The form is never stored: storing it would create a second truth that can
/// disagree with the tiles, and then something has to decide which one is
/// right. Recompute it instead; it is cheap and it cannot drift.
public struct CompanionForm: Sendable, Equatable {
    public let stage: CompanionStage
    public let element: Element
    public let rarity: Rarity
    public let seed: UInt32
    public let art: ArtWork
    public let vigor: Int
    public let frames: Int
    public let tally: [CompanionFrameKind: Int]
    public let lastUTC: String?

    /// The one place a life becomes a face.
    public static func fold(streamId: String, frames: [CompanionFrame]) -> CompanionForm {
        let stage = CompanionStage.forFrames(frames.count)
        var tally: [CompanionFrameKind: Int] = [:]
        for frame in frames { tally[frame.kind, default: 0] += 1 }

        // Dominant affinity, ties broken by the canonical element order so two
        // phones folding the same tiles never disagree.
        let element = CardArt.elementOrder.max { left, right in
            let leftCount = tally.reduce(0) { $0 + ($1.key.affinity == left ? $1.value : 0) }
            let rightCount = tally.reduce(0) { $0 + ($1.key.affinity == right ? $1.value : 0) }
            if leftCount == rightCount {
                return CardArt.elementIndex(left) > CardArt.elementIndex(right)
            }
            return leftCount < rightCount
        } ?? .spirit

        // A companion whose recent life is nothing but failures wears it.
        // Hiding that would make the face a portrait rather than a record.
        let recent = frames.suffix(3)
        let cursed = recent.count == 3 && recent.allSatisfy { $0.kind == .stalled }
        let rarity: Rarity = cursed ? .cursed : {
            switch stage {
            case .egg: .common
            case .hatchling: .common
            case .fledgling: .uncommon
            case .adept: .rare
            case .apex: .holo
            }
        }()

        // Seeded by identity + stage + element: the art holds still while the
        // companion is what it was, and re-mints the moment it morphs.
        let seed = CardArt.fingerprint([streamId, stage.rawValue, element.rawValue, rarity.rawValue].joined(separator: "::"))
        let style = CardStyleRegistry.styleForSeed(seed, rarity: rarity)
        let art = style.render(ArtContext(next: CardArt.rng(seed: seed ^ 0x9e37_79b9), element: element, rarity: rarity, seed: seed))

        let variety = Set(frames.map(\.kind)).count
        let vigor = max(5, min(100, frames.count * 2 + variety * 8 - tally[.stalled, default: 0] * 6))

        return CompanionForm(
            stage: stage,
            element: element,
            rarity: rarity,
            seed: seed,
            art: art,
            vigor: vigor,
            frames: frames.count,
            tally: tally,
            lastUTC: frames.last?.utc
        )
    }
}

/// The name a companion keeps for life.
///
/// Minted once from entropy and remembered — never computed from the device
/// name, the owner, or anything else that can be typed. An identity derived
/// from a name is the name in hex: anyone who picks the same name gets the
/// same identity, which is the oldest way to lose an identity system.
public enum CompanionIdentity {
    static let key = "rapp.companion.streamId"

    public static var streamId: String {
        if let stored = UserDefaults.standard.string(forKey: key), stored.count > 16 { return stored }
        let minted = mint()
        UserDefaults.standard.set(minted, forKey: key)
        return minted
    }

    public static func mint(uuid: UUID = UUID()) -> String {
        var bytes = Data()
        withUnsafeBytes(of: uuid.uuid) { bytes.append(contentsOf: $0) }
        let tail = TileAddress.ofBytes(space: TileAddress.rappidSpace, bytes)
        return "rappid:@this-phone/companion:\(tail)"
    }

    public static func reset() {
        UserDefaults.standard.removeObject(forKey: key)
    }
}

/// A living companion on this phone: its tiles, and what they add up to.
///
/// Every state-changing path here appends a tile and refolds. There is no
/// setter for the form and no way to edit a frame — the only verb is `record`.
@MainActor
@Observable
public final class Companion {
    public private(set) var frames: [CompanionFrame] = []
    public private(set) var form: CompanionForm
    /// Why the last write did not reach disk, if it did not. Never swallowed:
    /// a companion that silently stops persisting looks identical to one that
    /// is fine, right up until the app is relaunched.
    public private(set) var lastError: String?
    /// The stage the companion left behind on its most recent morph.
    public private(set) var morphedFrom: CompanionStage?

    public let streamId: String
    private let store: TileStore

    public init(streamId: String = CompanionIdentity.streamId, store: TileStore = TileStore()) {
        self.streamId = streamId
        self.store = store
        self.form = CompanionForm.fold(streamId: streamId, frames: [])
    }

    /// Read the life back off disk.
    public func load() async {
        do {
            let loaded = try await store.chain(streamId)
            frames = loaded
            form = CompanionForm.fold(streamId: streamId, frames: loaded)
            lastError = nil
        } catch {
            // A broken chain is named, not hidden. The companion still shows
            // the tiles it could read, and the reason sits in the interface.
            lastError = String(describing: error)
        }
    }

    /// Add a moment. This is the only way the companion changes.
    @discardableResult
    public func record(
        _ kind: CompanionFrameKind,
        _ payload: [String: TileJSON] = [:],
        at date: Date = Date()
    ) async -> CompanionFrame {
        let frame: CompanionFrame
        if let head = frames.last {
            frame = head.next(kind: kind, payload: .object(payload), at: date)
        } else {
            frame = CompanionFrame.genesis(kind: kind, streamId: streamId, payload: .object(payload), at: date)
        }

        let before = form.stage
        frames.append(frame)
        form = CompanionForm.fold(streamId: streamId, frames: frames)
        if form.stage != before { morphedFrom = before }

        do {
            try await store.put(frame)
            lastError = nil
        } catch {
            lastError = String(describing: error)
        }
        return frame
    }

    /// Record what was said, with anything credential-shaped scrubbed and the
    /// text capped — a companion's memory should not become a place secrets go.
    @discardableResult
    public func recordUtterance(_ kind: CompanionFrameKind, text: String, extra: [String: TileJSON] = [:]) async -> CompanionFrame {
        var payload = extra
        let safe = Diagnostics.redact(text)
        payload["text"] = .string(String(safe.prefix(280)))
        payload["length"] = .int(text.count)
        return await record(kind, payload)
    }

    public func stats() async -> TileStore.Stats {
        await store.stats()
    }

    /// Newest first, for a grid that shows what just happened at the top.
    public var newestFirst: [CompanionFrame] {
        frames.sorted { $0.seq > $1.seq }
    }
}
