def generate_system_prompt(source_code):
    return f"""You are an expert in Kotlin Multiplatform projects.
    Based on all the following project files, generate the necessary build files: root build.gradle.kts, composeApp build.gradle.kts, settings.gradle.kts, and gradlew.bat.
    Pay close attention to imports in .kt files and dependencies mentioned in other files.

    Combined source code from all relevant project files:
    ---
    {source_code}
    ---

    Your response MUST be in the following format, and nothing else:
    
    [ROOT_BUILD_START]
    (content of root build.gradle.kts)
    [ROOT_BUILD_END]

    [APP_BUILD_START]
    (content of composeApp/build.gradle.kts)
    [APP_BUILD_END]

    [SETTINGS_START]
    (content of settings.gradle.kts)
    [SETTINGS_END]

    [GRADLEW_START]
    (content of gradlew.bat - Windows batch file to run gradle wrapper)
    [GRADLEW_END]
    """
    
  