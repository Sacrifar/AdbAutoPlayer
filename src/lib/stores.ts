import { writable } from "svelte/store";
import type { AppSettings, ProfileState } from "$pytauri/_apiTypes";
export const appSettings = writable<null | AppSettings>(null);
export const debugLogLevelOverwrite = writable<boolean[]>([false]);
export const activeProfile = writable<number>(0);
export const profileStates = writable<ProfileState[]>([]);
export const profileStateTimestamp = writable<number | null>();

export const uiState = writable({
  showSettings: false,
  settingsType: "adb" as "adb" | "game" | "app",
  sidebarOpen: true,
  logOpen: true,
  theme: "dark" as "dark" | "light",
  accentHue: 272,
  customizerOpen: false,
});
