import Compression
import CoreImage
import Foundation

public let shareScheme = "rapp"
public let shareVersion = 1
public let maxPayloadCharacters = 1_800

public struct ForgeStep: Sendable, Codable, Equatable, Identifiable {
    public var id: String { title + detail }
    public let title: String
    public let detail: String

    public init(title: String, detail: String) {
        self.title = title
        self.detail = detail
    }
}

public struct ForgeParameter: Sendable, Codable, Equatable, Identifiable {
    public var id: String { name }
    public let name: String
    public let description: String
    public let type: String
    public let required: Bool

    public init(name: String, description: String, type: String, required: Bool) {
        self.name = name
        self.description = description
        self.type = type
        self.required = required
    }
}

public struct ForgeSpec: Sendable, Codable, Equatable, Identifiable {
    public var id: String { className }
    public let name: String
    public let className: String
    public let title: String
    public let description: String
    public let intent: String
    public let steps: [ForgeStep]
    public let parameters: [ForgeParameter]

    public init(name: String, className: String, title: String, description: String, intent: String, steps: [ForgeStep] = [], parameters: [ForgeParameter] = []) {
        self.name = name
        self.className = className
        self.title = title
        self.description = description
        self.intent = intent
        self.steps = steps
        self.parameters = parameters
    }

    public var agentCard: AgentCard {
        AgentCard(
            ok: true,
            verdict: .safe,
            className: className,
            name: title.isEmpty ? (name.isEmpty ? className : name) : title,
            description: description,
            parameters: parameters.map { AgentParameter(name: $0.name, description: $0.description) },
            steps: steps.enumerated().map { index, step in "\(index + 1). \(step.title): \(step.detail)" },
            findings: [],
            lineCount: 0
        )
    }
}

private struct PackedSpec: Codable {
    let n: String
    let c: String
    let t: String
    let d: String
    let i: String
    let s: [[String]]
    let p: [[PackedParameterValue]]
}

private enum PackedParameterValue: Codable, Equatable {
    case string(String)
    case int(Int)

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let int = try? container.decode(Int.self) {
            self = .int(int)
        } else {
            self = .string(try container.decode(String.self))
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .string(let value): try container.encode(value)
        case .int(let value): try container.encode(value)
        }
    }

    var string: String {
        switch self {
        case .string(let value): value
        case .int(let value): String(value)
        }
    }

    var int: Int? {
        if case .int(let value) = self { return value }
        return nil
    }
}

public struct EncodeShareResult: Sendable, Equatable {
    public let ok: Bool
    public let url: String?
    public let size: Int?
    public let error: String?
}

public struct DecodeShareResult: Sendable, Equatable {
    public let ok: Bool
    public let spec: ForgeSpec?
    public let error: String?
}

public enum ShareURL {
    public static func encodeShareUrl(_ spec: ForgeSpec) -> EncodeShareResult {
        guard isValidClassName(spec.className) else {
            return EncodeShareResult(ok: false, url: nil, size: nil, error: "the card names an invalid agent class")
        }
        do {
            let packed = pack(spec)
            let json = try JSONEncoder().encode(packed)
            let payload = base64URL(try deflateRaw(json))
            if payload.count > maxPayloadCharacters {
                return EncodeShareResult(ok: false, url: nil, size: payload.count, error: "this agent is too detailed to fit in a QR (\(payload.count) of \(maxPayloadCharacters) characters) — AirDrop the file instead")
            }
            let name = (spec.name.isEmpty ? (spec.className.isEmpty ? "agent" : spec.className) : spec.name).addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "agent"
            return EncodeShareResult(ok: true, url: "\(shareScheme)://agent?v=\(shareVersion)&n=\(name)&d=\(payload)", size: payload.count, error: nil)
        } catch {
            return EncodeShareResult(ok: false, url: nil, size: nil, error: error.localizedDescription)
        }
    }

