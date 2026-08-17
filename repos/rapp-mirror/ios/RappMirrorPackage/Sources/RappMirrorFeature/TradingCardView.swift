import CoreImage
import SwiftUI
#if os(iOS) && canImport(CoreMotion)
import CoreMotion
#endif
#if canImport(UIKit)
import UIKit
#elseif canImport(AppKit)
import AppKit
#endif

public struct TradingCardView: View {
    /// The card's design size — 5:7, the same trading-card aspect the web
    /// card uses. Anything that lays a card out reads it from here, so a
    /// container can never assume a height the card does not have.
    public static let face = CGSize(width: 320, height: 448)

    public let card: CardFace
    public let shareURL: String
    @State private var flipped = false
    @State private var motion = MotionSheen()

    public init(card: CardFace, shareURL: String) {
        self.card = card
        self.shareURL = shareURL
    }

    public var body: some View {
        Button {
            flipped.toggle()
        } label: {
            TimelineView(.animation(minimumInterval: 1.0 / 20.0)) { _ in
                let tilt = motion.tilt
                ZStack {
                    cardFront(tilt: tilt)
                        .opacity(flipped ? 0 : 1)
                        .rotation3DEffect(.degrees(flipped ? 180 : 0), axis: (x: 0, y: 1, z: 0))
                    cardBack(tilt: tilt)
                        .opacity(flipped ? 1 : 0)
                        .rotation3DEffect(.degrees(flipped ? 0 : -180), axis: (x: 0, y: 1, z: 0))
                }
                .frame(width: Self.face.width, height: Self.face.height)
                .rotation3DEffect(.degrees(tilt.x * 4), axis: (x: 0, y: 1, z: 0))
                .rotation3DEffect(.degrees(-tilt.y * 3), axis: (x: 1, y: 0, z: 0))
                .animation(.snappy(duration: 0.45), value: flipped)
            }
        }
        .buttonStyle(.plain)
        .task { motion.start() }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(card.title) trading card, \(card.rarity.rawValue), trust \(card.trust). Double tap to flip.")
        .accessibilityHint("Flips between the card face and QR code back.")
        .accessibilityIdentifier("trading-card-\(card.seed)")
    }

