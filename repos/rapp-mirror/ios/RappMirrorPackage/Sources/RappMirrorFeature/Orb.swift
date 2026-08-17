import SwiftUI

/// What the mirror is doing, expressed in one value the whole VUI reads from.
public enum MirrorPhase: Equatable, Sendable {
    case idle
    case listening
    case thinking
    case speaking
}

/// The rapp-vui palette, ported from the desktop mirror's `App.css` so the two
/// surfaces are unmistakably the same product.
enum VUI {
    static let bgA = Color(red: 0.953, green: 0.949, blue: 0.976) // #f3f2f9
    static let bgB = Color(red: 0.914, green: 0.918, blue: 0.953) // #e9eaf3
    static let ink = Color(red: 0.102, green: 0.133, blue: 0.188) // #1a2230
    static let dim = Color(red: 0.541, green: 0.576, blue: 0.639) // #8a93a3
    static let card = Color(red: 0.984, green: 0.984, blue: 0.992) // #fbfbfd
    static let orbA = Color(red: 0.545, green: 0.557, blue: 0.976) // #8b8ef9
    static let orbB = Color(red: 0.427, green: 0.447, blue: 0.953) // #6d72f3
    static let pink = Color(red: 0.957, green: 0.447, blue: 0.714) // #f472b6

    /// The dash colours a portal can wear, in order.
    static let dashes: [Color] = [
        Color(red: 0.204, green: 0.827, blue: 0.600), // green
        Color(red: 0.231, green: 0.510, blue: 0.965), // blue
        Color(red: 0.659, green: 0.333, blue: 0.969), // purple
        pink,
    ]

    static let background = LinearGradient(
        colors: [bgA, bgB],
        startPoint: .topLeading,
        endPoint: .bottomTrailing
    )
}

/// The living core: hold it to talk, release to send.
///
/// Everything about it is driven by `phase`, so there is exactly one place that
/// decides what the mirror looks like at any moment — the same discipline the
/// desktop orb follows.
struct Orb: View {
    let phase: MirrorPhase
    let onPressChanged: (Bool) -> Void

    @State private var drift = false
    @State private var pulse = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    private var pulsePeriod: Double {
        switch phase {
        case .listening: 1.3
        case .thinking: 0.8
        case .speaking: 2.4
        case .idle: 0
        }
    }

    private var glow: Color {
        phase == .listening ? VUI.pink : VUI.orbB
    }

    private var label: String {
        switch phase {
        case .idle: "HOLD TO TALK"
        case .listening: "LISTENING"
        case .thinking: "THINKING"
        case .speaking: "SPEAKING"
        }
    }

    var body: some View {
        ZStack {
            blob
            wireRing
            core
        }
        .frame(width: 340, height: 340)
        .onAppear {
            guard !reduceMotion else { return }
            withAnimation(.easeInOut(duration: 14).repeatForever(autoreverses: true)) {
                drift = true
            }
        }
        .onChange(of: phase) { _, _ in restartPulse() }
    }

    /// The soft violet mass behind the core — the mirror's "presence".
    private var blob: some View {
        RoundedPolygon(sides: 9, corner: 0.34)
            .fill(
                LinearGradient(
                    colors: [VUI.orbA, VUI.orbB],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
            )
            .frame(width: 318, height: 318)
            .rotationEffect(.degrees(drift ? 4 : -3))
            .scaleEffect(drift ? 1.02 : 0.99)
            .opacity(0.9)
            // Enough softness to glow, not so much that the silhouette is lost.
            .blur(radius: 4)
    }

    private var wireRing: some View {
        Circle()
            .stroke(Color.white.opacity(0.55), lineWidth: 1)
            .frame(width: 232, height: 232)
    }

    private var core: some View {
        ZStack {
            Circle()
                .fill(
                    RadialGradient(
                        colors: [
                            .white,
                            Color(red: 0.933, green: 0.949, blue: 1.0),
                            Color(red: 0.875, green: 0.902, blue: 0.992),
                        ],
                        center: UnitPoint(x: 0.42, y: 0.34),
                        startRadius: 4,
                        endRadius: 130
                    )
                )
                .overlay(Circle().stroke(Color.white.opacity(0.9), lineWidth: 1.5))
                .shadow(color: glow.opacity(phase == .idle ? 0.18 : 0.32), radius: 30, y: 18)

            VStack(spacing: 12) {
                Image(systemName: phase == .speaking ? "waveform" : "mic")
                    .font(.system(size: 30, weight: .regular))
                    .foregroundStyle(Color(red: 0.176, green: 0.216, blue: 0.282))
                    .contentTransition(.symbolEffect(.replace))
                Text(label)
                    .font(.system(size: 11, weight: .medium))
                    .tracking(3.4)
                    .foregroundStyle(Color(red: 0.290, green: 0.337, blue: 0.408))
            }
        }
        .frame(width: 196, height: 196)
        .scaleEffect(pulse && pulsePeriod > 0 ? 1.03 : 1)
        .contentShape(Circle())
        .accessibilityElement()
        .accessibilityIdentifier("orb")
        .accessibilityLabel("Hold to talk to the mirror")
        .accessibilityHint("Press and hold to speak, release to send")
        .accessibilityAddTraits(.isButton)
        .gesture(
            // Push-to-talk: the press *is* the recording, exactly like holding
            // the desktop orb or the space bar.
            DragGesture(minimumDistance: 0)
                .onChanged { _ in onPressChanged(true) }
                .onEnded { _ in onPressChanged(false) }
        )
    }

    private func restartPulse() {
        pulse = false
        guard pulsePeriod > 0, !reduceMotion else { return }
        withAnimation(.easeInOut(duration: pulsePeriod / 2).repeatForever(autoreverses: true)) {
            pulse = true
        }
    }
}

/// The blob's silhouette: a rounded polygon that reads as organic rather than
/// geometric, matching the desktop's drifting mass.
struct RoundedPolygon: Shape {
    let sides: Int
    /// 0 = sharp vertices, 1 = fully rounded.
    let corner: CGFloat

    func path(in rect: CGRect) -> Path {
        guard sides >= 3 else { return Path(ellipseIn: rect) }
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let radius = min(rect.width, rect.height) / 2
        var points: [CGPoint] = []
        for i in 0..<sides {
            let angle = (Double(i) / Double(sides)) * 2 * .pi - .pi / 2
            points.append(
                CGPoint(x: center.x + cos(angle) * radius, y: center.y + sin(angle) * radius)
            )
        }

        var path = Path()
        for i in 0..<points.count {
            let current = points[i]
            let next = points[(i + 1) % points.count]
            let mid = CGPoint(x: (current.x + next.x) / 2, y: (current.y + next.y) / 2)
            if i == 0 {
                path.move(to: mid)
            } else {
                // Quadratic through the vertex softens each corner.
                path.addQuadCurve(to: mid, control: blend(current, toward: mid, by: 1 - corner))
            }
        }
        let first = points[0]
        let last = points[points.count - 1]
        let closingMid = CGPoint(x: (last.x + first.x) / 2, y: (last.y + first.y) / 2)
        path.addQuadCurve(to: closingMid, control: blend(first, toward: closingMid, by: 1 - corner))
        path.closeSubpath()
        return path
    }

    private func blend(_ point: CGPoint, toward target: CGPoint, by amount: CGFloat) -> CGPoint {
        CGPoint(
            x: point.x + (target.x - point.x) * (1 - amount),
            y: point.y + (target.y - point.y) * (1 - amount)
        )
    }
}
