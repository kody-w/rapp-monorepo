import Foundation

/// Markdown is for reading, not for saying.
///
/// The brainstem answers in markdown, and a voice-first interface must never
/// read `###` or `**bold**` aloud — nor show the syntax in a caption that is
/// only ever glanced at. This strips formatting down to plain sentences while
/// keeping the words and their order intact.
public enum Plain {
    /// Ordered so that inline markers are removed before the leftovers.
    private static let rules: [(pattern: String, template: String)] = [
        (#"```[\s\S]*?```"#, " "),                      // fenced code
        (#"`([^`]*)`"#, "$1"),                          // inline code
        (#"!\[([^\]]*)\]\([^)]*\)"#, "$1"),             // images
        (#"\[([^\]]+)\]\([^)]*\)"#, "$1"),              // links -> their text
        (#"^\s{0,3}#{1,6}\s*"#, ""),                    // headings
        (#"^\s{0,3}>\s?"#, ""),                         // block quotes
        (#"^\s{0,3}[-*+]\s+"#, ""),                     // bullets
        (#"^\s{0,3}\d+[.)]\s+"#, ""),                   // numbered list markers
        (#"\*\*\*([^*]+)\*\*\*"#, "$1"),                // bold italic
        (#"\*\*([^*]+)\*\*"#, "$1"),                    // bold
        (#"(?<!\*)\*(?!\*)([^*\n]+)\*(?!\*)"#, "$1"),   // italic
        (#"__([^_]+)__"#, "$1"),                        // bold (underscores)
        (#"~~([^~]+)~~"#, "$1"),                        // strikethrough
        (#"^\s{0,3}([-*_]\s*){3,}$"#, ""),              // horizontal rules
        (#"\|"#, " "),                                  // table pipes
    ]

    /// Plain text, safe to speak and to show.
    public static func text(_ markdown: String) -> String {
        var out = markdown
        for rule in rules {
            guard
                let regex = try? NSRegularExpression(
                    pattern: rule.pattern,
                    options: [.anchorsMatchLines]
                )
            else { continue }
            out = regex.stringByReplacingMatches(
                in: out,
                range: NSRange(out.startIndex..., in: out),
                withTemplate: rule.template
            )
        }
        // Collapse the whitespace the stripping leaves behind.
        out = out.replacingOccurrences(
            of: #"[ \t]{2,}"#,
            with: " ",
            options: .regularExpression
        )
        out = out.replacingOccurrences(
            of: #"\n{3,}"#,
            with: "\n\n",
            options: .regularExpression
        )
        return out.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// What the mirror actually says: plain, and never an essay.
    public static func spoken(_ markdown: String, limit: Int = 600) -> String {
        let plain = text(markdown).replacingOccurrences(
            of: #"\s*\n+\s*"#,
            with: ". ",
            options: .regularExpression
        )
        // Stitching lines with ". " can double up terminal punctuation.
        let tidied = plain.replacingOccurrences(
            of: #"([.!?])\.\s"#,
            with: "$1 ",
            options: .regularExpression
        )
        guard tidied.count > limit else { return tidied }
        let cut = tidied.prefix(limit)
        // Prefer to stop on a sentence rather than mid-word.
        if let end = cut.lastIndex(where: { ".!?".contains($0) }) {
            return String(cut[...end])
        }
        return String(cut) + "…"
    }
}
