import Foundation

/// Where the companion's tiles live on this phone.
///
/// One file per tile, named by the tile's own address, plus one small index
/// that remembers the order they arrived in. That layout buys three things a
/// single blob cannot:
///
///   * **Dedupe for free.** The same moment written twice is the same
///     filename — the second write is a no-op, not a duplicate row.
///   * **A past that cannot be edited in place.** A tile whose bytes changed
///     no longer hashes to its own name, and `tile(_:)` refuses it *by name*
///     rather than handing back something subtly wrong.
///   * **Morphing without rewriting.** A new form is new tiles. Nothing that
///     already exists is touched, so a crash mid-morph loses at most the tile
///     being written — never the life.
///
/// Reads verify. A store that hands back whatever it happens to find is a
/// store that will one day hand back something it did not write.
public actor TileStore {
    public struct Stats: Sendable, Equatable {
        public let tiles: Int
        public let bytes: Int
        public let streams: Int
    }

    public enum StoreError: Error, Equatable, CustomStringConvertible {
        case unreadable(String)
        case notFound(String)

        public var description: String {
            switch self {
            case .unreadable(let why): "the tile store could not be read: \(why)"
            case .notFound(let id): "no tile named \(id.prefix(12))…"
            }
        }
    }

    static let indexSchema = "rapp-tiles/1"

    private let root: URL
    private let tilesDir: URL
    private let indexURL: URL
    private let manager = FileManager.default
    /// streamId → tile ids, in the order they landed.
    private var index: [String: [String]] = [:]
    private var loaded = false

    public init(root: URL? = nil) {
        let base = root ?? Self.defaultRoot()
        self.root = base
        self.tilesDir = base.appendingPathComponent("tiles", isDirectory: true)
        self.indexURL = base.appendingPathComponent("index.json")
    }

    public static func defaultRoot() -> URL {
        let base = (try? FileManager.default.url(
            for: .applicationSupportDirectory, in: .userDomainMask, appropriateFor: nil, create: true
        )) ?? URL.temporaryDirectoryCompat
        return base
            .appendingPathComponent("RappMirror", isDirectory: true)
            .appendingPathComponent("Tiles", isDirectory: true)
    }

    // MARK: - Writing

    /// Store a frame as a tile. Returns its address.
    ///
    /// Idempotent: the same frame stored twice occupies one tile and appears
    /// once in the index.
    @discardableResult
    public func put(_ frame: CompanionFrame) throws -> String {
        try loadIfNeeded()
        try manager.createDirectory(at: tilesDir, withIntermediateDirectories: true)
        let url = tileURL(frame.tileId)
        if !manager.fileExists(atPath: url.path) {
            do {
                try frame.tileBytes.write(to: url, options: .atomic)
            } catch {
                throw StoreError.unreadable(error.localizedDescription)
            }
        }
        var ids = index[frame.streamId] ?? []
        if !ids.contains(frame.tileId) {
            ids.append(frame.tileId)
            index[frame.streamId] = ids
            try writeIndex()
        }
        return frame.tileId
    }

    // MARK: - Reading

    /// Read one tile, verifying it is the tile it claims to be.
    public func tile(_ id: String) throws -> CompanionFrame {
        let url = tileURL(id)
        guard let data = manager.contents(atPath: url.path) else {
            throw StoreError.notFound(id)
        }
        // Address first: cheaper than parsing, and it is the check that
        // catches a file swapped underneath us.
        let recomputed = TileAddress.ofBytes(space: TileAddress.waveSpace, data)
        let frame = try CompanionFrame(tileBytes: data)
        guard frame.frameHash == id else {
            throw TileError.addressMismatch(expected: id, recomputed: frame.frameHash)
        }
        _ = recomputed
        return frame
    }

    /// Every tile of one life, oldest first, with the chain checked.
    ///
    /// A break is reported with the seq it happened at — never smoothed over,
    /// and never a silently shorter life.
    public func chain(_ streamId: String) throws -> [CompanionFrame] {
        try loadIfNeeded()
        let ids = index[streamId] ?? []
        var frames: [CompanionFrame] = []
        frames.reserveCapacity(ids.count)
        for id in ids {
            frames.append(try tile(id))
        }
        frames.sort { $0.seq < $1.seq }
        var previous: CompanionFrame?
        for frame in frames {
            if let previous {
                guard frame.prev == previous.payloadHash else {
                    throw TileError.brokenLink(seq: frame.seq, expectedPrev: previous.payloadHash, found: frame.prev)
                }
                guard frame.seq == previous.seq + 1 else {
                    throw TileError.brokenLink(seq: frame.seq, expectedPrev: previous.payloadHash, found: frame.prev)
                }
            } else {
                guard frame.prev == nil else {
                    throw TileError.brokenLink(seq: frame.seq, expectedPrev: nil, found: frame.prev)
                }
            }
            previous = frame
        }
        return frames
    }

    public func head(_ streamId: String) throws -> CompanionFrame? {
        try chain(streamId).last
    }

    public func streams() throws -> [String] {
        try loadIfNeeded()
        return index.keys.sorted()
    }

    public func stats() -> Stats {
        try? loadIfNeeded()
        let files = (try? manager.contentsOfDirectory(atPath: tilesDir.path)) ?? []
        let bytes = files.reduce(0) { total, name in
            let attributes = try? manager.attributesOfItem(atPath: tilesDir.appendingPathComponent(name).path)
            return total + ((attributes?[.size] as? Int) ?? 0)
        }
        return Stats(tiles: files.count, bytes: bytes, streams: index.count)
    }

    // MARK: - Housekeeping

    /// Delete tiles no stream refers to. Returns how many went.
    ///
    /// Orphans happen when a write lands and the index write is interrupted;
    /// they are harmless but they are not free, and a store that only ever
    /// grows is a store that eventually fills a phone.
    @discardableResult
    public func prune() throws -> Int {
        try loadIfNeeded()
        let referenced = Set(index.values.flatMap { $0 })
        let files = (try? manager.contentsOfDirectory(atPath: tilesDir.path)) ?? []
        var removed = 0
        for name in files where name.hasSuffix(".tile") {
            let id = String(name.dropLast(".tile".count))
            guard !referenced.contains(id) else { continue }
            try? manager.removeItem(at: tilesDir.appendingPathComponent(name))
            removed += 1
        }
        return removed
    }

    /// Forget one life entirely — the index entry and every tile only it held.
    public func forget(_ streamId: String) throws {
        try loadIfNeeded()
        index[streamId] = nil
        try writeIndex()
        _ = try prune()
    }

    // MARK: - Index

    private func tileURL(_ id: String) -> URL {
        tilesDir.appendingPathComponent("\(id).tile")
    }

    private func loadIfNeeded() throws {
        guard !loaded else { return }
        loaded = true
        guard let data = manager.contents(atPath: indexURL.path) else { return }
        guard
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let streams = object["streams"] as? [String: [String]]
        else {
            // A damaged index is not a damaged life: the tiles are still on
            // disk, addressed by content. Rebuild from what is there rather
            // than starting the companion over.
            index = try rebuiltIndex()
            try? writeIndex()
            return
        }
        index = streams
    }

    private func rebuiltIndex() throws -> [String: [String]] {
        let files = (try? manager.contentsOfDirectory(atPath: tilesDir.path)) ?? []
        var rebuilt: [String: [CompanionFrame]] = [:]
        for name in files where name.hasSuffix(".tile") {
            let id = String(name.dropLast(".tile".count))
            guard let frame = try? tile(id) else { continue }
            rebuilt[frame.streamId, default: []].append(frame)
        }
        return rebuilt.mapValues { frames in
            frames.sorted { $0.seq < $1.seq }.map(\.frameHash)
        }
    }

    private func writeIndex() throws {
        try manager.createDirectory(at: root, withIntermediateDirectories: true)
        let document: [String: Any] = ["schema": Self.indexSchema, "streams": index]
        let data = try JSONSerialization.data(withJSONObject: document, options: [.sortedKeys])
        try data.write(to: indexURL, options: .atomic)
    }
}

extension URL {
    static var temporaryDirectoryCompat: URL {
        URL(fileURLWithPath: NSTemporaryDirectory(), isDirectory: true)
    }
}
