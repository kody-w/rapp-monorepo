import SwiftUI

/// A portal: one choice the mirror is offering, orbiting the core.
///
/// The desktop draws these as soft white cards with a coloured dash and a dwell
/// ring that fills while you look at them. On a phone there is no gaze, so the
/// dash and the tap carry the whole interaction — but the shape, the shadow and
/// the colour language are deliberately identical.
struct PortalView: View {
    let option: HoloOption
    let dash: Color
    /// 0…1 — the desktop's dwell ring, reused here for voice-pick feedback.
    var progress: Double = 0
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 12) {
                Capsule()
                    .fill(dash)
                    .frame(width: 30, height: 4)
                Text(option.label)
                    .font(.system(size: 15, weight: .medium))
                    .foregroundStyle(VUI.ink)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
                    .minimumScaleFactor(0.75)
            }
            .padding(14)
            .frame(width: 138, height: 100)
            .background(VUI.card, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
            .overlay {
                if progress > 0 {
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .trim(from: 0, to: progress)
                        .stroke(VUI.orbB, style: StrokeStyle(lineWidth: 3, lineCap: .round))
                }
            }
            .shadow(color: Color(red: 0.102, green: 0.133, blue: 0.188).opacity(0.10), radius: 22, y: 14)
        }
        .buttonStyle(.plain)
        .accessibilityIdentifier("portal-\(option.label)")
        .accessibilityLabel(option.label)
        .accessibilityHint("Choose this option")
    }
}

/// Lays portals around the core the way the desktop does — orbiting, never in a
/// list. On a phone the ring is squashed so the cards clear the orb's edges and
/// still fit a narrow screen.
struct PortalRing: View {
    let options: [HoloOption]
    let onPick: (HoloOption) -> Void

    /// Fixed diagonal slots rather than an even sweep.
    ///
    /// The orb's face carries the mic and "HOLD TO TALK", so the horizontal
    /// band through the centre must stay clear. Portals therefore take the
    /// corners — overlapping the blob the way the desktop does, but never the
    /// thing you are meant to read.
    private static let slots: [CGPoint] = [
        CGPoint(x: -1, y: -1), // top-left
        CGPoint(x: 1, y: -1),  // top-right
        CGPoint(x: -1, y: 1),  // bottom-left
        CGPoint(x: 1, y: 1),   // bottom-right
    ]

    /// Three options read better as two up, one centred below.
    private func offset(for index: Int, of count: Int) -> CGPoint {
        if count == 1 { return CGPoint(x: 0, y: -1) }
        if count == 3 && index == 2 { return CGPoint(x: 0, y: 1.06) }
        return Self.slots[index % Self.slots.count]
    }

    var body: some View {
        GeometryReader { geo in
            let center = CGPoint(x: geo.size.width / 2, y: geo.size.height / 2)
            let rx = min(geo.size.width / 2 - 74, 116)
            let ry = min(geo.size.height / 2 - 56, 148)
            let shown = Array(options.prefix(4).enumerated())

            ForEach(shown, id: \.element.label) { index, option in
                let slot = offset(for: index, of: shown.count)
                PortalView(
                    option: option,
                    dash: VUI.dashes[index % VUI.dashes.count]
                ) { onPick(option) }
                    .position(
                        x: center.x + slot.x * rx,
                        y: center.y + slot.y * ry
                    )
                    .transition(.scale(scale: 0.86).combined(with: .opacity))
            }
        }
        .allowsHitTesting(true)
    }
}
