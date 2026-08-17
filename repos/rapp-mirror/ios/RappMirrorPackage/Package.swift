// swift-tools-version: 6.1
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "RappMirrorFeature",
    // macOS is declared so the pure-logic suites run under a plain `swift test`
    // (seconds, no simulator). The shipping product is the iOS app.
    platforms: [.iOS(.v18), .macOS(.v14)],
    products: [
        // Products define the executables and libraries a package produces, making them visible to other packages.
        .library(
            name: "RappMirrorFeature",
            targets: ["RappMirrorFeature"]
        ),
    ],
    targets: [
        // Targets are the basic building blocks of a package, defining a module or a test suite.
        // Targets can depend on other targets in this package and products from dependencies.
        .target(
            name: "RappMirrorFeature"
        ),
        .testTarget(
            name: "RappMirrorFeatureTests",
            dependencies: [
                "RappMirrorFeature"
            ]
        ),
    ]
)
