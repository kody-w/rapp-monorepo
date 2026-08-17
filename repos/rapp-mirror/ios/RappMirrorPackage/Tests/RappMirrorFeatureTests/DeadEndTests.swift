import Testing
@testable import RappMirrorFeature

@Suite("The mirror is never a dead end")
struct DeadEndTests {
    @Test("a refused hold with an empty stage gets the opening portals back")
    func emptyStageRecovers() {
        let recovered = MirrorVUI.wayForward(from: [])
        #expect(!recovered.isEmpty, "no voice and no options is a brick")
        #expect(recovered.count == MirrorVUI.openingPortals.count)
    }

    @Test("a refused hold does not overwrite options the brainstem just offered")
    func existingOptionsSurvive() {
        let offered = [HoloOption(label: "Approve"), HoloOption(label: "Reject")]
        let recovered = MirrorVUI.wayForward(from: offered)
        #expect(recovered.map(\.label) == ["Approve", "Reject"])
    }

    @Test("the opening portals are real choices, not placeholders")
    func openingPortalsAreUsable() {
        for portal in MirrorVUI.openingPortals {
            #expect(!portal.label.isEmpty)
            #expect(!portal.send.isEmpty, "a portal must have something to say")
        }
    }
}
