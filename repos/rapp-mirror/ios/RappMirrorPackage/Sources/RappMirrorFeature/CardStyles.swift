import Foundation

public enum TextureKind: String, Sendable, Codable, Equatable, CaseIterable {
    case none, grain, halftone, scanlines, paper, weave
}

public enum HoloKind: String, Sendable, Codable, Equatable, CaseIterable {
    case none, linear, prismatic, shattered, pearl
}

public struct Palette: Sendable, Codable, Equatable {
    public let from: String
    public let to: String
    public let accent: String
    public let ink: String
    public let spot: String?

    public init(from: String, to: String, accent: String, ink: String, spot: String? = nil) {
        self.from = from
        self.to = to
        self.accent = accent
        self.ink = ink
        self.spot = spot
    }
}

public struct PathShape: Sendable, Codable, Equatable {
    public let d: String
    public let fill: String?
    public let stroke: String?
    public let width: Double?
    public let opacity: Double?

    public init(d: String, fill: String? = nil, stroke: String? = nil, width: Double? = nil, opacity: Double? = nil) {
        self.d = d
        self.fill = fill
        self.stroke = stroke
        self.width = width
        self.opacity = opacity
    }
}

public struct CircleShape: Sendable, Codable, Equatable {
    public let cx: Double
    public let cy: Double
    public let r: Double
    public let fill: String?
    public let stroke: String?
    public let width: Double?
    public let opacity: Double?
}

public struct RectShape: Sendable, Codable, Equatable {
    public let x: Double
    public let y: Double
    public let w: Double
    public let h: Double
    public let fill: String?
    public let stroke: String?
    public let width: Double?
    public let opacity: Double?
    public let radius: Double?
}

public struct LineShape: Sendable, Codable, Equatable {
    public let x1: Double
    public let y1: Double
    public let x2: Double
    public let y2: Double
    public let stroke: String
    public let width: Double?
    public let opacity: Double?
}

public struct TextShape: Sendable, Codable, Equatable {
    public let x: Double
    public let y: Double
    public let text: String
    public let fill: String
    public let size: Double
    public let family: String?
    public let opacity: Double?
}

public enum ArtShape: Sendable, Codable, Equatable {
    case path(PathShape)
    case circle(CircleShape)
    case rect(RectShape)
    case line(LineShape)
    case text(TextShape)

    public var numericValues: [Double] {
        switch self {
        case .path(let shape): [shape.width, shape.opacity].compactMap { $0 }
        case .circle(let shape): [shape.cx, shape.cy, shape.r, shape.width, shape.opacity].compactMap { $0 }
        case .rect(let shape): [shape.x, shape.y, shape.w, shape.h, shape.width, shape.opacity, shape.radius].compactMap { $0 }
        case .line(let shape): [shape.x1, shape.y1, shape.x2, shape.y2, shape.width, shape.opacity].compactMap { $0 }
        case .text(let shape): [shape.x, shape.y, shape.size, shape.opacity].compactMap { $0 }
        }
    }
}

public struct ArtWork: Sendable, Codable, Equatable {
    public let viewBox: String
    public let palette: Palette
    public let shapes: [ArtShape]
    public let texture: TextureKind
    public let holo: HoloKind
}

public struct StyleCredit: Sendable, Codable, Equatable, Identifiable {
    public let id: String
    public let name: String
    public let artist: String
    public let medium: String
}

public struct ArtContext {
    public var next: () -> Double
    public let element: Element
    public let rarity: Rarity
    public let seed: UInt32
}

public struct ArtStyle: Identifiable, @unchecked Sendable {
    public let id: String
    public let name: String
    public let artist: String
    public let medium: String
    public let render: (ArtContext) -> ArtWork

    public var credit: StyleCredit { StyleCredit(id: id, name: name, artist: artist, medium: medium) }
}

public enum CardStyleRegistry {
    public static let artViewBox = "0 0 100 100"
    public static let defaultStyleId = "prism"

    public static let artStyles: [ArtStyle] = [prism, woodblock, riso, ascii, vapor, blueprint]

    public static func styleById(_ id: String?) -> ArtStyle {
        artStyles.first { $0.id == id } ?? prism
    }

    public static func styleForSeed(_ seed: UInt32, rarity: Rarity) -> ArtStyle {
        if rarity == .cursed { return vapor }
        return artStyles[Int(seed % UInt32(artStyles.count))]
    }

    public static func credits() -> [StyleCredit] { artStyles.map(\.credit) }

    private static let tau = Double.pi * 2
    private static let elementHue: [Element: Double] = [.spirit: 200, .aether: 265, .ember: 22, .stone: 40, .void: 330]

