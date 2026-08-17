import AVFoundation
import Foundation
import Speech

/// Voice, on this device only.
///
/// The desktop mirror transcribes with a local whisper.cpp and speaks with a
/// local VibeVoice; nothing about a phone should be looser. So hearing uses
/// `SFSpeechRecognizer` pinned to **on-device** recognition, and speaking uses
/// the system synthesiser. If on-device recognition is not available for the
/// user's locale, the mirror says so instead of quietly shipping audio to
/// Apple's servers.
@MainActor
@Observable
public final class Voice {
    public enum HearingState: Equatable, Sendable {
        case idle
        case listening
        /// Refused, with the reason — never a silent failure.
        case unavailable(String)
    }

    public private(set) var hearing: HearingState = .idle
    /// What has been heard so far in this hold, updated live.
    public private(set) var partial: String = ""

    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    private let engine = AVAudioEngine()
    private let synthesizer = AVSpeechSynthesizer()
    private var request: SFSpeechAudioBufferRecognitionRequest?
    private var task: SFSpeechRecognitionTask?

    public init() {}

    /// Ask once, up front, so the first hold is not spent on a permission sheet.
    ///
    /// `nonisolated` on purpose: TCC delivers both callbacks on its own queue,
    /// and inheriting this type's `@MainActor` isolation makes Swift 6 trap the
    /// moment the system replies.
    nonisolated public func requestPermission() async {
        _ = await withCheckedContinuation { (continuation: CheckedContinuation<Bool, Never>) in
            SFSpeechRecognizer.requestAuthorization { status in
                continuation.resume(returning: status == .authorized)
            }
        }
        #if os(iOS)
        _ = await withCheckedContinuation { (continuation: CheckedContinuation<Bool, Never>) in
            AVAudioApplication.requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
        #endif
    }

    /// Begin a push-to-talk hold.
    public func startListening() {
        guard hearing != .listening else { return }
        partial = ""

        guard let recognizer, recognizer.isAvailable else {
            hearing = .unavailable("speech recognition is unavailable on this device")
            return
        }
        guard SFSpeechRecognizer.authorizationStatus() == .authorized else {
            hearing = .unavailable("the mirror has not been allowed to listen — enable Speech Recognition in Settings")
            return
        }

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.shouldReportPartialResults = true
        // The whole point: audio must not leave the device.
        request.requiresOnDeviceRecognition = true
        guard recognizer.supportsOnDeviceRecognition else {
            hearing = .unavailable("on-device speech is not installed for this language — the mirror will not send your voice away")
            return
        }
        self.request = request

        do {
            // The audio session is an iOS concept; the package also builds for
            // macOS so the pure-logic suites can run without a simulator.
            #if os(iOS)
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, mode: .measurement, options: [.duckOthers, .defaultToSpeaker])
            try session.setActive(true, options: .notifyOthersOnDeactivation)
            #endif

            let input = engine.inputNode
            let format = input.outputFormat(forBus: 0)
            input.removeTap(onBus: 0)
            Voice.pipe(input, format: format, into: request)
            engine.prepare()
            try engine.start()
        } catch {
            hearing = .unavailable("the microphone could not start: \(error.localizedDescription)")
            return
        }

        task = Voice.transcribe(with: recognizer, request: request) { [weak self] heard in
            Task { @MainActor in self?.partial = heard }
        }
        hearing = .listening
    }

    /// Both of these exist to strip actor isolation off a callback.
    ///
    /// A closure written inside this `@MainActor` type inherits its isolation,
    /// and neither of these SDK callbacks is `@Sendable` — so Swift 6 inserts an
    /// executor check that traps the instant the framework calls back on its own
    /// thread. The audio tap runs on a realtime thread and the recogniser on its
    /// own queue, so both took the app down on every single hold. Declaring the
    /// wrappers `nonisolated` means the closures start life with no isolation to
    /// violate.
    private nonisolated static func pipe(
        _ input: AVAudioInputNode,
        format: AVAudioFormat,
        into request: SFSpeechAudioBufferRecognitionRequest
    ) {
        input.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            request.append(buffer)
        }
    }

    private nonisolated static func transcribe(
        with recognizer: SFSpeechRecognizer,
        request: SFSpeechAudioBufferRecognitionRequest,
        onHeard: @escaping @Sendable (String) -> Void
    ) -> SFSpeechRecognitionTask {
        recognizer.recognitionTask(with: request) { result, _ in
            guard let result else { return }
            // Hand back a String: the result itself is not safe to carry across.
            onHeard(result.bestTranscription.formattedString)
        }
    }

    /// End the hold and return what was heard, trimmed.
    @discardableResult
    public func stopListening() -> String {
        engine.inputNode.removeTap(onBus: 0)
        if engine.isRunning { engine.stop() }
        request?.endAudio()
        task?.finish()
        request = nil
        task = nil
        if case .listening = hearing { hearing = .idle }
        return partial.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    public func speak(_ text: String) {
        guard !text.isEmpty else { return }
        hush()
        #if os(iOS)
        try? AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio, options: [.duckOthers])
        #endif
        let utterance = AVSpeechUtterance(string: text)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        utterance.voice = AVSpeechSynthesisVoice(language: "en-US")
        synthesizer.speak(utterance)
    }

    public func hush() {
        if synthesizer.isSpeaking { synthesizer.stopSpeaking(at: .immediate) }
    }

    public var isSpeaking: Bool { synthesizer.isSpeaking }
}
