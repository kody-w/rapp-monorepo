import SwiftUI

/// The companion, as tiles.
///
/// The hero tile is what the life adds up to right now; the grid below it is
/// the life itself, newest first, one tile per frame. They are the same tiles
/// the store holds — the view never invents a moment the disk does not have,
/// which is why a morph you see here is a morph that survived the app being
/// killed.
struct CompanionTilesView: View {
    @Bindable var companion: Companion

    @Environment(\.dismiss) private var dismiss
    @State private var stats: TileStore.Stats?
    @State private var inspected: CompanionFrame?

    private let columns = [GridItem(.adaptive(minimum: 104), spacing: 12)]

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    hero
                    if let morphedFrom = companion.morphedFrom {
                        morphBanner(from: morphedFrom)
                    }
                    if let error = companion.lastError {
                        trouble(error)
                    }
                    tiles
                    ledger
                }
                .padding(.vertical, 14)
            }
            .background(VUI.background.ignoresSafeArea())
            .navigationTitle("Companion")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                        .accessibilityIdentifier("close-companion")
                }
            }
            .task {
                await companion.load()
                stats = await companion.stats()
            }
            .sheet(item: $inspected) { frame in
                FrameTileDetail(frame: frame)
            }
        }
    }

    /* ── the face ───────────────────────────────────────────────────── */

    private var hero: some View {
        VStack(spacing: 12) {
            ArtWorkView(art: companion.form.art, cursed: companion.form.rarity == .cursed)
                .frame(width: 168, height: 168)
                .clipShape(RoundedRectangle(cornerRadius: 26, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 26, style: .continuous)
                        .strokeBorder(VUI.ink.opacity(0.08), lineWidth: 1)
                }
                .shadow(color: VUI.ink.opacity(0.14), radius: 18, y: 8)
                // The whole point of a morph is that you can see it happen.
                .scaleEffect(companion.form.stage == .egg ? 0.92 : 1)
                .animation(.spring(response: 0.55, dampingFraction: 0.72), value: companion.form.stage)
                .animation(.easeInOut(duration: 0.4), value: companion.form.seed)
                .accessibilityIdentifier("companion-hero")
                .accessibilityLabel("\(companion.form.stage.title), \(companion.form.element.rawValue), \(companion.form.frames) tiles")

            Text(companion.form.stage.title)
                .font(.title3.weight(.semibold))
                .foregroundStyle(VUI.ink)

            HStack(spacing: 6) {
                chip(companion.form.element.rawValue)
                chip(companion.form.rarity.rawValue)
                chip("\(companion.form.frames) tiles")
            }

            vigorBar
        }
        .frame(maxWidth: .infinity)
        .padding(.horizontal, 20)
    }

    private var vigorBar: some View {
        VStack(alignment: .leading, spacing: 5) {
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    Capsule().fill(VUI.ink.opacity(0.08))
                    Capsule()
                        .fill(LinearGradient(colors: [VUI.orbA, VUI.orbB], startPoint: .leading, endPoint: .trailing))
                        .frame(width: max(8, geometry.size.width * CGFloat(companion.form.vigor) / 100))
                }
            }
            .frame(height: 8)
            Text("vigor \(companion.form.vigor)")
                .font(.system(size: 11))
                .foregroundStyle(VUI.dim)
        }
        .frame(maxWidth: 220)
        .animation(.easeOut(duration: 0.35), value: companion.form.vigor)
    }

    private func chip(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 11, weight: .medium))
            .foregroundStyle(VUI.dim)
            .padding(.horizontal, 9)
            .padding(.vertical, 4)
            .background(VUI.card, in: Capsule())
    }

    private func morphBanner(from stage: CompanionStage) -> some View {
        HStack(spacing: 8) {
            Image(systemName: "sparkles")
            Text("Morphed — \(stage.title) → \(companion.form.stage.title)")
                .font(.footnote.weight(.medium))
        }
        .foregroundStyle(VUI.ink.opacity(0.8))
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(VUI.card, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
        .padding(.horizontal, 20)
        .accessibilityIdentifier("companion-morph")
    }

    /// A read that failed is shown, not swallowed.
    private func trouble(_ error: String) -> some View {
        Text(error)
            .font(.footnote)
            .foregroundStyle(VUI.pink)
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(VUI.card, in: RoundedRectangle(cornerRadius: 13, style: .continuous))
            .padding(.horizontal, 20)
            .accessibilityIdentifier("companion-trouble")
    }

    /* ── the life ───────────────────────────────────────────────────── */

    private var tiles: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(companion.frames.isEmpty ? "No tiles yet" : "Tiles")
                .font(.footnote.weight(.medium))
                .foregroundStyle(VUI.dim)
                .padding(.horizontal, 20)

            if companion.frames.isEmpty {
                Text("Hold the orb and talk. Every moment lands here as its own tile, and the companion morphs as they add up.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 20)
            } else {
                LazyVGrid(columns: columns, spacing: 12) {
                    ForEach(companion.newestFirst) { frame in
                        Button { inspected = frame } label: { FrameTileView(frame: frame) }
                            .buttonStyle(.plain)
                            .accessibilityIdentifier("companion-tile-\(frame.seq)")
                    }
                }
                .padding(.horizontal, 20)
                .animation(.spring(response: 0.45, dampingFraction: 0.8), value: companion.frames.count)
            }
        }
    }

    private var ledger: some View {
        VStack(alignment: .leading, spacing: 4) {
            if let stats {
                Text("\(stats.tiles) tiles · \(stats.bytes) bytes on this phone · verified on read")
            }
            Text(companion.streamId)
                .lineLimit(1)
                .truncationMode(.middle)
        }
        .font(.system(size: 11, design: .monospaced))
        .foregroundStyle(VUI.dim)
        .padding(.horizontal, 20)
        .accessibilityIdentifier("companion-ledger")
    }
}

