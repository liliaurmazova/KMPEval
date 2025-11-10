// Simple test build configuration for golden_dataset validation
// This file is used only for syntax validation, not for full builds

plugins {
    // Use apply false for validation without actual application
}

// Basic project configuration for syntax checking
tasks.register("validateSyntax") {
    description = "Validates that this build.gradle.kts has correct syntax"
    doLast {
        println("✅ build.gradle.kts syntax is valid")
        println("📁 Project: ${project.name}")
        println("📁 Root dir: ${project.rootDir}")
    }
}