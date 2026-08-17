import Foundation

public enum FindingSeverity: String, Sendable, Codable, Equatable {
    case critical
    case warn
}

public enum AgentVerdict: String, Sendable, Codable, Equatable {
    case safe
    case review
    case dangerous
    case invalid
}

public struct Finding: Sendable, Codable, Equatable, Identifiable {
    public var id: String
    public var severity: FindingSeverity
    public var detail: String
    public var line: Int
    public var evidence: String

    public init(severity: FindingSeverity, id: String, detail: String, line: Int, evidence: String) {
        self.severity = severity
        self.id = id
        self.detail = detail
        self.line = line
        self.evidence = evidence
    }
}

public struct AgentParameter: Sendable, Codable, Equatable, Identifiable {
    public var id: String { name }
    public let name: String
    public let description: String

    public init(name: String, description: String) {
        self.name = name
        self.description = description
    }
}

public struct AgentCard: Sendable, Codable, Equatable, Identifiable {
    public var id: String { className.isEmpty ? name : className }
    public let ok: Bool
    public let verdict: AgentVerdict
    public let className: String
    public let name: String
    public let description: String
    public let parameters: [AgentParameter]
    public let steps: [String]
    public let findings: [Finding]
    public let lineCount: Int
    public let error: String?

    public init(
        ok: Bool,
        verdict: AgentVerdict,
        className: String,
        name: String,
        description: String,
        parameters: [AgentParameter],
        steps: [String],
        findings: [Finding],
        lineCount: Int,
        error: String? = nil
    ) {
        self.ok = ok
        self.verdict = verdict
        self.className = className
        self.name = name
        self.description = description
        self.parameters = parameters
        self.steps = steps
        self.findings = findings
        self.lineCount = lineCount
        self.error = error
    }
}

private struct CapabilityProbe: Sendable {
    let id: String
    let severity: FindingSeverity
    let pattern: String
    let options: NSRegularExpression.Options
    let detail: String
}