    private static let prism = ArtStyle(id: "prism", name: "Prism", artist: "RAPP Studio", medium: "vector geometry") { context in
        var next = context.next
        let palette = elementPalette(context.element, next: &next)
        var shapes: [ArtShape] = []
        let rings = 3 + Int(floor(next() * 3))
        for index in 0..<rings {
            shapes.append(.path(PathShape(
                d: starPath(next: &next, points: 5 + Int(floor(next() * 4)), cx: 50, cy: 50, min: 10 + Double(index) * 6, span: 18),
                stroke: palette.accent,
                width: round2(0.6 + next() * 1.2),
                opacity: round2(0.35 + Double(index) * 0.18)
            )))
        }
        shapes.append(.circle(CircleShape(cx: 50, cy: 50, r: round2(6 + next() * 5), fill: palette.accent, stroke: nil, width: nil, opacity: 0.9)))
        return ArtWork(viewBox: artViewBox, palette: palette, shapes: shapes, texture: .grain, holo: .prismatic)
    }

    private static let woodblock = ArtStyle(id: "woodblock", name: "Floating World", artist: "after Hokusai", medium: "ukiyo-e woodblock") { context in
        var next = context.next
        let palette = elementPalette(context.element, next: &next)
        var shapes: [ArtShape] = []
        for index in 0..<4 {
            let y = 30 + Double(index) * 16
            let lift = 8 + next() * 14
            shapes.append(.path(PathShape(
                d: "M0,\(round2(y + lift)) C25,\(round2(y - lift)) 75,\(round2(y + lift * 1.4)) 100,\(round2(y - lift * 0.4)) L100,100 L0,100 Z",
                fill: index.isMultiple(of: 2) ? palette.accent : (palette.spot ?? palette.accent),
                opacity: round2(0.28 + Double(index) * 0.16)
            )))
        }
        shapes.append(.circle(CircleShape(cx: round2(28 + next() * 44), cy: round2(22 + next() * 10), r: round2(9 + next() * 5), fill: palette.ink, stroke: nil, width: nil, opacity: 0.85)))
        return ArtWork(viewBox: artViewBox, palette: palette, shapes: shapes, texture: .paper, holo: .none)
    }

    private static let riso = ArtStyle(id: "riso", name: "Duplicator", artist: "Riso Collective", medium: "risograph screenprint") { context in
        var next = context.next
        let palette = elementPalette(context.element, next: &next)
        var shapes: [ArtShape] = []
        func offset() -> Double { round2((next() - 0.5) * 5) }
        for layer in 0..<2 {
            let ink = layer == 0 ? palette.accent : (palette.spot ?? palette.ink)
            let dx = offset()
            let dy = offset()
            shapes.append(.path(PathShape(
                d: starPath(next: &next, points: 3 + Int(floor(next() * 4)), cx: 50 + dx, cy: 50 + dy, min: 16, span: 24),
                fill: ink,
                opacity: 0.62
            )))
        }
        return ArtWork(viewBox: artViewBox, palette: palette, shapes: shapes, texture: .halftone, holo: .none)
    }

    private static let ascii = ArtStyle(id: "ascii", name: "Teletype", artist: "Terminal Anonymous", medium: "ASCII / monospace") { context in
        var next = context.next
        let palette = elementPalette(context.element, next: &next, dark: true)
        let glyphs = ["#", "@", "%", "*", "+", "=", "-", ".", ":", "░", "▒", "▓"]
        var shapes: [ArtShape] = []
        let columns = 16
        let rows = 16
        for row in 0..<rows {
            var line = ""
            for column in 0..<columns {
                let dx = (Double(column) - Double(columns) / 2) / (Double(columns) / 2)
                let dy = (Double(row) - Double(rows) / 2) / (Double(rows) / 2)
                let density = 1 - min(1, hypot(dx, dy))
                line += density > next() * 0.9 ? pick(next: &next, glyphs) : " "
            }
            shapes.append(.text(TextShape(x: 6, y: round2(10 + Double(row) * 5.6), text: line, fill: row.isMultiple(of: 4) ? palette.accent : palette.ink, size: 5.4, family: "monospace", opacity: 0.9)))
        }
        return ArtWork(viewBox: artViewBox, palette: palette, shapes: shapes, texture: .scanlines, holo: .linear)
    }

