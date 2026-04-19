const fs = require("fs");
const path = require("path");

const newVersion = process.argv[2];

if (!newVersion) {
  console.error("❌ Usage: node set-version.cjs <version>");
  process.exit(1);
}

const rootDir = path.join(__dirname, "..");

// 1. Update src-tauri/tauri.conf.json
const tauriConfigPath = path.join(rootDir, "src-tauri", "tauri.conf.json");
if (fs.existsSync(tauriConfigPath)) {
  const config = JSON.parse(fs.readFileSync(tauriConfigPath, "utf8"));
  config.version = newVersion;
  fs.writeFileSync(tauriConfigPath, JSON.stringify(config, null, 2) + "\n");
  console.log(`✅ Updated tauri.conf.json to ${newVersion}`);
}

// 2. Update package.json
const packagePath = path.join(rootDir, "package.json");
if (fs.existsSync(packagePath)) {
  const pkg = JSON.parse(fs.readFileSync(packagePath, "utf8"));
  pkg.version = newVersion;
  fs.writeFileSync(packagePath, JSON.stringify(pkg, null, 2) + "\n");
  console.log(`✅ Updated package.json to ${newVersion}`);
}

// 3. Update Cargo.toml files
const cargoPaths = [
  path.join(rootDir, "Cargo.toml"),
  path.join(rootDir, "src-tauri", "Cargo.toml"),
];

cargoPaths.forEach((cPath) => {
  if (fs.existsSync(cPath)) {
    let content = fs.readFileSync(cPath, "utf8");
    // Update version = "x.y.z" at the start of a line (for [package] or [workspace.package])
    content = content.replace(/^(version\s*=\s*)"[^"]*"/m, `$1"${newVersion}"`);
    fs.writeFileSync(cPath, content);
    console.log(`✅ Updated ${path.relative(rootDir, cPath)} to ${newVersion}`);
  }
});

// 4. Update pyproject.toml (root and src-tauri)
const pyprojectPaths = [
  path.join(rootDir, "pyproject.toml"),
  path.join(rootDir, "src-tauri", "pyproject.toml"),
];

pyprojectPaths.forEach((pyPath) => {
  if (fs.existsSync(pyPath)) {
    let pyContent = fs.readFileSync(pyPath, "utf8");
    pyContent = pyContent.replace(
      /^(version\s*=\s*)"[^"]*"/m,
      `$1"${newVersion}"`,
    );
    fs.writeFileSync(pyPath, pyContent);
    console.log(
      `✅ Updated ${path.relative(rootDir, pyPath)} to ${newVersion}`,
    );
  }
});
