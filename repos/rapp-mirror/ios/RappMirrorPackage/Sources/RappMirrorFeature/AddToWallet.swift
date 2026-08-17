import SwiftUI
#if canImport(PassKit) && canImport(UIKit)
import PassKit
import UIKit
#endif

public struct AddToWalletButton: View {
    public let signedPassData: Data?
    public let label: String
    @State private var message: String?
    #if canImport(PassKit) && canImport(UIKit)
    @State private var passBundle: PassBundle?
    #endif

    public init(signedPassData: Data?, label: String = "Add to Apple Wallet") {
        self.signedPassData = signedPassData
        self.label = label
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button(action: add) {
                Label(label, systemImage: "wallet.pass")
                    .font(.callout.weight(.semibold))
            }
            .buttonStyle(.borderedProminent)
            .disabled(signedPassData == nil)
            .accessibilityLabel(label)
            .accessibilityHint(signedPassData == nil ? "A signed pkpass is required before Wallet can install it." : "Opens Apple Wallet to confirm adding this pass.")
            .accessibilityIdentifier("add-to-wallet-button")

            Text(message ?? missingMessage)
                .font(.caption)
                .foregroundStyle(signedPassData == nil ? .secondary : .primary)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityIdentifier("wallet-status")
        }
        #if canImport(PassKit) && canImport(UIKit)
        .sheet(item: $passBundle) { bundle in
            AddPassesSheet(pass: bundle.pass)
        }
        #endif
    }

    private var missingMessage: String {
        "Wallet requires a signed .pkpass. Create an Apple Pass Type ID certificate, sign the pass bundle, then provide that signed pass here; this app will not pretend an unsigned pass was installed."
    }

    private func add() {
        guard let signedPassData else {
            message = missingMessage
            return
        }
        #if canImport(PassKit) && canImport(UIKit)
        do {
            let pass = try PKPass(data: signedPassData)
            guard PKAddPassesViewController.canAddPasses() else {
                message = "This device cannot add Wallet passes right now. No pass was installed."
                return
            }
            passBundle = PassBundle(pass: pass)
            message = "Opening Apple Wallet confirmation."
        } catch {
            message = "That pass is not a valid signed .pkpass: \(error.localizedDescription)"
        }
        #else
        message = "Apple Wallet pass installation is available only on iOS with PassKit."
        #endif
    }
}

#if canImport(PassKit) && canImport(UIKit)
private struct PassBundle: Identifiable {
    let id = UUID()
    let pass: PKPass
}

private struct AddPassesSheet: UIViewControllerRepresentable {
    let pass: PKPass

    func makeUIViewController(context: Context) -> UIViewController {
        PKAddPassesViewController(pass: pass) ?? UIViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
#endif