    private static let vapor = ArtStyle(id: "vapor", name: "Horizon", artist: "Night Drive", medium: "neon / CRT") { context in
        var next = context.next
        let palette = elementPalette(context.element, next: &next, dark: true)
        var shapes: [ArtShape] = []
        let horizon = 54.0
        shapes.append(.circle(CircleShape(cx: 50, cy: round2(horizon - 10), r: round2(14 + next() * 8), fill: palette.accent, stroke: nil, width: nil, opacity: 0.8)))
        for index in 0..<9 {
            let t = Double(index + 1) / 10
            let y = round2(horizon + t * t * 46)
            shapes.append(.line(LineShape(x1: 0, y1: y, x2: 100, y2: y, stroke: palette.spot ?? palette.accent, width: 0.5, opacity: round2(0.9 - t * 0.5))))
        }
        for index in -6...6 {
            shapes.append(.line(LineShape(x1: 50, y1: horizon, x2: round2(50 + Double(index) * 22), y2: 100, stroke: palette.spot ?? palette.accent, width: 0.4, opacity: 0.45)))
        }
        return ArtWork(viewBox: artViewBox, palette: palette, shapes: shapes, texture: .scanlines, holo: .shattered)
    }

    private static let blueprint = ArtStyle(id: "blueprint", name: "Drafting Table", artist: "Sheet 3 of 7", medium: "cyanotype blueprint") { context in
        var next = context.next
        let palette = Palette(from: "hsl(214 65% 26%)", to: "hsl(214 70% 16%)", accent: "hsl(200 30% 92%)", ink: "hsl(200 25% 88%)", spot: "hsl(38 90% 66%)")
        var shapes: [ArtShape] = []
        for index in 1..<10 {
            let value = round2(Double(index) * 10)
            shapes.append(.line(LineShape(x1: value, y1: 0, x2: value, y2: 100, stroke: palette.accent, width: 0.25, opacity: 0.22)))
            shapes.append(.line(LineShape(x1: 0, y1: value, x2: 100, y2: value, stroke: palette.accent, width: 0.25, opacity: 0.22)))
        }
        let w = round2(30 + next() * 26)
        let h = round2(24 + next() * 26)
        let x = round2((100 - w) / 2)
        let y = round2((100 - h) / 2)
        shapes.append(.rect(RectShape(x: x, y: y, w: w, h: h, fill: nil, stroke: palette.ink, width: 1, opacity: 0.95, radius: nil)))
        shapes.append(.circle(CircleShape(cx: round2(x + w / 2), cy: round2(y + h / 2), r: round2(min(w, h) / 3), fill: nil, stroke: palette.spot ?? palette.ink, width: 0.8, opacity: 0.9)))
        shapes.append(.line(LineShape(x1: x, y1: round2(y + h + 6), x2: round2(x + w), y2: round2(y + h + 6), stroke: palette.spot ?? palette.ink, width: 0.5, opacity: 0.8)))
        shapes.append(.text(TextShape(x: x, y: round2(y + h + 12), text: "\(formatDimension(w)) × \(formatDimension(h))", fill: palette.ink, size: 5, family: "monospace", opacity: 0.85)))
        return ArtWork(viewBox: artViewBox, palette: palette, shapes: shapes, texture: .grain, holo: .none)
    }

    private static func elementPalette(_ element: Element, next: inout () -> Double, dark: Bool = false) -> Palette {
        let hue = elementHue[element] ?? 210
        let drift = (next() - 0.5) * 24
        if dark {
            return Palette(
                from: hsl(hue + drift, 30, 12),
                to: hsl(hue + drift + 30, 40, 22),
                accent: hsl(hue + drift, 85, 62),
                ink: hsl(hue, 20, 95),
                spot: hsl(hue + 160, 70, 60)
            )
        }
        return Palette(
            from: hsl(hue + drift, 70, 95),
            to: hsl(hue + drift + 20, 60, 80),
            accent: hsl(hue + drift, 75, 48),
            ink: hsl(hue, 45, 16),
            spot: hsl(hue + 150, 60, 55)
        )
    }

    private static func starPath(next: inout () -> Double, points: Int, cx: Double = 50, cy: Double = 50, min: Double = 18, span: Double = 26) -> String {
        var segments: [String] = []
        for index in 0..<points {
            let angle = (Double(index) / Double(points)) * tau - Double.pi / 2
            let radius = min + next() * span
            let command = index == 0 ? "M" : "L"
            segments.append("\(command)\(round2(cx + cos(angle) * radius)),\(round2(cy + sin(angle) * radius))")
        }
        return segments.joined(separator: " ") + " Z"
    }

    private static func hsl(_ hue: Double, _ saturation: Double, _ lightness: Double) -> String {
        "hsl(\(Int(hue.rounded())) \(Int(saturation.rounded()))% \(Int(lightness.rounded()))%)"
    }

    private static func pick<T>(next: inout () -> Double, _ items: [T]) -> T {
        items[Int(floor(next() * Double(items.count))) % items.count]
    }

    private static func round2(_ value: Double) -> Double {
        (value * 100).rounded() / 100
    }

    private static func formatDimension(_ value: Double) -> String {
        value == floor(value) ? String(Int(value)) : String(value)
    }
}
