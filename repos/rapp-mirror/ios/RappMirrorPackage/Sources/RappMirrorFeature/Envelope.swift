import Foundation

/// A choice the mirror can project as a portal.
public struct HoloOption: Equatable, Sendable {
    public let label: String
    public let value: String?

    public init(label: String, value: String? = nil) {
        self.label = label
        self.value = value
    }

    /// What to send back when this portal is picked.
    public var send: String { value ?? label }
}

public struct Holo: Equatable, Sendable {
    public let prompt: String?
    public let options: [HoloOption]

    public init(prompt: String? = nil, options: [HoloOption]) {
        self.prompt = prompt
        self.options = options
    }
}

/// The rapp-vui envelope: what is shown, what is spoken, what is offered.
public struct Envelope: Equatable, Sendable {
    public let text: String
    public let spoken: String?
    public let holo: Holo?

    public init(text: String, spoken: String? = nil, holo: Holo? = nil) {
        self.text = text
        self.spoken = spoken
        self.holo = holo
    }
}

/// Faithful Swift port of the desktop mirror's `parseEnvelope` (common/ipc.ts).
///
///     text |||VOICE||| spoken |||OPTIONS||| a | b | c
///     text |||VOICE||| spoken |||HOLO||| {"prompt": "…", "options": [ … ]}
///
/// Malformed sections degrade to clean text — never to a crash, and never to a
/// marker leaking into something the user reads or hears.
public enum EnvelopeParser {
    static let maxOptions = 6
    static let maxLabelLength = 80

    private static let markers = ["|||VOICE|||", "|||HOLO|||", "|||OPTIONS|||"]

    public static func parse(_ raw: String) -> Envelope {
        let src = raw
        let found = markers
            .compactMap { marker -> (marker: String, range: Range<String.Index>)? in
                guard let range = src.range(of: marker) else { return nil }
                return (marker, range)
            }
            .sorted { $0.range.lowerBound < $1.range.lowerBound }

        let textEnd = found.first?.range.lowerBound ?? src.endIndex
        let text = String(src[src.startIndex..<textEnd]).trimmingCharacters(in: .whitespacesAndNewlines)

        var spoken: String?
        var holo: Holo?

        for (index, entry) in found.enumerated() {
            let sectionEnd = index + 1 < found.count ? found[index + 1].range.lowerBound : src.endIndex
            let section = String(src[entry.range.upperBound..<sectionEnd])
                .trimmingCharacters(in: .whitespacesAndNewlines)

            switch entry.marker {
            case "|||VOICE|||":
                spoken = section.isEmpty ? nil : section
            case "|||HOLO|||":
                if let parsed = parseHolo(section) { holo = parsed }
            default:
                if holo == nil, let parsed = parseOptions(section) { holo = parsed }
            }
        }

        return Envelope(text: text, spoken: spoken, holo: holo)
    }

    private static func parseHolo(_ section: String) -> Holo? {
        guard
            let data = section.data(using: .utf8),
            let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
            let rawOptions = object["options"] as? [Any]
        else { return nil }

        let options = rawOptions.compactMap { item -> HoloOption? in
            guard let dict = item as? [String: Any], let label = dict["label"] as? String else { return nil }
            return HoloOption(label: label, value: dict["value"] as? String)
        }
        .prefix(maxOptions)

        return Holo(prompt: object["prompt"] as? String, options: Array(options))
    }

    /// `|||OPTIONS|||` quick form: pipe-separated labels, deduped, capped.
    private static func parseOptions(_ section: String) -> Holo? {
        var seen = Set<String>()
        let options = section
            .split(separator: "|", omittingEmptySubsequences: false)
            .map(clean)
            .filter { label in
                guard !label.isEmpty else { return false }
                return seen.insert(label.lowercased()).inserted
            }
            .prefix(maxOptions)
            .map { HoloOption(label: $0) }

        return options.isEmpty ? nil : Holo(options: Array(options))
    }

    /// Strip list bullets/numbering the model may have added, then cap length.
    private static func clean(_ raw: Substring) -> String {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        let stripped = trimmed.drop { "-•0123456789. \t".contains($0) }
        return String(stripped.prefix(maxLabelLength))
    }
}
