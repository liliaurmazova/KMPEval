import os
import difflib
import anthropic
import re
from difflib import SequenceMatcher
from config.constants import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE, GOLDEN_DATASET_PATH, GENERATED_OUTPUT_PATH
from prompts.system_prompt_generator import generate_system_prompt
from util.folder_helper import ensure_directory_exists, find_relevant_files_in_codebase

def generate_build_files():

    ensure_directory_exists(GENERATED_OUTPUT_PATH)

    source_code = find_relevant_files_in_codebase(os.path.join(GOLDEN_DATASET_PATH, "input_codebase"))

    if source_code is None:
        print("No source code found. Exiting.")
        exit(1)

    else:
        system_prompt = generate_system_prompt(source_code)

        print("api key:", ANTHROPIC_API_KEY)
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        try:
            response = client.messages.create(
                model=MODEL_NAME,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "user", "content": system_prompt}
                ]
            )
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text
            
            # What has been received from the model
            print(f"📝 Model response length: {len(content)} characters")
            print(f"📝 Response preview: {content[:200]}...")
            
            # Marker checks
            markers = ["[ROOT_BUILD_START]", "[ROOT_BUILD_END]", "[APP_BUILD_START]", "[APP_BUILD_END]", "[SETTINGS_START]", "[SETTINGS_END]"]
            for marker in markers:
                if marker in content:
                    print(f"✅ Found marker: {marker}")
                else:
                    print(f"❌ Missing marker: {marker}")
            
            # Files extraction
            try:
                root_build_content = content.split("[ROOT_BUILD_START]")[1].split("[ROOT_BUILD_END]")[0].strip()
                print(f"✅ Root build extracted: {len(root_build_content)} chars")
            except IndexError:
                print("❌ Failed to extract root build content")
                root_build_content = None
                
            try:
                app_build_content = content.split("[APP_BUILD_START]")[1].split("[APP_BUILD_END]")[0].strip()
                print(f"✅ App build extracted: {len(app_build_content)} chars")
            except IndexError:
                print("❌ Failed to extract app build content")
                app_build_content = None
                
            try:
                settings_content = content.split("[SETTINGS_START]")[1].split("[SETTINGS_END]")[0].strip()
                print(f"✅ Settings extracted: {len(settings_content)} chars")
            except IndexError:
                print("❌ Failed to extract settings content")
                settings_content = None

            # Preview extracted contents
            print(f"\n🔍 Root build preview: '{root_build_content[:100] if root_build_content else 'EMPTY'}'")
            print(f"🔍 App build preview: '{app_build_content[:100] if app_build_content else 'EMPTY'}'")  
            print(f"🔍 Settings preview: '{settings_content[:100] if settings_content else 'EMPTY'}'")

            return root_build_content, app_build_content, settings_content

        except Exception as e:
            print(f"API parsing error: {e}")
            return None, None, None



"""
BLUE-like metric implementation for n-grams
"""
def calculate_bleu_score(reference, candidate):
    ref_words = reference.split()
    cand_words = candidate.split()
    
    if not cand_words:
        return 0.0
    
    # 1-grams
    ref_1grams = set(ref_words)
    cand_1grams = set(cand_words)
    precision_1 = len(ref_1grams & cand_1grams) / len(cand_1grams) if cand_1grams else 0

    # 2-grams
    ref_2grams = set(zip(ref_words, ref_words[1:]))
    cand_2grams = set(zip(cand_words, cand_words[1:]))
    precision_2 = len(ref_2grams & cand_2grams) / len(cand_2grams) if cand_2grams else 0

    # Combined BLUE-like metric
    return (precision_1 + precision_2) / 2