    private func cardFront(tilt: MotionSheen.Tilt) -> some View {
        let cursed = card.rarity == .cursed
        return RoundedRectangle(cornerRadius: 22, style: .continuous)
            .fill(stockGradient(cursed: cursed))
            .overlay {
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(cursed ? Color.red.opacity(0.75) : Color.white.opacity(0.75), lineWidth: 2)
            }
            .overlay(alignment: .top) {
                FitVertically(height: Self.face.height) {
                    VStack(spacing: 9) {
                        header(cursed: cursed)
                        aperture(cursed: cursed)
                        typeLine(cursed: cursed)
                        moves(cursed: cursed)
                        footer(cursed: cursed)
                    }
                    .padding(16)
                }
            }
            // A trading card whose ink runs off its own edge is not a card.
            // SwiftUI overlays do not clip, and this one overflowed onto the
            // page below it.
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay { foil(cursed: cursed, tilt: tilt).clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous)) }
            .shadow(color: cursed ? .red.opacity(0.35) : .black.opacity(0.25), radius: 18, y: 10)
    }

    private func cardBack(tilt: MotionSheen.Tilt) -> some View {
        let cursed = card.rarity == .cursed
        return RoundedRectangle(cornerRadius: 22, style: .continuous)
            .fill(cursed ? LinearGradient(colors: [.black, .red.opacity(0.28)], startPoint: .topLeading, endPoint: .bottomTrailing) : LinearGradient(colors: [Color.rappCSS(card.palette.to), Color.rappCSS(card.palette.from)], startPoint: .top, endPoint: .bottom))
            .overlay {
                FitVertically(height: Self.face.height) {
                    VStack(spacing: 14) {
                        Text("RAPP AGENT CARD")
                            .font(.system(.headline, design: .rounded).weight(.black))
                            .tracking(2)
                        QRImage(text: shareURL)
                            .frame(width: 210, height: 210)
                            .padding(12)
                            .background(.white, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
                            .accessibilityLabel("QR code for \(card.title)")
                            .accessibilityIdentifier("trading-card-qr")
                        Text("Scan or tap to review. This never installs automatically.")
                            .font(.footnote.weight(.semibold))
                            .multilineTextAlignment(.center)
                        Text(card.dex)
                            .font(.caption.monospacedDigit())
                    }
                    .foregroundStyle(cursed ? .white : Color.rappCSS(card.palette.ink))
                    .padding(20)
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay { foil(cursed: cursed, tilt: tilt).clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous)) }
    }

    private func header(cursed: Bool) -> some View {
        HStack(alignment: .firstTextBaseline) {
            VStack(alignment: .leading, spacing: 2) {
                Text(card.title)
                    .font(.system(.title3, design: .rounded).weight(.black))
                    .lineLimit(1)
                Text(card.subtitle)
                    .font(.caption.monospaced())
                    .lineLimit(1)
                    .opacity(0.78)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 0) {
                Text("TRUST")
                    .font(.caption2.weight(.black))
                Text("\(card.trust)")
                    .font(.title3.monospacedDigit().weight(.black))
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(cursed ? .red.opacity(0.25) : Color.rappCSS(card.palette.accent).opacity(0.22), in: Capsule())
        }
        .foregroundStyle(cursed ? .white : Color.rappCSS(card.palette.ink))
    }

    private func aperture(cursed: Bool) -> some View {
        ArtWorkView(art: card.art, cursed: cursed)
            // The web card sets the aperture to 42% of the card, so every
            // artist paints the same hole. Ported as a proportion, not a
            // hardcoded 168pt, or the face stops adding up.
            .frame(height: Self.face.height * 0.42)
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(cursed ? .red.opacity(0.9) : Color.rappCSS(card.palette.ink).opacity(0.5), lineWidth: 2)
            }
            .background(.black.opacity(cursed ? 0.7 : 0.08), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .accessibilityIdentifier("trading-card-art")
    }

    private func typeLine(cursed: Bool) -> some View {
        HStack {
            Text(card.element.rawValue.uppercased())
            Spacer()
            Text(card.rarity.rawValue.uppercased())
        }
        .font(.caption.weight(.black))
        .tracking(1.5)
        .foregroundStyle(cursed ? .red : Color.rappCSS(card.palette.accent))
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(cursed ? .black.opacity(0.5) : .white.opacity(0.42), in: Capsule())
    }

    private func moves(cursed: Bool) -> some View {
        VStack(spacing: 7) {
            ForEach(card.moves) { move in
                VStack(alignment: .leading, spacing: 3) {
                    HStack {
                        HStack(spacing: 3) {
                            ForEach(0..<move.cost, id: \.self) { _ in
                                Circle().fill(cursed ? .red : Color.rappCSS(card.palette.accent)).frame(width: 9, height: 9)
                            }
                        }
                        Text(move.name)
                            .font(.subheadline.weight(.black))
                        Spacer()
                        Text("\(move.power)")
                            .font(.subheadline.monospacedDigit().weight(.black))
                    }
                    Text(move.text)
                        .font(.caption2)
                        .lineLimit(2)
                        .opacity(0.82)
                }
                .padding(8)
                .background(cursed ? .black.opacity(0.32) : .white.opacity(0.32), in: RoundedRectangle(cornerRadius: 10, style: .continuous))
            }
            if card.moves.isEmpty { Text("No declared moves.").font(.caption).opacity(0.7) }
        }
        .foregroundStyle(cursed ? .white : Color.rappCSS(card.palette.ink))
    }

    private func footer(cursed: Bool) -> some View {
        VStack(spacing: 3) {
            Text(card.flavor)
                .font(.caption.italic())
                .lineLimit(1)
            HStack {
                Text("Illus. \(card.style.artist)")
                Spacer()
                Text(card.dex)
            }
            .font(.caption2.monospaced())
        }
        .foregroundStyle(cursed ? .white.opacity(0.82) : Color.rappCSS(card.palette.ink).opacity(0.82))
    }

    private func stockGradient(cursed: Bool) -> LinearGradient {
        if cursed { return LinearGradient(colors: [.black, Color(red: 0.16, green: 0.02, blue: 0.05)], startPoint: .topLeading, endPoint: .bottomTrailing) }
        return LinearGradient(colors: [Color.rappCSS(card.palette.from), Color.rappCSS(card.palette.to)], startPoint: .topLeading, endPoint: .bottomTrailing)
    }

    private func foil(cursed: Bool, tilt: MotionSheen.Tilt) -> some View {
        let x = 0.5 + tilt.x * 0.18
        let y = 0.5 + tilt.y * 0.18
        return LinearGradient(
            colors: cursed ? [.clear, .red.opacity(0.16), .clear] : [.clear, .white.opacity(0.35), Color.rappCSS(card.palette.accent).opacity(0.18), .clear],
            startPoint: UnitPoint(x: max(0, x - 0.6), y: max(0, y - 0.6)),
            endPoint: UnitPoint(x: min(1, x + 0.6), y: min(1, y + 0.6))
        )
        .blendMode(cursed ? .plusDarker : .screen)
        .allowsHitTesting(false)
    }
}

public struct ArtWorkView: View {
    public let art: ArtWork
    public let cursed: Bool

    public init(art: ArtWork, cursed: Bool = false) {
        self.art = art
        self.cursed = cursed
    }

    public var body: some View {
        Canvas { context, size in
            let rect = CGRect(origin: .zero, size: size)
            let gradient = Gradient(colors: [Color.rappCSS(art.palette.from), Color.rappCSS(art.palette.to)])
            context.fill(Path(rect), with: .linearGradient(gradient, startPoint: .zero, endPoint: CGPoint(x: size.width, y: size.height)))
            let scale = min(size.width, size.height) / 100
            let xOffset = (size.width - 100 * scale) / 2
            let yOffset = (size.height - 100 * scale) / 2
            for shape in art.shapes {
                draw(shape, in: &context, scale: scale, xOffset: xOffset, yOffset: yOffset)
            }
            drawTexture(art.texture, in: &context, size: size)
            if cursed {
                context.stroke(Path(CGRect(x: 8, y: 8, width: size.width - 16, height: size.height - 16)), with: .color(.red.opacity(0.35)), lineWidth: 1)
            }
        }
    }

    private func draw(_ shape: ArtShape, in context: inout GraphicsContext, scale: Double, xOffset: Double, yOffset: Double) {
        func point(_ x: Double, _ y: Double) -> CGPoint { CGPoint(x: xOffset + x * scale, y: yOffset + y * scale) }
        func color(_ value: String?) -> Color { Color.rappCSS(value ?? art.palette.ink) }
        var local = context
        switch shape {
        case .path(let shape):
            let path = SVGPath.path(from: shape.d, scale: scale, xOffset: xOffset, yOffset: yOffset)
            local.opacity = shape.opacity ?? 1
            if let fill = shape.fill { local.fill(path, with: .color(color(fill))) }
            if let stroke = shape.stroke { local.stroke(path, with: .color(color(stroke)), lineWidth: (shape.width ?? 1) * scale) }
        case .circle(let shape):
            let center = point(shape.cx, shape.cy)
            let rect = CGRect(x: center.x - shape.r * scale, y: center.y - shape.r * scale, width: shape.r * 2 * scale, height: shape.r * 2 * scale)
            let path = Path(ellipseIn: rect)
            local.opacity = shape.opacity ?? 1
            if let fill = shape.fill { local.fill(path, with: .color(color(fill))) }
            if let stroke = shape.stroke { local.stroke(path, with: .color(color(stroke)), lineWidth: (shape.width ?? 1) * scale) }
        case .rect(let shape):
            let rect = CGRect(x: xOffset + shape.x * scale, y: yOffset + shape.y * scale, width: shape.w * scale, height: shape.h * scale)
            let path = Path(roundedRect: rect, cornerRadius: (shape.radius ?? 0) * scale)
            local.opacity = shape.opacity ?? 1
            if let fill = shape.fill { local.fill(path, with: .color(color(fill))) }
            if let stroke = shape.stroke { local.stroke(path, with: .color(color(stroke)), lineWidth: (shape.width ?? 1) * scale) }
        case .line(let shape):
            var path = Path()
            path.move(to: point(shape.x1, shape.y1))
            path.addLine(to: point(shape.x2, shape.y2))
            local.opacity = shape.opacity ?? 1
            local.stroke(path, with: .color(color(shape.stroke)), lineWidth: (shape.width ?? 1) * scale)
        case .text(let shape):
            local.opacity = shape.opacity ?? 1
            let resolved = local.resolve(Text(shape.text).font(.system(size: shape.size * scale, design: shape.family == "monospace" ? .monospaced : .default)).foregroundColor(color(shape.fill)))
            local.draw(resolved, at: point(shape.x, shape.y), anchor: .leading)
        }
    }

    private func drawTexture(_ texture: TextureKind, in context: inout GraphicsContext, size: CGSize) {
        switch texture {
        case .scanlines:
            for y in stride(from: 0.0, through: size.height, by: 5) {
                var path = Path()
                path.move(to: CGPoint(x: 0, y: y))
                path.addLine(to: CGPoint(x: size.width, y: y))
                context.stroke(path, with: .color(.black.opacity(0.12)), lineWidth: 1)
            }
        case .halftone:
            for x in stride(from: 6.0, through: size.width, by: 12) {
                for y in stride(from: 6.0, through: size.height, by: 12) {
                    context.fill(Path(ellipseIn: CGRect(x: x, y: y, width: 2, height: 2)), with: .color(.black.opacity(0.16)))
                }
            }
        case .grain, .paper, .weave:
            for i in 0..<32 {
                let x = Double((i * 37) % max(1, Int(size.width)))
                let y = Double((i * 53) % max(1, Int(size.height)))
                context.fill(Path(ellipseIn: CGRect(x: x, y: y, width: 1.4, height: 1.4)), with: .color(.white.opacity(0.16)))
            }
        case .none:
            break
        }
    }
}

public struct QRImage: View {
    public let text: String
    private let context = CIContext()

    public init(text: String) {
        self.text = text
    }

    public var body: some View {
        if let image = QRCode.image(for: text), let cgImage = context.createCGImage(image.transformed(by: CGAffineTransform(scaleX: 12, y: 12)), from: image.transformed(by: CGAffineTransform(scaleX: 12, y: 12)).extent) {
            Image(cgImage, scale: 1, orientation: .up, label: Text("QR code"))
                .interpolation(.none)
                .resizable()
                .scaledToFit()
        } else {
            Image(systemName: "qrcode")
                .resizable()
                .scaledToFit()
                .foregroundStyle(.black)
        }
    }
}

@Observable
public final class MotionSheen {
    public struct Tilt: Sendable, Equatable {
        public let x: Double
        public let y: Double
        public static let zero = Tilt(x: 0, y: 0)
    }

    #if os(iOS) && canImport(CoreMotion)
    @ObservationIgnored private let manager = CMMotionManager()
    #endif

    public init() {}

    public var tilt: Tilt {
        #if os(iOS) && canImport(CoreMotion)
        guard let motion = manager.deviceMotion else { return Tilt(x: 0.35, y: -0.2) }
        return Tilt(x: max(-1, min(1, motion.gravity.x)), y: max(-1, min(1, motion.gravity.y)))
        #else
        return Tilt(x: 0.35, y: -0.2)
        #endif
    }

    public func start() {
        #if os(iOS) && canImport(CoreMotion)
        guard manager.isDeviceMotionAvailable, !manager.isDeviceMotionActive else { return }
        manager.deviceMotionUpdateInterval = 1.0 / 30.0
        manager.startDeviceMotionUpdates()
        #endif
    }
}

private enum SVGPath {
    static func path(from data: String, scale: Double, xOffset: Double, yOffset: Double) -> Path {
        let tokens = tokenize(data)
        var path = Path()
        var index = 0
        var command = ""
        var current = CGPoint.zero
        func isCommand(_ token: String) -> Bool { token.count == 1 && "MLCQqZz".contains(token) }
        func number() -> Double? {
            guard index < tokens.count, let value = Double(tokens[index]) else { return nil }
            index += 1
            return value
        }
        func point(_ x: Double, _ y: Double) -> CGPoint { CGPoint(x: xOffset + x * scale, y: yOffset + y * scale) }

        while index < tokens.count {
            if isCommand(tokens[index]) {
                command = tokens[index]
                index += 1
            }
            switch command {
            case "M":
                guard let x = number(), let y = number() else { break }
                current = point(x, y)
                path.move(to: current)
                command = "L"
            case "L":
                guard let x = number(), let y = number() else { break }
                current = point(x, y)
                path.addLine(to: current)
            case "C":
                guard let x1 = number(), let y1 = number(), let x2 = number(), let y2 = number(), let x = number(), let y = number() else { break }
                current = point(x, y)
                path.addCurve(to: current, control1: point(x1, y1), control2: point(x2, y2))
            case "Q":
                guard let x1 = number(), let y1 = number(), let x = number(), let y = number() else { break }
                current = point(x, y)
                path.addQuadCurve(to: current, control: point(x1, y1))
            case "q":
                guard let x1 = number(), let y1 = number(), let x = number(), let y = number() else { break }
                let control = CGPoint(x: current.x + x1 * scale, y: current.y + y1 * scale)
                current = CGPoint(x: current.x + x * scale, y: current.y + y * scale)
                path.addQuadCurve(to: current, control: control)
            case "Z", "z":
                path.closeSubpath()
                command = ""
            default:
                index += 1
            }
        }
        return path
    }

    private static func tokenize(_ data: String) -> [String] {
        var out: [String] = []
        var current = ""
        func flush() {
            if !current.isEmpty { out.append(current); current = "" }
        }
        for char in data {
            if "MLCQqZz".contains(char) {
                flush()
                out.append(String(char))
            } else if char == "," || char.isWhitespace {
                flush()
            } else {
                current.append(char)
            }
        }
        flush()
        return out
    }
}

private extension Color {
    static func rappCSS(_ css: String) -> Color {
        let text = css.trimmingCharacters(in: .whitespacesAndNewlines)
        if text.hasPrefix("#") || text.range(of: #"^[0-9A-Fa-f]{6}$"#, options: .regularExpression) != nil {
            let hex = text.replacingOccurrences(of: "#", with: "")
            if let value = Int(hex, radix: 16) {
                return Color(red: Double((value >> 16) & 0xff) / 255, green: Double((value >> 8) & 0xff) / 255, blue: Double(value & 0xff) / 255)
            }
        }
        if text.hasPrefix("hsl") {
            let numbers = text.replacingOccurrences(of: #"[^0-9.\-]+"#, with: " ", options: .regularExpression).split(separator: " ").compactMap { Double($0) }
            if numbers.count >= 3 { return hsl(h: numbers[0], s: numbers[1], l: numbers[2]) }
        }
        return .primary
    }

    private static func hsl(h: Double, s: Double, l: Double) -> Color {
        let hue = ((h.truncatingRemainder(dividingBy: 360)) + 360).truncatingRemainder(dividingBy: 360) / 360
        let saturation = max(0, min(1, s / 100))
        let lightness = max(0, min(1, l / 100))
        let c = (1 - abs(2 * lightness - 1)) * saturation
        let x = c * (1 - abs((hue * 6).truncatingRemainder(dividingBy: 2) - 1))
        let m = lightness - c / 2
        let (r, g, b): (Double, Double, Double)
        switch hue * 6 {
        case 0..<1: (r, g, b) = (c, x, 0)
        case 1..<2: (r, g, b) = (x, c, 0)
        case 2..<3: (r, g, b) = (0, c, x)
        case 3..<4: (r, g, b) = (0, x, c)
        case 4..<5: (r, g, b) = (x, 0, c)
        default: (r, g, b) = (c, 0, x)
        }
        return Color(red: r + m, green: g + m, blue: b + m)
    }
}

/// Fits a card's printed matter inside the card.
///
/// A card face is a fixed 5:7 rectangle, but what goes on it is not fixed: move
/// names differ, art styles differ, and Dynamic Type can grow all of it. Rather
/// than tuning paddings until one particular agent happens to fit — and clipping
/// the footer off every other one — the content is measured at its natural size
/// and scaled down only if it would overrun. Nothing is cropped, and the design
/// keeps its proportions.
struct FitVertically<Content: View>: View {
    let height: CGFloat
    @ViewBuilder var content: Content

    @State private var natural: CGFloat = 0

    var body: some View {
        // scaleEffect does not change layout, so measuring the unscaled content
        // cannot feed back into the measurement.
        let scale = natural > height && natural > 0 ? height / natural : 1
        content
            .fixedSize(horizontal: false, vertical: true)
            .background {
                GeometryReader { geo in
                    Color.clear
                        .onAppear { natural = geo.size.height }
                        .onChange(of: geo.size.height) { _, new in natural = new }
                }
            }
            .scaleEffect(scale, anchor: .top)
            .frame(height: height, alignment: .top)
    }
}
