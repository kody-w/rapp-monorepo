import Foundation

/// Where the brainstem lives.
///
/// On the desktop the engine answers on loopback; on a phone it is another
/// machine on the network, so the URL is the one thing a user must actually
/// configure. Kept in `UserDefaults` — this is a preference, not a document,
/// and it must never hold a secret.
public enum BrainstemSettings {
    static let key = "rapp.brainstem.url"
    public static let fallback = URL(string: "http://127.0.0.1:7071")!

    public static var storedURL: URL {
        guard
            let raw = UserDefaults.standard.string(forKey: key),
            let url = URL(string: raw),
            url.scheme != nil
        else { return fallback }
        return url
    }

    /// Returns false (and stores nothing) when the text is not a usable URL.
    @discardableResult
    public static func store(_ raw: String) -> Bool {
        let trimmed = raw.trimmingCharacters(in: .whitespacesAndNewlines)
        guard
            !trimmed.isEmpty,
            let url = URL(string: trimmed),
            let scheme = url.scheme,
            ["http", "https"].contains(scheme.lowercased()),
            url.host != nil
        else { return false }
        UserDefaults.standard.set(url.absoluteString, forKey: key)
        return true
    }

    public static func reset() {
        UserDefaults.standard.removeObject(forKey: key)
    }
}
