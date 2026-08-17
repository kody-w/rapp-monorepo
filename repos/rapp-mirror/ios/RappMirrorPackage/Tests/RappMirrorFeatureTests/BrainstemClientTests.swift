import Foundation
import Testing
@testable import RappMirrorFeature

/// Answers every request from a script, so the suite never touches a network.
final class StubURLProtocol: URLProtocol, @unchecked Sendable {
    nonisolated(unsafe) static var handler: (@Sendable (URLRequest) throws -> (HTTPURLResponse, Data))?

    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }

    override func startLoading() {
        guard let handler = Self.handler else {
            client?.urlProtocol(self, didFailWithError: URLError(.badServerResponse))
            return
        }
        do {
            let (response, data) = try handler(request)
            client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
            client?.urlProtocol(self, didLoad: data)
            client?.urlProtocolDidFinishLoading(self)
        } catch {
            client?.urlProtocol(self, didFailWithError: error)
        }
    }

    override func stopLoading() {}
}

private func stubbedSession() -> URLSession {
    let config = URLSessionConfiguration.ephemeral
    config.protocolClasses = [StubURLProtocol.self]
    return URLSession(configuration: config)
}

private func reply(_ status: Int, _ body: String, url: URL) -> (HTTPURLResponse, Data) {
    (
        HTTPURLResponse(url: url, statusCode: status, httpVersion: nil, headerFields: nil)!,
        Data(body.utf8)
    )
}

@Suite("Brainstem client reports only what it observed", .serialized)
struct BrainstemClientTests {
    let base = URL(string: "http://127.0.0.1:7071")!

    @Test("health parses version, model and the agent list")
    func healthOK() async {
        StubURLProtocol.handler = { request in
            reply(200, #"{"status":"ok","version":"0.6.16","model":"claude-haiku-4.5","agents":["A","B"]}"#, url: request.url!)
        }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let health = await client.health()
        #expect(health.ok)
        #expect(health.version == "0.6.16")
        #expect(health.agents == ["A", "B"])
    }

    @Test("an HTTP error is never reported as ok, and carries its status")
    func healthHTTPError() async {
        StubURLProtocol.handler = { request in reply(500, "boom", url: request.url!) }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let health = await client.health()
        #expect(!health.ok)
        #expect(health.error?.contains("500") == true)
    }

    @Test("an HTML error page does not masquerade as a healthy brainstem")
    func healthNonJSON() async {
        StubURLProtocol.handler = { request in reply(200, "<html>nope</html>", url: request.url!) }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let health = await client.health()
        #expect(!health.ok)
        #expect(health.error?.contains("non-JSON") == true)
    }

    @Test("a refused connection explains itself in plain language")
    func healthUnreachable() async {
        StubURLProtocol.handler = { _ in throw URLError(.cannotConnectToHost) }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let health = await client.health()
        #expect(!health.ok)
        #expect(health.error?.contains("no brainstem answering") == true)
    }

    @Test("chat returns the response field the kernel actually uses")
    func chatOK() async {
        StubURLProtocol.handler = { request in
            reply(200, #"{"response":"hello there","model":"claude-haiku-4.5"}"#, url: request.url!)
        }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let result = await client.chat("hi")
        #expect(result.ok)
        #expect(result.response == "hello there")
        #expect(result.model == "claude-haiku-4.5")
    }

    @Test("an error field in a 200 body still fails the call")
    func chatErrorField() async {
        StubURLProtocol.handler = { request in
            reply(200, #"{"error":"no model configured"}"#, url: request.url!)
        }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let result = await client.chat("hi")
        #expect(!result.ok)
        #expect(result.error == "no model configured")
    }

    @Test("a body with no response field is a failure, not an empty success")
    func chatMissingField() async {
        StubURLProtocol.handler = { request in reply(200, #"{"unexpected":true}"#, url: request.url!) }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        let result = await client.chat("hi")
        #expect(!result.ok)
        #expect(result.response == nil)
    }

    @Test("chat posts the wire format the desktop mirror uses")
    func chatWireFormat() async throws {
        nonisolated(unsafe) var seen: [String: Any] = [:]
        StubURLProtocol.handler = { request in
            let body = request.httpBody ?? request.httpBodyStream.map { stream in
                stream.open()
                defer { stream.close() }
                var data = Data()
                let size = 4096
                let buffer = UnsafeMutablePointer<UInt8>.allocate(capacity: size)
                defer { buffer.deallocate() }
                while stream.hasBytesAvailable {
                    let read = stream.read(buffer, maxLength: size)
                    if read <= 0 { break }
                    data.append(buffer, count: read)
                }
                return data
            } ?? Data()
            seen = (try? JSONSerialization.jsonObject(with: body) as? [String: Any]) as? [String: Any] ?? [:]
            return reply(200, #"{"response":"ok"}"#, url: request.url!)
        }
        let client = BrainstemClient(baseURL: base, session: stubbedSession())
        _ = await client.chat("question", history: [ChatTurn(role: "user", content: "earlier")], sessionId: "s1")
        #expect(seen["user_input"] as? String == "question")
        #expect(seen["session_id"] as? String == "s1")
        #expect((seen["conversation_history"] as? [[String: String]])?.count == 1)
    }
}

@Suite("The evidence ledger", .serialized)
struct DiagnosticsTests {
    private func freshLedger() -> Diagnostics {
        let url = FileManager.default.temporaryDirectory
            .appendingPathComponent("mirror-diag-\(UUID().uuidString).jsonl")
        return Diagnostics(fileURL: url)
    }

    @Test("seq is monotonic so an agent can poll a cursor")
    func monotonic() async {
        let ledger = freshLedger()
        let a = await ledger.record("A", .info, "one")
        let b = await ledger.record("A", .info, "two")
        #expect(a.seq + 1 == b.seq)
    }

    @Test("events(since:) returns only what is new")
    func cursor() async {
        let ledger = freshLedger()
        await ledger.record("A", .info, "first")
        let mark = await ledger.cursor()
        await ledger.record("A", .info, "second")
        let fresh = await ledger.events(since: mark)
        #expect(fresh.map(\.message) == ["second"])
    }

    @Test("a secret is scrubbed before it is ever written down")
    func redaction() {
        let dirty = "failed with X-Brainstem-Secret: sk-supersecret"
        let clean = Diagnostics.redact(dirty)
        #expect(!clean.contains("sk-supersecret"))
        #expect(clean.contains("[redacted]"))
    }

    @Test("an unwritable ledger never throws into the caller")
    func unwritable() async {
        let ledger = Diagnostics(fileURL: URL(fileURLWithPath: "/definitely/not/writable/x.jsonl"))
        await ledger.record("A", .info, "still fine")
        let events = await ledger.events()
        #expect(events.last?.message == "still fine")
    }
}
