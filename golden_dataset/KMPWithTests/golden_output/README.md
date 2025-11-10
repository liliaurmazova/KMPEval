# Golden Output Configuration

## Overview
This directory contains **reference configuration files** for KMP project evaluation. These files serve as "golden" examples for comparing AI-generated build configurations.

## Important Notes

### Build Configuration
- **Purpose**: Syntax validation and structure verification only
- **Not for full builds**: This simplified configuration doesn't support complete KMP compilation
- **Focus**: File comparison and dependency analysis

### Files

#### `build.gradle.kts`
- **Current**: Simplified validation-only configuration  
- **Backup**: `build.gradle.kts.original` contains the full original configuration with version catalog references
- **Purpose**: Allows Gradle syntax validation without requiring full KMP setup

#### `settings.gradle.kts`
- **Modified**: Removed `include(":composeApp")` reference
- **Reason**: No composeApp subproject exists in this validation-only directory
- **Note**: Full structure available in `../generated/` folder

#### `gradle/libs.versions.toml`
- **Added**: For dependency version management
- **Contains**: Android SDK versions, library versions, plugin versions
- **Purpose**: Supports build.gradle.kts compilation and validation

### Usage

#### Syntax Validation
```powershell
gradle validateSyntax
```

#### Full Build (Not Supported)
For actual KMP builds, use the `../generated/` directory which contains complete project structure.

### File Comparison
The evaluation system compares:
- ✅ Dependency declarations
- ✅ Plugin configurations  
- ✅ Android settings
- ✅ Source set structure
- ✅ Build type configurations

### Troubleshooting

#### Gradle Not Recognized
If you get "gradle is not recognized" error:
```powershell
.\fix-gradle-path.ps1
```

This script will:
1. Fix PATH for current session
2. Show instructions for permanent fix

#### Path Issues
The system PATH may point to `C:\Gradle\gradle-9.1.0\bin` but Gradle is actually in `C:\Gradle\bin`. 

**Temporary fix** (current session):
```powershell
$env:PATH = ($env:PATH -replace 'C:\\Gradle\\gradle-9\.1\.0\\bin', 'C:\Gradle\bin')
```

**Permanent fix** (requires Administrator):
Update System Environment Variables to change the path from `C:\Gradle\gradle-9.1.0\bin` to `C:\Gradle\bin`

## Structure

```
golden_output/
├── build.gradle.kts              # Simplified validation configuration
├── build.gradle.kts.original     # Full original configuration (backup)
├── settings.gradle.kts           # Project settings (composeApp reference removed)
├── gradle/
│   ├── libs.versions.toml        # Version catalog  
│   └── wrapper/                  # Gradle wrapper files
├── composeApp-debug.apk          # Pre-built APK for testing
├── local.properties              # Local SDK configuration
└── output-metadata.json          # Build metadata

```

## Comparison Process

1. **Generate**: AI generates new build configurations
2. **Save**: Output saved to `../generated/`
3. **Compare**: System compares generated files against these golden files
4. **Metrics**: Calculates similarity scores, BLEU, dependency analysis

## Maintenance

When updating golden files:
1. Backup existing files
2. Update with new reference configuration  
3. Verify syntax: `gradle validateSyntax`
4. Document changes in this README
5. Update evaluation metrics if structure changes significantly