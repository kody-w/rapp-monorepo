import XCTest

/// Does it survive its own launch?
///
/// Every crash this app has had so far happened in the first few seconds:
/// audio-session APIs that do not exist on the host platform, a missing
/// `NSSpeechRecognitionUsageDescription`, and a permission callback that
/// arrived off the main actor under Swift 6 strict concurrency. All three were
/// invisible to unit tests and obvious the instant the app was run. So run it.
final class RappMirrorUITests: XCTestCase {
    override func setUpWithError() throws {
        continueAfterFailure = false
    }

    /// The app must still be alive after the permission prompts have resolved.
    /// A TCC callback that traps takes the process down a beat *after* launch,
    /// so a bare `app.launch()` is not enough — this waits it out.
    @MainActor
    func testTheAppSurvivesLaunchAndThePermissionFlow() throws {
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(
            app.staticTexts["HOLD TO TALK"].waitForExistence(timeout: 25),
            "the app did not draw its interface — check the device log for a crash"
        )

        // Speech and microphone authorisation land asynchronously. Sit through
        // the window in which an isolation trap would fire.
        Thread.sleep(forTimeInterval: 6)

        XCTAssertEqual(
            app.state, .runningForeground,
            "the app died shortly after launch — most likely a permission callback"
        )
        XCTAssertTrue(
            app.staticTexts["HOLD TO TALK"].exists,
            "the interface disappeared after the permission flow"
        )
    }

    /// A blank screen with a live process is the failure mode that looks
    /// healthy. Assert there is actually something drawn.
    @MainActor
    func testTheInterfaceIsNotBlank() throws {
        let app = XCUIApplication()
        app.launch()

        XCTAssertTrue(app.staticTexts["prompt"].waitForExistence(timeout: 25))
        XCTAssertGreaterThan(
            app.staticTexts.count, 2,
            "the process is running but nothing was rendered"
        )
        XCTAssertGreaterThan(
            app.buttons.count, 0,
            "nothing on screen is touchable — the interface is inert"
        )
    }
}
