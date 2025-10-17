import os
import shutil
import subprocess

from config.constants import GOLDEN_DATASET_PATH

def assemble_project_stub(golden_path):
    """Заглушка для тестирования сборки - использует готовые файлы из golden_output"""
    print("\n--- Testing project assembly with golden files ---")
    
    golden_output_path = os.path.join(golden_path, "golden_output")
    
    if not os.path.exists(golden_output_path):
        print(f"❌ Golden output path not found: {golden_output_path}")
        return False
    
    # Проверяем наличие основных файлов
    required_files = ["build.gradle.kts", "settings.gradle.kts"]
    
    for file in required_files:
        file_path = os.path.join(golden_output_path, file)
        if os.path.exists(file_path):
            print(f"✅ Found: {file}")
            # Показываем размер файла
            size = os.path.getsize(file_path)
            print(f"   Size: {size} bytes")
        else:
            print(f"❌ Missing: {file}")
    
    # Проверяем структуру проекта
    print(f"\n📁 Golden output contents:")
    for item in os.listdir(golden_output_path):
        item_path = os.path.join(golden_output_path, item)
        if os.path.isdir(item_path):
            print(f"   [DIR]  {item}/")
        else:
            print(f"   [FILE] {item}")
    
    # Имитируем проверку синтаксиса build.gradle.kts
    build_gradle = os.path.join(golden_output_path, "build.gradle.kts")
    if os.path.exists(build_gradle):
        with open(build_gradle, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Простые проверки синтаксиса
        syntax_checks = [
            ("plugins block", "plugins" in content),
            ("kotlin block", "kotlin" in content or "multiplatform" in content),
            ("android block", "android" in content),
            ("braces balanced", content.count("{") == content.count("}")),
        ]
        
        print(f"\n🔍 Syntax checks for build.gradle.kts:")
        all_passed = True
        for check_name, passed in syntax_checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
                
        if all_passed:
            print(f"\n🎉 Golden files pass basic validation!")
            return True
        else:
            print(f"\n❌ Golden files have syntax issues!")
            return False
    else:
        print(f"\n❌ No build.gradle.kts found for validation")
        return False


def assemble_project(generated_path):
    print("\n--- Trying to assemble project ---")

    # Copy source code to the generated files folder for assembly
    input_codebase_path = os.path.join(GOLDEN_DATASET_PATH, "input_codebase")
    
    # Копируем все файлы из input_codebase в generated_path, не перезаписывая build.gradle.kts
    for root, dirs, files in os.walk(input_codebase_path):
        # Вычисляем относительный путь от input_codebase
        rel_path = os.path.relpath(root, input_codebase_path)
        if rel_path == ".":
            target_dir = generated_path
        else:
            target_dir = os.path.join(generated_path, rel_path)
        
        # Создаем целевую директорию если её нет
        os.makedirs(target_dir, exist_ok=True)
        
        # Копируем файлы
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_dir, file)
            
            # Не перезаписываем build.gradle.kts файлы
            if file == "build.gradle.kts" and os.path.exists(target_file):
                print(f"Skipping existing build file: {target_file}")
                continue
                
            shutil.copy2(source_file, target_file)

    # Создаем папку для gradle wrapper если её нет
    wrapper_dir = os.path.join(generated_path, "gradle", "wrapper")
    os.makedirs(wrapper_dir, exist_ok=True)
    
    # Создаем gradle-wrapper.properties если его нет
    wrapper_props = os.path.join(wrapper_dir, "gradle-wrapper.properties")
    if not os.path.exists(wrapper_props):
        with open(wrapper_props, 'w') as f:
            f.write("""distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.1-bin.zip
networkTimeout=10000
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists""")
    
    # Проверяем наличие Gradle wrapper
    gradlew_path = os.path.join(generated_path, "gradlew.bat")
    if not os.path.exists(gradlew_path):
        print("gradlew.bat file not found. Trying to use system gradle...")
        
        # Попробуем использовать системный gradle
        try:
            command = ["gradle", ":composeApp:assembleDebug", "--stacktrace"]
            process = subprocess.run(
                command,
                cwd=generated_path,
                capture_output=True,
                text=True,
                shell=True
            )
            
            if process.returncode == 0:
                print("\n SUCCESS! Project assembled successfully with system gradle!")
            else:
                print("\n FAILURE! Project assembly failed with system gradle.")
                print("--- Gradle Error ---")
                print(process.stderr)
                print("---------------------")
                
        except Exception as e:
            print(f"System gradle also failed: {e}")
            print("Skipping project assembly - no Gradle available.")
        
        return

    # Используем gradlew если он есть
    command = [gradlew_path, ":composeApp:assembleDebug", "--stacktrace"]
    try:
        process = subprocess.run(
            command,
            cwd=generated_path,
            capture_output=True,
            text=True,
            shell=True
        )

        if process.returncode == 0:
            print("\n SUCCESS! Project assembled successfully!")
        else:
            print("\n FAILURE! Project assembly failed.")
            print("--- Gradle Error ---")
            print(process.stderr)
            print("---------------------")

    except Exception as e:
        print(f" Critical error occurred while starting the build: {e}")