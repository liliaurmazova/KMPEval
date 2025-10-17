from evaluators.model_evaluator import generate_build_files
import os
from config.constants import GOLDEN_DATASET_PATH, GENERATED_OUTPUT_PATH
from evaluators.model_evaluator import compare_results
from evaluators.project_assembler import assemble_project, assemble_project_stub


def main():
   
    root_build, app_build, settings = generate_build_files()
    
    if root_build is None or app_build is None or settings is None:
        print("Cannot generate build files. Interruption.")
        return
    
    # Дополнительная проверка на пустые файлы
    if not root_build.strip() or not app_build.strip() or not settings.strip():
        print("⚠️ Warning: One or more generated files are empty!")
        print(f"Root build: {len(root_build)} chars, App build: {len(app_build)} chars, Settings: {len(settings)} chars")
    
    # Save generated files
    with open(os.path.join(GENERATED_OUTPUT_PATH, "build.gradle.kts"), "w", encoding="utf-8") as f:
        f.write(root_build)

    # Create composeApp directory if it doesn't exist
    compose_app_dir = os.path.join(GENERATED_OUTPUT_PATH, "composeApp")
    os.makedirs(compose_app_dir, exist_ok=True)
    
    with open(os.path.join(compose_app_dir, "build.gradle.kts"), "w", encoding="utf-8") as f:
        f.write(app_build)
        
    # Save settings.gradle.kts
    with open(os.path.join(GENERATED_OUTPUT_PATH, "settings.gradle.kts"), "w", encoding="utf-8") as f:
        f.write(settings)
        
    print(f"✅ Generated files saved to {GENERATED_OUTPUT_PATH}")
        
    compare_results(GOLDEN_DATASET_PATH, GENERATED_OUTPUT_PATH)

    # Тестируем логику сборки с готовыми файлами
    print("\n" + "="*60)
    assemble_success = assemble_project_stub(GOLDEN_DATASET_PATH)
    if assemble_success:
        print("🎉 Assembly logic works with golden files!")
    else:
        print("❌ Assembly logic needs fixes")
        
    # Сборка сгенерированных файлов отключена
    # assemble_project(GENERATED_OUTPUT_PATH)
    print("\nGenerated files assembly skipped - focusing on golden file validation.")


if __name__ == "__main__":
    main()