public enum AgentCardInspector {
    private static let probes: [CapabilityProbe] = [
        CapabilityProbe(id: "exec", severity: .critical, pattern: #"\b(?:exec|eval)\s*\("#, options: [], detail: "runs code built at runtime (exec/eval)"),
        CapabilityProbe(id: "shell", severity: .critical, pattern: #"\b(?:subprocess|os\.system|os\.popen|os\.execv|pty\.spawn)\b"#, options: [], detail: "runs shell commands on your machine"),
        CapabilityProbe(id: "credentials", severity: .critical, pattern: #"(?:\.ssh|\.env\b|id_rsa|keychain|\.brainstem_secret|AWS_SECRET|credentials\.json)"#, options: [.caseInsensitive], detail: "reaches for credentials or private keys"),
        CapabilityProbe(id: "obfuscation", severity: .critical, pattern: #"base64\s*\.\s*b64decode|codecs\s*\.\s*decode\s*\([^)]*rot13|bytes\.fromhex"#, options: [], detail: "decodes hidden content before running it"),
        CapabilityProbe(id: "network", severity: .warn, pattern: #"\b(?:requests|httpx|urllib|http\.client|socket|aiohttp)\b"#, options: [], detail: "sends or receives data over the network"),
        CapabilityProbe(id: "filewrite", severity: .warn, pattern: #"\b(?:shutil\.rmtree|os\.remove|os\.unlink|\.write_text\s*\(|\.write_bytes\s*\()|open\s*\([^)]*['"][wa]"#, options: [], detail: "writes to or deletes files"),
        CapabilityProbe(id: "dynamic-import", severity: .warn, pattern: #"\b(?:__import__|importlib)\b"#, options: [], detail: "loads other modules dynamically"),
        CapabilityProbe(id: "env", severity: .warn, pattern: #"os\.environ\b"#, options: [], detail: "reads environment variables"),
    ]

    public static func inspectAgentSource(_ source: String) -> AgentCard {
        let lines = source.components(separatedBy: "\n")
        let base = AgentCard(
            ok: false,
            verdict: .invalid,
            className: "",
            name: "",
            description: "",
            parameters: [],
            steps: [],
            findings: [],
            lineCount: lines.count
        )

        guard !source.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            return base.with(error: "the file is empty")
        }

        guard let className = firstMatch(source, #"class\s+([A-Za-z_]\w*)\s*\(\s*BasicAgent\s*\)"#) else {
            return base.with(error: "not a RAPP agent: no `class <Name>(BasicAgent)` was found")
        }

        guard matches(source, #"def\s+perform\s*\("#) else {
            return base.with(className: className, error: "not a RAPP agent: it has no perform() method")
        }

        var findings: [Finding] = []
        var insideDocstring = false
        for (index, line) in lines.enumerated() {
            if isProse(line, insideDocstring: &insideDocstring) { continue }
            for probe in probes where matches(line, probe.pattern, options: probe.options) {
                findings.append(
                    Finding(
                        severity: probe.severity,
                        id: probe.id,
                        detail: probe.detail,
                        line: index + 1,
                        evidence: String(line.trimmingCharacters(in: .whitespacesAndNewlines).prefix(160))
                    )
                )
            }
        }

        var seen = Set<String>()
        let deduped = findings.filter { finding in
            guard !seen.contains(finding.id) else { return false }
            seen.insert(finding.id)
            return true
        }
        let verdict: AgentVerdict = deduped.contains { $0.severity == .critical } ? .dangerous : (deduped.isEmpty ? .safe : .review)
        let name = firstMatch(source, #"self\.name\s*=\s*"([^"]+)""#) ?? className
        let description = firstMatch(source, #""description"\s*:\s*"((?:[^"\\]|\\.)*)""#, options: [.dotMatchesLineSeparators])?.replacingOccurrences(of: #"\""#, with: #"""#) ?? ""

        return AgentCard(
            ok: true,
            verdict: verdict,
            className: className,
            name: name,
            description: description,
            parameters: parseParameters(source),
            steps: parseSteps(source),
            findings: deduped,
            lineCount: lines.count
        )
    }

    public static func cardSummary(_ card: AgentCard) -> String {
        guard card.ok else { return card.error ?? "unreadable" }
        let what = card.description.isEmpty ? "no description" : card.description
        switch card.verdict {
        case .safe:
            return "\(card.className) — \(what). Runs no shell, no network, no file writes."
        case .review:
            return "\(card.className) — \(what). Also: \(card.findings.map(\.detail).joined(separator: "; "))."
        case .dangerous, .invalid:
            let critical = card.findings.filter { $0.severity == .critical }.map(\.detail).joined(separator: "; ")
            return "\(card.className) — \(what). DANGEROUS: \(critical)."
        }
    }

    private static func isProse(_ line: String, insideDocstring: inout Bool) -> Bool {
        let trimmed = line.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.hasPrefix("#") { return true }
        let startsTriple = trimmed.hasPrefix("\"\"\"") || trimmed.hasPrefix("'''")
        guard startsTriple || insideDocstring else { return false }

        if startsTriple {
            let quote = trimmed.hasPrefix("\"\"\"") ? "\"\"\"" : "'''"
            let remainder = String(trimmed.dropFirst(3))
            let closesSameLine = remainder.contains(quote)
            insideDocstring = !insideDocstring && !closesSameLine
        } else if trimmed.contains("\"\"\"") || trimmed.contains("'''") {
            insideDocstring = false
        }
        return true
    }

    private static func parseParameters(_ source: String) -> [AgentParameter] {
        guard let block = firstMatch(source, #""properties"\s*:\s*\{([\s\S]*?)\n\s*\}\s*,\s*\n\s*"required""#, options: [.dotMatchesLineSeparators]) else { return [] }
        let regex = try? NSRegularExpression(pattern: #""([A-Za-z_]\w*)"\s*:\s*\{[^}]*?"description"\s*:\s*"((?:[^"\\]|\\.)*)""#, options: [.dotMatchesLineSeparators])
        let range = NSRange(block.startIndex..<block.endIndex, in: block)
        return regex?.matches(in: block, range: range).compactMap { match in
            guard let nameRange = Range(match.range(at: 1), in: block), let descriptionRange = Range(match.range(at: 2), in: block) else { return nil }
            return AgentParameter(
                name: String(block[nameRange]),
                description: String(block[descriptionRange]).replacingOccurrences(of: #"\""#, with: #"""#)
            )
        } ?? []
    }

    private static func parseSteps(_ source: String) -> [String] {
        guard let block = firstMatch(source, #"steps\s*=\s*\[([\s\S]*?)\]"#, options: [.dotMatchesLineSeparators]) else { return [] }
        let regex = try? NSRegularExpression(pattern: #""((?:[^"\\]|\\.)*)""#)
        let range = NSRange(block.startIndex..<block.endIndex, in: block)
        return regex?.matches(in: block, range: range).compactMap { match in
            guard let stepRange = Range(match.range(at: 1), in: block) else { return nil }
            let step = String(block[stepRange]).replacingOccurrences(of: #"\""#, with: #"""#)
            return step.isEmpty ? nil : step
        } ?? []
    }

    private static func firstMatch(_ source: String, _ pattern: String, options: NSRegularExpression.Options = []) -> String? {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: options) else { return nil }
        let range = NSRange(source.startIndex..<source.endIndex, in: source)
        guard let match = regex.firstMatch(in: source, range: range), match.numberOfRanges > 1,
              let matchRange = Range(match.range(at: 1), in: source) else { return nil }
        return String(source[matchRange])
    }

    private static func matches(_ source: String, _ pattern: String, options: NSRegularExpression.Options = []) -> Bool {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: options) else { return false }
        return regex.firstMatch(in: source, range: NSRange(source.startIndex..<source.endIndex, in: source)) != nil
    }
}

private extension AgentCard {
    func with(className: String? = nil, error: String) -> AgentCard {
        AgentCard(
            ok: ok,
            verdict: verdict,
            className: className ?? self.className,
            name: name,
            description: description,
            parameters: parameters,
            steps: steps,
            findings: findings,
            lineCount: lineCount,
            error: error
        )
    }
}