"""
Text similarity ratio
"""
def calculate_similarity_ratio(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def extract_dependencies(gradle_content):
    """Extracts dependencies from build.gradle.kts"""
    dependencies = []

    # Various patterns for Kotlin DSL
    patterns = [
        # Regular dependencies: implementation("lib:name:version")
        r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(\s*["\']([^"\']+)["\']',
        # Version catalogs: implementation(libs.androidx.activity.compose)
        r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(\s*libs\.([^)]+)\)',
        # Compose dependencies: implementation(compose.runtime)
        r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(\s*(compose\.[^)]+)\)',
        # Kotlin dependencies: implementation(kotlin("test"))
        r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(\s*kotlin\s*\(\s*["\']([^"\']+)["\']',
        # Plugin aliases: alias(libs.plugins.kotlin.multiplatform)
        r'alias\s*\(\s*libs\.plugins\.([^)]+)\)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, gradle_content, re.IGNORECASE | re.MULTILINE)
        dependencies.extend(matches)

    # Also search for dependencies and sourceSets blocks for context
    deps_blocks = re.findall(r'dependencies\s*\{([^}]+)\}', gradle_content, re.DOTALL)
    for block in deps_blocks:
        # Simple dependencies within blocks
        simple_deps = re.findall(r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(\s*["\']([^"\']+)["\']', block)
        dependencies.extend(simple_deps)
    
    return set(dependencies)


"""
Calculates precision, recall, F1 for dependencies
"""
def calculate_dependency_metrics(golden_deps, generated_deps):
    
    if not golden_deps and not generated_deps:
        return 1.0, 1.0, 1.0
    if not generated_deps:
        return 0.0, 0.0, 0.0
    if not golden_deps:
        return 0.0, 1.0, 0.0
        
    intersection = golden_deps & generated_deps
    precision = len(intersection) / len(generated_deps)
    recall = len(intersection) / len(golden_deps)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1


"""
Compare generated files against golden files with detailed metrics
"""
def compare_results(golden_path, generated_path):

    print("\n--- Compare results ---")

    files_to_compare = [
        "build.gradle.kts"
    ]
    
    for file_path in files_to_compare:
        golden_file = os.path.join(golden_path, "golden_output", file_path)
        generated_file = os.path.join(generated_path, file_path)
        
        print(f"\n File to compare: {file_path}")
        print(f"Golden file path: {golden_file}")
        print(f"Generated file path: {generated_file}")
        
        if not os.path.exists(golden_file):
            print(f"Golden file not found: {golden_file}")
            continue
            
        if not os.path.exists(generated_file):
            print(f"Generated file not found: {generated_file}")
            continue
            
        with open(golden_file, 'r', encoding='utf-8') as f1, open(generated_file, 'r', encoding='utf-8') as f2:
            golden_content = f1.read()
            generated_content = f2.read()

            print(f"\n=== DETAILED METRICS ===")
            
            # --- Metric 1: Similarity Ratio ---
            similarity = calculate_similarity_ratio(golden_content, generated_content)
            print(f"📊 Similarity Ratio: {similarity:.3f}")
            
            # --- Metric 2: BLEU-like Score ---
            bleu = calculate_bleu_score(golden_content, generated_content)
            print(f"📊 BLEU-like Score: {bleu:.3f}")
            
            # --- Metric 3: Line-by-line diff ---
            golden_lines = golden_content.splitlines()
            generated_lines = generated_content.splitlines()
            diff = list(difflib.unified_diff(golden_lines, generated_lines, lineterm=''))
            if not diff:
                print("📊 Text match: 100%")
            else:
                match_percentage = max(0, 100 - len(diff) * 2)  
                print(f"📊 Text match: ~{match_percentage}%")
                if len(diff) <= 20:  
                    print("--- Differences ---")
                    print("\n".join(diff[:20]))
                    if len(diff) > 20:
                        print(f"... and {len(diff) - 20} more differences")

            # --- Metric 4: Dependency Analysis (for build files) ---
            if file_path.endswith("build.gradle.kts"):
                golden_deps = extract_dependencies(golden_content)
                generated_deps = extract_dependencies(generated_content)
                
                
                print(f"🔍 Golden dependencies found ({len(golden_deps)}): {list(golden_deps)[:10]}")
                print(f"🔍 Generated dependencies found ({len(generated_deps)}): {list(generated_deps)[:10]}")
                
                precision, recall, f1 = calculate_dependency_metrics(golden_deps, generated_deps)
                print(f"📊 Dependencies - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
                
                missing_deps = golden_deps - generated_deps
                extra_deps = generated_deps - golden_deps
                
                if missing_deps:
                    print(f"❌ Missing dependencies: {', '.join(list(missing_deps)[:5])}")
                if extra_deps:
                    print(f"➕ Extra dependencies: {', '.join(list(extra_deps)[:5])}")
                if not missing_deps and not extra_deps:
                    print("✅ All dependencies match!")

            # --- Metric 5: Key dependency check (for app build) ---
            if "composeApp" in file_path:
                key_deps = ['io.ktor:ktor-client-core', 'compose.runtime', 'compose.foundation']
                found_key_deps = [dep for dep in key_deps if dep in generated_content]
                print(f"📊 Key dependencies found: {len(found_key_deps)}/{len(key_deps)}")
                for dep in key_deps:
                    status = "✅" if dep in generated_content else "❌"
                    print(f"  {status} {dep}")
            
            print("=" * 50)

