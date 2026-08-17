import SwiftUI

/// The cards, behind the voice.
///
/// Agent cards matter, but they are not the interface — the orb is. This is
/// where they live: one swipe behind the mirror, reachable from the header, or
/// pushed to the front when a card arrives by scan, tap or AirDrop.
struct AgentCardsSheet: View {
    /// The card that was just scanned or opened, if any. It leads, because
    /// being shown somebody else's cards after scanning one is a non-answer.
    var arrived: GalleryCard?

    @Environment(\.dismiss) private var dismiss
    @State private var selected: GalleryCard?
    private let cards = GalleryCard.samples

    /// Cards are drawn at their design size and scaled, never cropped: a card
    /// with its title sliced off is not a card. The size comes from the card
    /// itself so this can never drift out of step with it again.
    private static let design = TradingCardView.face
    private static let shelf: CGFloat = 268

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    if let arrived {
                        arrivedSection(arrived)
                        Divider().padding(.horizontal, 20)
                    }

                    Text(consentCopy)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .padding(.horizontal, 20)

                    shelfRow

                    AddToWalletButton(signedPassData: nil)
                        .padding(.horizontal, 20)
                }
                .padding(.vertical, 12)
            }
            .background(VUI.background.ignoresSafeArea())
            .navigationTitle(arrived == nil ? "Agent cards" : "A card arrived")
            #if os(iOS)
            .navigationBarTitleDisplayMode(.inline)
            #endif
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Done") { dismiss() }
                        .accessibilityIdentifier("close-cards")
                }
            }
            .sheet(item: $selected) { item in
                NavigationStack {
                    ScrollView {
                        card(item, width: Self.shelf)
                            .padding()
                    }
                    .background(VUI.background.ignoresSafeArea())
                    .navigationTitle(item.card.title)
                    #if os(iOS)
                    .navigationBarTitleDisplayMode(.inline)
                    #endif
                }
            }
        }
    }

    private var consentCopy: String {
        arrived == nil
            ? "A card is a preview for consent. A scanned or tapped link decodes into a review card — nothing installs automatically."
            : "This card was decoded on your phone. Nothing has been installed, and nothing will be until you say so."
    }

    private func arrivedSection(_ item: GalleryCard) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(item.card.title)
                .font(.title3.weight(.semibold))
                .padding(.horizontal, 20)
                .accessibilityIdentifier("arrived-title")

            Text(item.spec.description)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .padding(.horizontal, 20)

            card(item, width: Self.shelf)
                .frame(maxWidth: .infinity, alignment: .center)
                .accessibilityIdentifier("arrived-card")
        }
    }

    private var shelfRow: some View {
        VStack(alignment: .leading, spacing: 8) {
            if arrived != nil {
                Text("Already on this phone")
                    .font(.footnote.weight(.medium))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 20)
            }
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(alignment: .top, spacing: 18) {
                    ForEach(cards) { item in
                        Button { selected = item } label: {
                            card(item, width: Self.shelf)
                        }
                        .buttonStyle(.plain)
                        .accessibilityIdentifier("card-\(item.card.title)")
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 6)
            }
        }
    }

    /// Scale to fit, rather than `.frame` which would crop the artwork.
    private func card(_ item: GalleryCard, width: CGFloat) -> some View {
        let scale = width / Self.design.width
        return TradingCardView(card: item.card, shareURL: item.shareURL)
            .scaleEffect(scale)
            .frame(width: width, height: Self.design.height * scale)
    }
}