/// One frame, one tile.
struct FrameTileView: View {
    let frame: CompanionFrame

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 5) {
                Image(systemName: frame.kind.glyph)
                    .font(.system(size: 11, weight: .semibold))
                Text(frame.kind.label)
                    .font(.system(size: 11, weight: .semibold))
                Spacer(minLength: 0)
                Text("\(frame.seq)")
                    .font(.system(size: 10, design: .monospaced))
                    .foregroundStyle(VUI.dim)
            }
            .foregroundStyle(tint)

            Text(snippet)
                .font(.system(size: 11))
                .foregroundStyle(VUI.ink.opacity(0.75))
                .lineLimit(3)
                .frame(maxWidth: .infinity, alignment: .leading)

            Spacer(minLength: 0)

            HStack(spacing: 4) {
                Text(FrameTileView.clock(frame.utc))
                Spacer(minLength: 0)
                Text(frame.frameHash.prefix(8))
            }
            .font(.system(size: 9, design: .monospaced))
            .foregroundStyle(VUI.dim)
        }
        .padding(10)
        .frame(height: 104)
        .background(VUI.card, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .strokeBorder(tint.opacity(0.22), lineWidth: 1)
        }
        .transition(.scale.combined(with: .opacity))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(frame.kind.label), tile \(frame.seq). \(snippet)")
    }

    /// What this moment says, in words a person reads.
    ///
    /// A raw 24-byte stamp is the correct thing to *store* and the wrong thing
    /// to show: on a tile this size it wraps to three lines and tells you
    /// nothing you did not already know from the ordering.
    private var snippet: String {
        if let text = frame.payload["text"]?.stringValue, !text.isEmpty { return text }
        if let card = frame.payload["card"]?.stringValue { return card }
        if let engine = frame.payload["engine"]?.stringValue { return "brainstem \(engine)" }
        return FrameTileView.clock(frame.utc)
    }

    /// `18:43` — the part of a stamp a person can use.
    static func clock(_ utc: String) -> String {
        guard let date = UTCStamp.date(utc) else { return utc }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }

    private var tint: Color {
        switch frame.kind {
        case .woke: VUI.orbA
        case .heard: VUI.dashes[1]
        case .spoke: VUI.dashes[2]
        case .met: VUI.dashes[0]
        case .forged: VUI.orbB
        case .stalled: VUI.pink
        }
    }
}

/// The tile, opened: every field, because a tile you cannot read is a tile you
/// have to take on faith.
struct FrameTileDetail: View {
    let frame: CompanionFrame
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    row("kind", frame.kind.rawValue)
                    row("seq", "\(frame.seq)")
                    row("utc", frame.utc)
                    row("payload", Canonical.string(frame.payload))
                    row("payload_hash (particle)", frame.payloadHash)
                    row("frame_hash (wave · tile name)", frame.frameHash)
                    row("prev", frame.prev ?? "null")
                    row("verified", (try? frame.verify()) != nil ? "yes — recomputed just now" : "NO")
                }
                .padding(20)
            }
            .background(VUI.background.ignoresSafeArea())
            .navigationTitle("Tile \(frame.seq)")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    private func row(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(label)
                .font(.system(size: 11, weight: .medium))
                .foregroundStyle(VUI.dim)
            Text(value)
                .font(.system(size: 12, design: .monospaced))
                .foregroundStyle(VUI.ink)
                .textSelection(.enabled)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
