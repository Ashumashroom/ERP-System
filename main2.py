import LocalAuthentication

func authenticateUser() {
    let context = LAContext()
    var error: NSError?

    if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
        context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: "Authenticate using Touch ID") { success, error in
            if success {
                print("Authentication successful")
            } else {
                print("Authentication failed: \(String(describing: error?.localizedDescription))")
            }
        }
    } else {
        print("Touch ID not available or not configured")
    }
}

authenticateUser()
