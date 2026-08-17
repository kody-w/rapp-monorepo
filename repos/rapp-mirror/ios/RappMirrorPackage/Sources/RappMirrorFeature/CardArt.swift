import Foundation

public enum Element: String, Sendable, Codable, Equatable, CaseIterable {
    case spirit, aether, ember, stone, void
}

public enum Rarity: String, Sendable, Codable, Equatable, CaseIterable {
    case common, uncommon, rare, holo, cursed
}

public struct Move: Sendable, Codable, Equatable, Identifiable {
    public var id: String { "\(name)-\(cost)-\(power)" }
    public let name: String
    public let cost: Int
    public let text: String
    public let power: Int
}

public struct CardFace: Sendable, Codable, Equatable, Identifiable {
    public var id: UInt32 { seed }
    public let seed: UInt32
    public let title: String
    public let subtitle: String
    public let element: Element
    public let rarity: Rarity
    public let trust: Int
    public let moves: [Move]
    public let art: ArtWork
    public let style: StyleCredit
    public let palette: Palette
    public let flavor: String
    public let dex: String
}

public enum CardArt {
    public static let elementOrder: [Element] = [.spirit, .aether, .ember, .stone, .void]

    private static let flavor: [Rarity: String] = [
        .common: "Forged in a quiet room.",
        .uncommon: "It has seen the outside.",
        .rare: "Few of these were ever made.",
        .holo: "Watched once. Repeats forever.",
        .cursed: "It asks for the keys. Decide carefully.",
    ]

    public static func fingerprint(_ input: String) -> UInt32 {
        var hash: UInt32 = 0x811c9dc5
        for codeUnit in input.utf16 {
            hash ^= UInt32(codeUnit)
            hash = hash &* 0x01000193
        }
        return hash
    }

    public static func rng(seed: UInt32) -> () -> Double {
        var a = seed
        return {
            a = a &+ 0x6d2b79f5
            var t = (a ^ (a >> 15)) &* (1 | a)
            t = (t &+ ((t ^ (t >> 7)) &* (61 | t))) ^ t
            return Double((t ^ (t >> 14))) / 4_294_967_296
        }
    }

    public static func elementFor(_ card: AgentCard) -> Element {
        let ids = Set(card.findings.map(\.id))
        if ids.contains("exec") || ids.contains("credentials") || ids.contains("obfuscation") { return .void }
        if ids.contains("shell") { return .ember }
        if ids.contains("network") { return .aether }
        if ids.contains("filewrite") || ids.contains("dynamic-import") || ids.contains("env") { return .stone }
        return .spirit
    }

    public static func rarityFor(_ card: AgentCard) -> Rarity {
        if card.verdict == .dangerous { return .cursed }
        if card.verdict == .review { return card.findings.count > 2 ? .common : .uncommon }
        if card.steps.count >= 5 { return .holo }
        if card.steps.count >= 3 { return .rare }
        return .uncommon
    }

    public static func trustFor(_ card: AgentCard) -> Int {
        let penalty = card.findings.reduce(0) { sum, finding in sum + (finding.severity == .critical ? 35 : 12) }
        let bonus = min(card.parameters.count * 5, 20)
        return max(20, min(120, 100 - penalty + bonus))
    }

    public static func mintCard(_ card: AgentCard, styleId: String? = nil) -> CardFace {
        let seed = fingerprint([card.className, card.name, card.description, card.steps.joined(separator: "|"), card.verdict.rawValue].joined(separator: "::"))
        var next = rng(seed: seed)
        let element = elementFor(card)
        let rarity = rarityFor(card)
        let style = styleId.map(CardStyleRegistry.styleById) ?? CardStyleRegistry.styleForSeed(seed, rarity: rarity)
        let art = style.render(ArtContext(next: rng(seed: seed ^ 0x9e3779b9), element: element, rarity: rarity, seed: seed))
        return CardFace(
            seed: seed,
            title: card.name.isEmpty ? (card.className.isEmpty ? "Unknown Agent" : card.className) : card.name,
            subtitle: card.className,
            element: element,
            rarity: rarity,
            trust: trustFor(card),
            moves: movesFor(card, next: &next),
            art: art,
            style: style.credit,
            palette: art.palette,
            flavor: flavor[rarity] ?? "Forged in a quiet room.",
            dex: "\(String(format: "%03d", Int(seed % 151) + 1)) / 151"
        )
    }

    public static func elementIndex(_ element: Element) -> Int {
        elementOrder.firstIndex(of: element) ?? -1
    }

    private static func movesFor(_ card: AgentCard, next: inout () -> Double) -> [Move] {
        let source = card.steps.isEmpty ? [card.description.isEmpty ? "Performs its purpose." : card.description] : card.steps
        return source.prefix(3).enumerated().map { index, step in
            let stripped = step.replacingOccurrences(of: #"^\s*\d+[.)]\s*"#, with: "", options: .regularExpression)
            let parts = stripped.split(separator: ":", omittingEmptySubsequences: false)
            let head = parts.first.map(String.init) ?? ""
            let rest = parts.dropFirst().joined(separator: ":")
            let name = String((head.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? "Move \(index + 1)" : head.trimmingCharacters(in: .whitespacesAndNewlines)).prefix(28))
            let textSource = rest.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? stripped : rest.trimmingCharacters(in: .whitespacesAndNewlines)
            return Move(name: name, cost: 1 + (index % 3), text: String(textSource.prefix(96)), power: 10 * (2 + Int(floor(next() * 7))))
        }
    }
}
