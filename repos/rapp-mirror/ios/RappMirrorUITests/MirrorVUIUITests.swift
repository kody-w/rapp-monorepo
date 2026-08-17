import XCTest

/// The VUI, driven the way a person drives it.
///
/// These tests are deliberately *not* unit tests. `Plain` already has unit
/// coverage; what unit tests cannot tell you is whether the stripped text ever
/// reaches the screen, whether the orb is really the home screen, or whether a
/// tapped portal produces an answer from the live brainstem. That only shows up
/// when you run the app and look — so this looks, on every build, automatically.
///
/// The brainstem-dependent tests skip honestly when nothing is listening on
/// 7071, and say so. They never pass by pretending the check happened.
final class MirrorVUIUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    /* ── the orb is the product ─────────────────────────────────────── */

    /// The main interface is the voice. Not a list, not a gallery — the orb,
    /// on screen, first thing, with no navigation to get to it.
    @MainActor
    func testTheOrbIsTheHomeScreen() throws {
        let app = launch()

        XCTAssertTrue(
            app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 20),
            "the orb must be the first thing on screen — the interface is the voice"
        )
        XCTAssertTrue(
            app.staticTexts["prompt"].exists,
            "the mirror must open by asking something, not by showing a menu"
        )
        XCTAssertEqual(
            app.tables.count + app.collectionViews.count, 0,
            "the home screen must not be a list or a gallery"
        )
    }

    /// Cards live *behind* the orb. Reaching them must never displace it.
    @MainActor
    func testCardsLiveBehindTheOrbNotInFrontOfIt() throws {
        let app = launch()
        XCTAssertTrue(app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 20))

        let cards = app.buttons["open-cards"]
        XCTAssertTrue(cards.exists, "there must be a way through to the cards")
        cards.tap()

        // The sheet is a sheet: dismissing it returns you to the orb.
        let sheetAppeared = app.buttons["close-cards"].waitForExistence(timeout: 8)
            || app.staticTexts["Agent cards"].waitForExistence(timeout: 2)
        XCTAssertTrue(sheetAppeared, "the cards sheet did not open")

        if app.buttons["close-cards"].exists {
            app.buttons["close-cards"].tap()
        } else {
            app.swipeDown(velocity: .fast)
        }

        XCTAssertTrue(
            app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 10),
            "the orb must still be the home screen after visiting the cards"
        )
    }

    /* ── the live loop ──────────────────────────────────────────────── */

    /// The mirror says what it actually found. If the brainstem is up, the
    /// header must say so rather than sitting on "reaching for…" forever.
    @MainActor
    func testTheMirrorReportsTheBrainstemItActuallyReached() throws {
        try requireBrainstem()
        let app = launch()

        // Queried across every element type: the header is one combined
        // accessibility element, and SwiftUI is free to pick its own trait.
        let state = app.descendants(matching: .any)["engine-state"].firstMatch
        XCTAssertTrue(state.waitForExistence(timeout: 20), "the header never rendered")

        let settled = expectation(description: "engine state settles")
        let poll = pollUntil(timeout: 25) {
            let label = state.label
            return !label.contains("reaching for")
        } then: { settled.fulfill() }
        wait(for: [settled], timeout: 30)
        poll.invalidate()

        let label = state.label
        XCTAssertFalse(
            label.localizedCaseInsensitiveContains("no brainstem"),
            "the brainstem answered /health but the mirror reported: \(label)"
        )
        XCTAssertTrue(
            label.localizedCaseInsensitiveContains("agents"),
            "a connected mirror names the engine and counts its agents; got: \(label)"
        )
    }

    /// Tap a portal, get a real answer — and the caption must be plain prose.
    /// This is the regression guard for markdown leaking into a glanceable UI.
    @MainActor
    func testAPortalAnswerIsPlainProseNotMarkdown() throws {
        try requireBrainstem()
        let app = launch()

        let portal = app.buttons["portal-What can you do"]
        XCTAssertTrue(portal.waitForExistence(timeout: 20), "the opening portals never appeared")
        portal.tap()

        let transcript = app.staticTexts["transcript"]
        XCTAssertTrue(transcript.waitForExistence(timeout: 10), "the tap was not echoed back")

        // The echo is the question; wait for it to become the answer.
        let answered = expectation(description: "the brainstem answers")
        let poll = pollUntil(timeout: 90) {
            let text = transcript.label
            return !text.isEmpty && text != "What can you do"
        } then: { answered.fulfill() }
        wait(for: [answered], timeout: 95)
        poll.invalidate()

        let said = transcript.label
        if app.staticTexts["notice"].exists {
            XCTFail("the mirror reported a problem: \(app.staticTexts["notice"].label)")
        }
        XCTAssertNotEqual(said, "What can you do", "no answer arrived within 90s")

        for marker in ["**", "###", "```", "~~"] {
            XCTAssertFalse(
                said.contains(marker),
                "markdown '\(marker)' leaked into the caption: \(said)"
            )
        }
        XCTAssertFalse(
            said.hasPrefix("- ") || said.hasPrefix("* "),
            "a raw bullet marker leaked into the caption: \(said)"
        )

        // Keep the screen that was judged. When this test fails, the picture is
        // the fastest explanation of why.
        let shot = XCTAttachment(screenshot: app.screenshot())
        shot.name = "vui-answered"
        shot.lifetime = .keepAlways
        add(shot)
    }

    /* ── hold to talk ───────────────────────────────────────────────── */

    /// Holding the orb is the whole product. It must either start listening or
    /// say why it cannot — a hold that is silently swallowed is the worst
    /// possible failure in a voice interface, because there is nothing to read.
    ///
    /// The state under test only exists *while* the finger is down, so the
    /// press runs on another queue and the assertions watch it happen.
    @MainActor
    func testHoldingTheOrbEitherListensOrExplainsItself() throws {
        let app = launch()
        let orb = app.descendants(matching: .any)["orb"].firstMatch
        XCTAssertTrue(orb.waitForExistence(timeout: 25), "the orb never appeared")

        orb.press(forDuration: 2.5)

        let notice = app.staticTexts["notice"]
        let answered = notice.waitForExistence(timeout: 8)

        let shot = XCTAttachment(screenshot: app.screenshot())
        shot.name = answered ? "orb-answered-the-hold" : "orb-swallowed-the-hold"
        shot.lifetime = .keepAlways
        add(shot)

        if answered { print("HOLD-DIAGNOSTIC: \(notice.label)") }
        XCTAssertTrue(
            answered,
            "holding the orb did nothing and said nothing — a voice interface "
                + "must never swallow a hold"
        )
        XCTAssertFalse(notice.label.isEmpty, "the mirror responded with an empty message")
    }

    /* ── trading a card ─────────────────────────────────────────────── */

    /// A card minted by the **desktop** mirror, pasted verbatim.
    ///
    /// This is the interop fixture: if the two encoders ever drift, this URL
    /// stops decoding and this test says so. Regenerate with
    /// `curl -X POST 127.0.0.1:8474/share -d '{"spec":…}'`.
    private static let desktopMintedCard =
        "rapp://agent?v=1&n=tideclock&d=lcyxjsIwEATQXxlN7S_IB1Bdd3RRChNv8ArjjZKNuAjx"
        + "74hAgRDNlaN5M1dWNnRN0hfrTwzs2XD_lv2jT49eSpmx2gLPgip_jqzHjIfDYBMiDhL7zED9"
        + "H5_ZtC1_zE5Yxo1vyOOhCAN3Nj0_4lnSa9SFljut6cs5A_dZMOg0O6wK4uAyodplW_3GFeoY"
        + "S9Ra1hd2PUtArAnZLihWj1iqa4E6uy5wZNN2tzs"

    /// Scanning a card must show you *that* card.
    ///
    /// The first version of this decoded the URL correctly and then presented
    /// the sample gallery, so trading an agent showed you somebody else's.
    @MainActor
    func testAScannedCardIsTheCardYouAreShown() throws {
        let app = launch()
        XCTAssertTrue(app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 25))

        guard let url = URL(string: Self.desktopMintedCard) else {
            return XCTFail("the fixture is not a URL")
        }
        XCUIDevice.shared.system.open(url)

        let title = app.staticTexts["arrived-title"]
        XCTAssertTrue(
            title.waitForExistence(timeout: 15),
            "a scanned card did not surface — check onOpenURL and the sheet item"
        )
        XCTAssertEqual(title.label, "tideclock", "the wrong card was presented")

        // A move that exists only on the scanned agent: proof the spec was
        // decoded rather than a placeholder being drawn.
        XCTAssertTrue(
            app.staticTexts["Look up the tide table"].waitForExistence(timeout: 5),
            "the card is not carrying the agent that was scanned"
        )

        let front = XCTAttachment(screenshot: app.screenshot())
        front.name = "scanned-card-front"
        front.lifetime = .keepAlways
        add(front)
    }

    /// The whole card must be on the card. It used to overflow its own edge,
    /// clipping the footer and printing it onto the page underneath.
    @MainActor
    func testTheWholeCardFitsOnTheCard() throws {
        let app = launch()
        XCTAssertTrue(app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 25))
        guard let url = URL(string: Self.desktopMintedCard) else {
            return XCTFail("the fixture is not a URL")
        }
        XCUIDevice.shared.system.open(url)

        let card = app.descendants(matching: .any)["arrived-card"].firstMatch
        XCTAssertTrue(card.waitForExistence(timeout: 15), "the arrived card never appeared")

        // The footer is the last thing printed: if it is visible and inside the
        // card's own frame, nothing above it was pushed off.
        let footer = app.staticTexts["Illus. Riso Collective"]
        XCTAssertTrue(footer.waitForExistence(timeout: 5), "the card footer was clipped away")
        XCTAssertTrue(
            card.frame.contains(footer.frame),
            "the footer is printed outside the card: card \(card.frame), footer \(footer.frame)"
        )

        let lastMove = app.staticTexts["Say it plainly"]
        XCTAssertTrue(lastMove.exists, "the last move was clipped off the card")
        XCTAssertTrue(
            card.frame.contains(lastMove.frame),
            "a move is printed outside the card"
        )
    }

    /// The back carries the QR that makes trading work.
    @MainActor
    func testFlippingTheCardShowsTheQRThatTradesIt() throws {
        let app = launch()
        XCTAssertTrue(app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 25))
        guard let url = URL(string: Self.desktopMintedCard) else {
            return XCTFail("the fixture is not a URL")
        }
        XCUIDevice.shared.system.open(url)

        let card = app.descendants(matching: .any)["arrived-card"].firstMatch
        XCTAssertTrue(card.waitForExistence(timeout: 15))
        card.tap()

        let qr = app.descendants(matching: .any)["trading-card-qr"].firstMatch
        XCTAssertTrue(qr.waitForExistence(timeout: 8), "the card did not flip to its QR back")
        XCTAssertTrue(
            card.frame.contains(qr.frame),
            "the QR is printed outside the card: card \(card.frame), qr \(qr.frame)"
        )

        let back = XCTAttachment(screenshot: app.screenshot())
        back.name = "scanned-card-back"
        back.lifetime = .keepAlways
        add(back)
    }

    /* ── helpers ────────────────────────────────────────────────────── */
    @MainActor
    private func launch() -> XCUIApplication {
        let app = XCUIApplication()
        app.launchArguments += ["-AppleLanguages", "(en)"]
        app.launch()
        return app
    }

    /// Polls a condition off the main run loop so XCTest predicates don't have
    /// to guess at element identity across re-renders.
    private func pollUntil(
        timeout: TimeInterval,
        every interval: TimeInterval = 0.5,
        condition: @escaping () -> Bool,
        then done: @escaping () -> Void
    ) -> Timer {
        let deadline = Date().addingTimeInterval(timeout)
        var finished = false
        let timer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { t in
            guard !finished else { return }
            if condition() || Date() > deadline {
                finished = true
                t.invalidate()
                done()
            }
        }
        RunLoop.current.add(timer, forMode: .common)
        return timer
    }

    /// A real probe — not a flag. If this ever returns without throwing while
    /// nothing is listening, the skip is broken and the tests below are lying.
    private func requireBrainstem() throws {
        guard let url = URL(string: "http://127.0.0.1:7071/health") else { return }
        var request = URLRequest(url: url)
        request.timeoutInterval = 4

        var healthy = false
        var reason = "no response"
        let waited = DispatchSemaphore(value: 0)
        URLSession.shared.dataTask(with: request) { data, response, error in
            defer { waited.signal() }
            if let error { reason = error.localizedDescription; return }
            guard let http = response as? HTTPURLResponse else { return }
            guard http.statusCode == 200 else { reason = "HTTP \(http.statusCode)"; return }
            guard let data, let body = String(data: data, encoding: .utf8) else { return }
            healthy = body.contains("\"agents\"")
            if !healthy { reason = "unexpected /health body" }
        }.resume()
        _ = waited.wait(timeout: .now() + 8)

        if !healthy {
            throw XCTSkip("no brainstem on 127.0.0.1:7071 (\(reason)) — live VUI checks not run")
        }
    }
}
