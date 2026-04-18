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

// 3. Update src-tauri/Cargo.toml
const cargoPath = path.join(rootDir, "src-tauri", "Cargo.toml");
if (fs.existsSync(cargoPath)) {
  let cargoContent = fs.readFileSync(cargoPath, "utf8");
  // Simple regex for version = "x.y.z" under [package]
  cargoContent = cargoContent.replace(
    /^version\s*=\s*"[^"]*"/m,
    `version = "${newVersion}"`,
  );
  fs.writeFileSync(cargoPath, cargoContent);
  console.log(`✅ Updated Cargo.toml to ${newVersion}`);
}
