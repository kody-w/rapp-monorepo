import CoreImage
import CoreImage.CIFilterBuiltins
import Testing
@testable import RappMirrorFeature

@Suite("Agent share URLs interoperate with desktop")
struct ShareURLTests {
    @Test("round-trip encodes and decodes a spec")
    func roundTrip() throws {
        let encoded = ShareURL.encodeShareUrl(Self.spec)
        #expect(encoded.ok)
        let url = try #require(encoded.url)
        let decoded = ShareURL.decodeShareUrl(url)
        #expect(decoded.ok)
        #expect(decoded.spec == Self.spec)
    }

    @Test("a real TypeScript-produced URL fixture decodes correctly")
    func typescriptFixtureDecodes() throws {
        let url = "rapp://agent?v=1&n=greeter&d=RY4xC8IwEEb_yvHNWVy7Obk46eAQMoR6poGYlOQolOJ_9xpRx_f43nEbMgaEyixcYTAqnT50DJxFlfyV0v1LjTwtsUUpu46qr36liVMq1PyD06q6YbAW59iEs-KFR44La5n9k-GMVTX35S-GcwZz7_rI4DYVkkL9yf2m1JgDzMG51xs"
        let decoded = ShareURL.decodeShareUrl(url)
        #expect(decoded.ok)
        let spec = try #require(decoded.spec)
        #expect(spec.name == "greeter")
        #expect(spec.className == "GreeterAgent")
        #expect(spec.title == "Greeter")
        #expect(spec.description == "Greets a visitor")
        #expect(spec.intent == "Say hello safely")
        #expect(spec.steps == [ForgeStep(title: "Listen", detail: "Receive a name"), ForgeStep(title: "Reply", detail: "Say hello")])
        #expect(spec.parameters == [ForgeParameter(name: "name", description: "Who to greet", type: "string", required: true)])
    }

    @Test("hostile or damaged URLs fail without throwing")
    func damagedFails() {
        let notRapp = ShareURL.decodeShareUrl("https://example.com")
        #expect(!notRapp.ok)
        let damaged = ShareURL.decodeShareUrl("rapp://agent?v=1&n=x&d=%%%")
        #expect(!damaged.ok)
    }

    @Test("invalid class names are rejected")
    func invalidClassNameRejected() {
        let spec = ForgeSpec(name: "bad", className: "9Bad", title: "Bad", description: "No", intent: "No")
        #expect(!ShareURL.encodeShareUrl(spec).ok)
    }

    @Test("QR generator returns an image for a real share URL")
    func qrImageExists() throws {
        let url = try #require(ShareURL.encodeShareUrl(Self.spec).url)
        #expect(QRCode.image(for: url) != nil)
    }

    /// The card back is only worth printing if a camera can read it.
    ///
    /// Checking the image is non-nil proves nothing: a QR can be generated,
    /// rendered, and be completely unscannable. The desktop encoder shipped
    /// exactly that bug at version 7 and up. So decode it for real.
    @Test("a rendered QR scans back to the identical URL")
    func qrRoundTripsThroughARealScanner() throws {
        let url = try #require(ShareURL.encodeShareUrl(Self.spec).url)
        let image = try #require(QRCode.image(for: url))
        // Scale up the way the card does; a 1px-per-module image is not what a
        // camera ever sees.
        let scaled = image.transformed(by: CGAffineTransform(scaleX: 12, y: 12))

        let detector = try #require(
            CIDetector(
                ofType: CIDetectorTypeQRCode,
                context: nil,
                options: [CIDetectorAccuracy: CIDetectorAccuracyHigh]
            )
        )
        let found = detector.features(in: scaled).compactMap { $0 as? CIQRCodeFeature }
        let message = try #require(found.first?.messageString, "the rendered QR could not be scanned")
        #expect(message == url, "a scan of the card returns a different agent than the card carries")

        // And the scanned text must decode back into the same agent.
        let decoded = ShareURL.decodeShareUrl(message)
        #expect(decoded.ok)
        #expect(decoded.spec?.className == Self.spec.className)
    }

    /// A long agent still has to survive the whole loop, not just a short one.
    @Test("a card at the size limit still scans")
    func longSpecStillScans() throws {
        let long = ForgeSpec(
            name: "tideclock",
            className: "TideclockAgent",
            title: "Tide Clock",
            description: String(repeating: "tide ", count: 20),
            intent: "Report the next high tide for a named beach",
            steps: [
                ForgeStep(title: "Look up the tide table", detail: "For the named beach"),
                ForgeStep(title: "Find the next high tide", detail: "The first one after now"),
                ForgeStep(title: "Say it plainly", detail: "The time, and how long until it"),
            ],
            parameters: [ForgeParameter(name: "beach", description: "Beach name", type: "string", required: true)]
        )
        let url = try #require(ShareURL.encodeShareUrl(long).url)
        let image = try #require(QRCode.image(for: url))
        let scaled = image.transformed(by: CGAffineTransform(scaleX: 12, y: 12))
        let detector = try #require(
            CIDetector(ofType: CIDetectorTypeQRCode, context: nil, options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])
        )
        let message = detector.features(in: scaled)
            .compactMap { ($0 as? CIQRCodeFeature)?.messageString }
            .first
        #expect(message == url, "a full-size agent card does not scan")
    }

    static let spec = ForgeSpec(
        name: "greeter",
        className: "GreeterAgent",
        title: "Greeter",
        description: "Greets a visitor",
        intent: "Say hello safely",
        steps: [ForgeStep(title: "Listen", detail: "Receive a name"), ForgeStep(title: "Reply", detail: "Say hello")],
        parameters: [ForgeParameter(name: "name", description: "Who to greet", type: "string", required: true)]
    )
}
