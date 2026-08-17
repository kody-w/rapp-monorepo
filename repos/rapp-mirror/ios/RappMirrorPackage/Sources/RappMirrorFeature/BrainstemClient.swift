import Foundation

/// What the brainstem says about itself.
public struct BrainstemHealth: Equatable, Sendable {
    public let ok: Bool
    public let version: String?
    public let model: String?
    public let agents: [String]
    /// Why it is not ok — never an empty "connecting…".
    public let error: String?

    public init(ok: Bool, version: String? = nil, model: String? = nil, agents: [String] = [], error: String? = nil) {
        self.ok = ok
        self.version = version
        self.model = model
        self.agents = agents
        self.error = error
    }
}

public struct ChatResult: Equatable, Sendable {
    public let ok: Bool
    public let response: String?
    public let model: String?
    public let error: String?

    public init(ok: Bool, response: String? = nil, model: String? = nil, error: String? = nil) {
        self.ok = ok
        self.response = response
        self.model = model
        self.error = error
    }
}

public struct ChatTurn: Equatable, Sendable, Codable {
    public let role: String
    public let content: String

    public init(role: String, content: String) {
        self.role = role
        self.content = content
    }
}

/// Talks to a RAPP brainstem over the network.
///
/// The desktop mirror reaches a brainstem on loopback; on iPhone the brainstem
/// lives on another machine, so the URL is user-configured. Every failure comes
/// back with a real reason attached — the mirror never reports a success it did
/// not observe.
public actor BrainstemClient {
    public private(set) var baseURL: URL
    private let session: URLSession
    private let timeout: TimeInterval

    public init(baseURL: URL, session: URLSession = .shared, timeout: TimeInterval = 120) {
        self.baseURL = baseURL
        self.session = session
        self.timeout = timeout
    }

    public func setBaseURL(_ url: URL) {
        baseURL = url
    }

    public func health() async -> BrainstemHealth {
        do {
            var request = URLRequest(url: baseURL.appendingPathComponent("health"))
            request.timeoutInterval = 10
            let (data, response) = try await session.data(for: request)

            guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
                let code = (response as? HTTPURLResponse)?.statusCode ?? -1
                return BrainstemHealth(ok: false, error: "brainstem answered HTTP \(code)")
            }
            guard let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                return BrainstemHealth(ok: false, error: "brainstem returned a non-JSON body")
            }
            return BrainstemHealth(
                ok: true,
                version: object["version"] as? String,
                model: object["model"] as? String,
                agents: object["agents"] as? [String] ?? []
            )
        } catch {
            return BrainstemHealth(ok: false, error: reason(error))
        }
    }

    public func chat(_ text: String, history: [ChatTurn] = [], sessionId: String = "ios-mirror") async -> ChatResult {
        do {
            var request = URLRequest(url: baseURL.appendingPathComponent("chat"))
            request.httpMethod = "POST"
            request.timeoutInterval = timeout
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try JSONSerialization.data(withJSONObject: [
                "user_input": text,
                "conversation_history": history.map { ["role": $0.role, "content": $0.content] },
                "session_id": sessionId,
            ])

            let (data, response) = try await session.data(for: request)
            guard let object = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
                let code = (response as? HTTPURLResponse)?.statusCode ?? -1
                let snippet = String(decoding: data.prefix(200), as: UTF8.self)
                return ChatResult(ok: false, error: "brainstem returned a non-JSON body (HTTP \(code)): \(snippet)")
            }
            let http = response as? HTTPURLResponse
            let status = http?.statusCode ?? -1
            if let message = object["error"] as? String, !message.isEmpty {
                return ChatResult(ok: false, error: message)
            }
            guard (200..<300).contains(status) else {
                return ChatResult(ok: false, error: "brainstem answered HTTP \(status)")
            }
            guard let reply = object["response"] as? String else {
                return ChatResult(ok: false, error: "brainstem returned no response field")
            }
            return ChatResult(ok: true, response: reply, model: object["model"] as? String)
        } catch {
            return ChatResult(ok: false, error: reason(error))
        }
    }

    /// Turn a URLError into something a human can act on.
    private func reason(_ error: Error) -> String {
        guard let urlError = error as? URLError else { return error.localizedDescription }
        switch urlError.code {
        case .cannotConnectToHost, .cannotFindHost:
            return "no brainstem answering at \(baseURL.absoluteString)"
        case .timedOut:
            return "the brainstem did not answer in time"
        case .notConnectedToInternet, .networkConnectionLost:
            return "this device is off the network the brainstem is on"
        default:
            return urlError.localizedDescription
        }
    }
}
