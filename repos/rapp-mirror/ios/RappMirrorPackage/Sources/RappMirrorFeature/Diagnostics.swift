import Foundation

/// The evidence ledger — the iOS mirror's answer to "did that actually happen?".
///
/// Same rule as the desktop mirror: zero telemetry, nothing leaves the device.
/// Events are kept in a bounded in-memory ring and appended to a redacted JSONL
/// file in Application Support, so a failure is still answerable afterwards.
public actor Diagnostics {
    public static let shared = Diagnostics()

    public enum Level: String, Sendable, Codable {
        case info, warn, error
    }

    public struct Event: Sendable, Codable, Equatable {
        public let seq: Int
        public let at: Date
        public let component: String
        public let level: Level
        public let message: String
    }

    private static let ringMax = 500
    private static let fileMaxBytes = 512_000

    private var seq = 0
    private var ring: [Event] = []
    private var writesDisabled = false
    private let fileURL: URL?

    init(fileURL: URL? = Diagnostics.defaultFileURL()) {
        self.fileURL = fileURL
    }

    static func defaultFileURL() -> URL? {
        guard
            let base = try? FileManager.default.url(
                for: .applicationSupportDirectory,
                in: .userDomainMask,
                appropriateFor: nil,
                create: true
            )
        else { return nil }
        let dir = base.appendingPathComponent("RappMirror", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        return dir.appendingPathComponent("mirror.jsonl")
    }

    /// Anything that looks like a credential is scrubbed before it is recorded.
    static func redact(_ message: String) -> String {
        guard
            let regex = try? NSRegularExpression(
                pattern: "((?:secret|token|password|authorization|api[-_]?key)\\s*[:=]\\s*)(\\S+)",
                options: .caseInsensitive
            )
        else { return message }
        let range = NSRange(message.startIndex..., in: message)
        return regex.stringByReplacingMatches(
            in: message,
            range: range,
            withTemplate: "$1[redacted]"
        )
    }

    @discardableResult
    public func record(_ component: String, _ level: Level, _ message: String) -> Event {
        seq += 1
        let event = Event(
            seq: seq,
            at: Date(),
            component: component,
            level: level,
            message: Self.redact(message)
        )
        ring.append(event)
        if ring.count > Self.ringMax { ring.removeFirst(ring.count - Self.ringMax) }
        append(event)
        return event
    }

    public func events(since cursor: Int = 0) -> [Event] {
        ring.filter { $0.seq > cursor }
    }

    public func cursor() -> Int { seq }

    /// Never throws into the caller: the ledger is evidence, not a dependency.
    private func append(_ event: Event) {
        guard !writesDisabled, let fileURL else { return }
        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            var line = try encoder.encode(event)
            line.append(0x0A)

            let manager = FileManager.default
            if let size = try? manager.attributesOfItem(atPath: fileURL.path)[.size] as? Int,
               size > Self.fileMaxBytes {
                try? manager.removeItem(at: fileURL.appendingPathExtension("1"))
                try? manager.moveItem(at: fileURL, to: fileURL.appendingPathExtension("1"))
            }

            if manager.fileExists(atPath: fileURL.path) {
                let handle = try FileHandle(forWritingTo: fileURL)
                defer { try? handle.close() }
                try handle.seekToEnd()
                try handle.write(contentsOf: line)
            } else {
                try line.write(to: fileURL)
            }
        } catch {
            writesDisabled = true
        }
    }
}
