import Foundation
import CoreImage

let path = CommandLine.arguments[1]
guard let image = CIImage(contentsOf: URL(fileURLWithPath: path)) else {
    print("DECODE_FAIL: could not load image"); exit(1)
}
let detector = CIDetector(ofType: CIDetectorTypeQRCode, context: nil,
                          options: [CIDetectorAccuracy: CIDetectorAccuracyHigh])!
let features = detector.features(in: image).compactMap { $0 as? CIQRCodeFeature }
guard let message = features.first?.messageString else {
    print("DECODE_FAIL: no QR found"); exit(1)
}
print("DECODED: \(message)")