    public static func decodeShareUrl(_ raw: String) -> DecodeShareResult {
        do {
            let text = raw.trimmingCharacters(in: .whitespacesAndNewlines)
            guard text.hasPrefix("\(shareScheme)://agent") else { return DecodeShareResult(ok: false, spec: nil, error: "not a RAPP agent card") }
            guard let components = URLComponents(string: text), components.scheme == shareScheme, components.host == "agent" else {
                return DecodeShareResult(ok: false, spec: nil, error: "not a RAPP agent card")
            }
            let items = Dictionary(uniqueKeysWithValues: (components.queryItems ?? []).compactMap { item in item.value.map { (item.name, $0) } })
            let version = Int(items["v"] ?? "0") ?? 0
            guard version == shareVersion else { return DecodeShareResult(ok: false, spec: nil, error: "this card was made by a newer mirror (format v\(version))") }
            guard let data = items["d"], !data.isEmpty else { return DecodeShareResult(ok: false, spec: nil, error: "the card carries no agent") }
            let json = try inflateRaw(unbase64URL(data))
            let packed = try JSONDecoder().decode(PackedSpec.self, from: json)
            let spec = unpack(packed)
            guard isValidClassName(spec.className) else { return DecodeShareResult(ok: false, spec: nil, error: "the card names an invalid agent class") }
            return DecodeShareResult(ok: true, spec: spec, error: nil)
        } catch {
            return DecodeShareResult(ok: false, spec: nil, error: "the card is damaged or was not made by a mirror")
        }
    }

    public static func isValidClassName(_ className: String) -> Bool {
        className.range(of: #"^[A-Za-z_]\w*$"#, options: .regularExpression) != nil
    }

    private static func pack(_ spec: ForgeSpec) -> PackedSpec {
        PackedSpec(
            n: spec.name,
            c: spec.className,
            t: spec.title,
            d: spec.description,
            i: spec.intent,
            s: spec.steps.map { [$0.title, $0.detail] },
            p: spec.parameters.map { [.string($0.name), .string($0.description), .string($0.type), .int($0.required ? 1 : 0)] }
        )
    }

    private static func unpack(_ packed: PackedSpec) -> ForgeSpec {
        ForgeSpec(
            name: packed.n,
            className: packed.c,
            title: packed.t,
            description: packed.d,
            intent: packed.i,
            steps: packed.s.map { ForgeStep(title: $0.indices.contains(0) ? $0[0] : "", detail: $0.indices.contains(1) ? $0[1] : "") },
            parameters: packed.p.map { row in
                ForgeParameter(
                    name: row.indices.contains(0) ? row[0].string : "",
                    description: row.indices.contains(1) ? row[1].string : "",
                    type: row.indices.contains(2) ? row[2].string : "string",
                    required: (row.indices.contains(3) ? row[3].int : 0) == 1
                )
            }
        )
    }

    private static func base64URL(_ data: Data) -> String {
        data.base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=+$", with: "", options: .regularExpression)
    }

    private static func unbase64URL(_ text: String) throws -> Data {
        var base64 = text.replacingOccurrences(of: "-", with: "+").replacingOccurrences(of: "_", with: "/")
        let padding = (4 - base64.count % 4) % 4
        if padding > 0 { base64 += String(repeating: "=", count: padding) }
        guard let data = Data(base64Encoded: base64) else { throw ShareError.invalidBase64 }
        return data
    }

    private static func deflateRaw(_ data: Data) throws -> Data {
        try data.withUnsafeBytes { sourceBuffer in
            guard let source = sourceBuffer.bindMemory(to: UInt8.self).baseAddress else { return Data() }
            var destination = Data(count: max(64, data.count + 64))
            while destination.count <= maxPayloadCharacters * 4 {
                let capacity = destination.count
                let written = destination.withUnsafeMutableBytes { destinationBuffer in
                    compression_encode_buffer(destinationBuffer.bindMemory(to: UInt8.self).baseAddress!, capacity, source, data.count, nil, COMPRESSION_ZLIB)
                }
                if written > 0 { return Data(destination.prefix(written)) }
                destination = Data(count: destination.count * 2)
            }
            throw ShareError.compressionFailed
        }
    }

    private static func inflateRaw(_ data: Data) throws -> Data {
        try data.withUnsafeBytes { sourceBuffer in
            guard let source = sourceBuffer.bindMemory(to: UInt8.self).baseAddress else { return Data() }
            var destination = Data(count: 4_096)
            while destination.count <= 1_048_576 {
                let capacity = destination.count
                let written = destination.withUnsafeMutableBytes { destinationBuffer in
                    compression_decode_buffer(destinationBuffer.bindMemory(to: UInt8.self).baseAddress!, capacity, source, data.count, nil, COMPRESSION_ZLIB)
                }
                if written > 0 { return Data(destination.prefix(written)) }
                destination = Data(count: destination.count * 2)
            }
            throw ShareError.compressionFailed
        }
    }
}

public enum QRCode {
    public static func image(for text: String) -> CIImage? {
        let filter = CIFilter(name: "CIQRCodeGenerator")
        filter?.setValue(Data(text.utf8), forKey: "inputMessage")
        filter?.setValue("M", forKey: "inputCorrectionLevel")
        return filter?.outputImage
    }
}

private enum ShareError: Error {
    case invalidBase64
    case compressionFailed
}
