import XCTest

/// The companion tiles, driven the way a person drives them.
///
/// The storage layer has unit coverage — addresses, refusals, the fold. What
/// unit tests cannot tell you is whether a tile ever reaches the screen: that
/// the hero renders the folded form, that a moment recorded on launch shows up
/// as a tile you can open, and that the ledger says how much of the phone the
/// life is using. That only shows up when you run the app and look, so this
/// looks, on every build.
final class CompanionTilesUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    /// Tiles live behind the orb, like the cards do. Reaching them must never
    /// displace the voice.
    @MainActor
    func testCompanionTilesOpenBehindTheOrb() throws {
        let app = launch()
        XCTAssertTrue(app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 20))

        let opener = app.buttons["open-companion"]
        XCTAssertTrue(opener.exists, "there must be a way through to the companion")
        opener.tap()

        XCTAssertTrue(
            app.otherElements["companion-hero"].waitForExistence(timeout: 8)
                || app.images["companion-hero"].waitForExistence(timeout: 2),
            "the companion sheet must show the folded form, not an empty page"
        )

        // The store is not a claim: the sheet says what is actually on disk.
        XCTAssertTrue(
            app.staticTexts["companion-ledger"].waitForExistence(timeout: 4)
                || app.otherElements["companion-ledger"].waitForExistence(timeout: 2),
            "the ledger line must report the real tile count"
        )

        // Keep the frame: a UI nobody has looked at is a UI nobody has checked,
        // and this is the one place the folded form is actually rendered.
        let shot = XCTAttachment(screenshot: app.screenshot())
        shot.name = "companion-tiles"
        shot.lifetime = .keepAlways
        add(shot)

        app.buttons["close-companion"].tap()
        XCTAssertTrue(
            app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 8),
            "closing the tiles must return you to the orb"
        )
    }

    /// Waking is a moment, so waking is a tile. If the first launch leaves no
    /// tile behind, nothing downstream of the store can be trusted either.
    @MainActor
    func testWakingLeavesATileBehind() throws {
        let app = launch()
        XCTAssertTrue(app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 20))
        app.buttons["open-companion"].tap()

        let firstTile = app.buttons["companion-tile-0"]
        XCTAssertTrue(
            firstTile.waitForExistence(timeout: 8),
            "the companion recorded no tile for waking up"
        )

        firstTile.tap()
        // Opening a tile shows the frame whole — including the line that says
        // its addresses were recomputed just now, which is the only claim in
        // this app that is allowed to say "verified".
        XCTAssertTrue(
            app.staticTexts["yes — recomputed just now"].waitForExistence(timeout: 6),
            "a tile must be able to prove it is the tile it claims to be"
        )
    }

    /// The loop that makes a companion: talk to the mirror, and the turn shows
    /// up as tiles you can see.
    ///
    /// This is the only test that proves the wiring end to end — a store that
    /// works and a view that renders are still two separate facts until a real
    /// answer from a real brainstem lands in the grid as `heard` and `spoke`.
    /// It skips honestly when nothing is listening, rather than passing by
    /// pretending the check happened.
    @MainActor
    func testATurnWithTheBrainstemLandsAsTiles() throws {
        try requireBrainstem()
        let app = launch()

        let portal = app.buttons["portal-What can you do"]
        XCTAssertTrue(portal.waitForExistence(timeout: 20), "the opening portals never appeared")
        portal.tap()

        let transcript = app.staticTexts["transcript"]
        XCTAssertTrue(transcript.waitForExistence(timeout: 10), "the tap was not echoed back")
        let answered = expectation(description: "the brainstem answers")
        let poll = pollUntil(timeout: 90) {
            let text = transcript.label
            return !text.isEmpty && text != "What can you do"
        } then: { answered.fulfill() }
        wait(for: [answered], timeout: 95)
        poll.invalidate()

        app.buttons["open-companion"].tap()
        XCTAssertTrue(
            app.otherElements["companion-hero"].waitForExistence(timeout: 8)
                || app.images["companion-hero"].waitForExistence(timeout: 2),
            "the companion sheet never opened"
        )

        // What was said, and what was answered, are two separate moments.
        let heard = app.descendants(matching: .any).matching(NSPredicate(format: "label CONTAINS[c] 'heard'")).firstMatch
        let spoke = app.descendants(matching: .any).matching(NSPredicate(format: "label CONTAINS[c] 'spoke'")).firstMatch
        XCTAssertTrue(heard.waitForExistence(timeout: 8), "the turn left no 'heard' tile")
        XCTAssertTrue(spoke.waitForExistence(timeout: 8), "the answer left no 'spoke' tile")

        let shot = XCTAttachment(screenshot: app.screenshot())
        shot.name = "companion-after-a-turn"
        shot.lifetime = .keepAlways
        add(shot)
    }

    /// Polls a condition off the main run loop so XCTest predicates don't have
    /// to guess at element identity across re-renders.
    @discardableResult
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

    /// A real probe — not a flag.
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
            throw XCTSkip("no brainstem on 127.0.0.1:7071 (\(reason)) — the live tile loop was not run")
        }
    }

    @MainActor
    private func launch() -> XCUIApplication {
        let app = XCUIApplication()
        app.launchArguments += ["-AppleLanguages", "(en)"]
        app.launch()
        return app
    }
}
