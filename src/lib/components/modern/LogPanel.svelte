<script lang="ts">
  import { t } from "$lib/i18n/i18n";
  import { onMount, tick } from "svelte";
  import { listen } from "@tauri-apps/api/event";
  import { appSettings, debugLogLevelOverwrite, uiState } from "$lib/stores";
  import { EventNames } from "$lib/log/eventNames";
  import {
    formatMessage,
    logMessageToTextDisplayCardItem,
  } from "$lib/log/logHelper";
  import type { TextDisplayCardItem } from "$lib/log/logHelper";
  import { Instant } from "@js-joda/core";

  interface TaskCompletedEvent {
    profile_index: number;
    msg: string | null;
    exit_code: number | null;
  }

  interface Props {
    profileIndex: number;
    onClear: () => void;
    collapsed: boolean;
    position?: "right" | "bottom";
  }

  let {
    profileIndex,
    onClear,
    collapsed,
    position = "right",
  }: Props = $props();

  let profileEntries: Record<number, TextDisplayCardItem[]> = $state({});
  let maxEntries = 1000;
  let scrollContainer: HTMLDivElement | null = $state(null);

  const logLevelOrder: Record<string, number> = {
    DEBUG: 0,
    INFO: 1,
    WARNING: 2,
    ERROR: 3,
    FATAL: 4,
  };

  function getOrCreateEntriesForProfile(index: number): TextDisplayCardItem[] {
    return profileEntries[index] ?? [];
  }

  function insertEntry(
    index: number | undefined | null,
    entry: TextDisplayCardItem,
  ) {
    const insertCount =
      index === undefined || index === null
        ? ($appSettings?.profiles?.profiles?.length ?? 1)
        : 1;

    const startIndex = index ?? 0;

    for (let i = 0; i < insertCount; i++) {
      const targetIndex = startIndex + i;
      profileEntries[targetIndex] ??= [];
      profileEntries[targetIndex].push(entry);
      if (profileEntries[targetIndex].length > maxEntries) {
        profileEntries[targetIndex].shift();
      }
    }

    // Trigger reactivity for profileEntries
    profileEntries = { ...profileEntries };

    scrollToBottom();
  }

  async function scrollToBottom() {
    await tick();
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }
  }

  function addSummaryMessageToLog(summary: TaskCompletedEvent) {
    if (!summary.msg) return;
    const summaryProfileIndex = summary.profile_index;
    const summaryMessage = formatMessage(summary.msg);
    if ("" === summaryMessage) return;

    insertEntry(summaryProfileIndex, {
      message: summaryMessage,
      timestamp: Instant.now(),
      html_class: "whitespace-pre-wrap text-secondary-500",
      level: "INFO", // Summary messages are usually info
    } as any);
  }

  onMount(() => {
    let unsubscribers: Array<() => void> = [];
    const setupListeners = async () => {
      const logUnsub = await listen<any>(EventNames.LOG_MESSAGE, (event) => {
        const logMessage = event.payload;
        const configLogLevel =
          ($appSettings?.logging?.level as string) ?? "INFO";

        let alwaysLogDebug = false;
        if (logMessage.profile_index !== undefined) {
          alwaysLogDebug =
            $debugLogLevelOverwrite[logMessage.profile_index] ?? false;
        }

        if (
          alwaysLogDebug ||
          logLevelOrder[logMessage.level] >= logLevelOrder[configLogLevel]
        ) {
          const entry = logMessageToTextDisplayCardItem(logMessage);
          (entry as any).level = logMessage.level; // Keep level for styling
          insertEntry(logMessage.profile_index, entry);
        }
      });

      const summaryUnsub = await listen<TaskCompletedEvent>(
        EventNames.TASK_COMPLETED,
        (event) => {
          if (event.payload) addSummaryMessageToLog(event.payload);
        },
      );

      unsubscribers.push(logUnsub, summaryUnsub);
    };

    setupListeners();
    return () => unsubscribers.forEach((unsub) => unsub());
  });

  const currentEntries = $derived(getOrCreateEntriesForProfile(profileIndex));

  function fmtTime(instant: Instant) {
    // Basic formatting for the terminal look
    const d = new Date(instant.toEpochMilli());
    return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
  }

  function handleClear() {
    profileEntries[profileIndex] = [];
    profileEntries = { ...profileEntries };
    onClear();
  }
</script>

<div
  class="log-panel"
  class:collapsed
  class:compact={$uiState.taskViewVariant === "accordion"}
  data-position={position}
>
  <div class="header">
    <span class="status-dot"></span>
    <div class="title">{$t("Live Log")}</div>
    <span class="spacer"></span>
    <span class="count">{currentEntries.length} {$t("lines")}</span>
    <button class="clear-btn" onclick={handleClear}>{$t("clear")}</button>
  </div>

  <div class="scroll-area" bind:this={scrollContainer}>
    {#each currentEntries as entry}
      <div class="log-line">
        <span class="time">{fmtTime(entry.timestamp)}</span>
        <span class="level-tag" data-level={(entry as any).level || "INFO"}>
          {(entry as any).level || "INFO"}
        </span>
        <span class="message">
          {@html entry.message.replace(/^\[[A-Z]+\]\s*/, "")}
        </span>
      </div>
    {/each}
    {#if currentEntries.length === 0}
      <div class="empty">{$t("No logs for this profile yet...")}</div>
    {/if}
  </div>
</div>

<style>
  .log-panel {
    display: flex;
    flex-direction: column;
    background: var(--bg-1);
    min-width: 0;
    transition: all var(--dur-2) var(--ease);
  }

  .log-panel[data-position="right"] {
    width: 400px;
    flex: 0 0 400px;
    border-left: 1px solid var(--line);
    height: 100%;
  }

  .log-panel[data-position="right"].collapsed {
    width: 0;
    flex: 0 0 0;
    border-left: none;
    overflow: hidden;
  }

  .log-panel[data-position="bottom"] {
    height: 250px;
    flex: 0 0 250px;
    border-top: 1px solid var(--line);
    width: 100%;
  }

  .log-panel[data-position="bottom"].collapsed {
    height: 0;
    flex: 0 0 0;
    border-top: none;
    overflow: hidden;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-bottom: 1px solid var(--line);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 999px;
    background: var(--ok);
  }

  .title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-3);
  }

  .spacer {
    flex: 1;
  }

  .count {
    font-size: 11px;
    color: var(--text-4);
    font-family: var(--font-mono);
  }

  .clear-btn {
    font-size: 11px;
    color: var(--text-3);
    padding: 2px 6px;
    border-radius: 4px;
    transition: background var(--dur-1);
  }

  .clear-btn:hover {
    background: var(--bg-hover);
    color: var(--text-1);
  }

  .scroll-area {
    flex: 1;
    overflow: auto;
    padding: 8px 0;
    background: var(--log-bg);
    font-family: var(--font-mono);
    font-size: 12px;
    line-height: 1.55;
  }

  .log-line {
    display: grid;
    grid-template-columns: 74px 62px 1fr;
    gap: 8px;
    padding: 2px 14px;
    min-width: 0;
  }

  .time {
    color: var(--text-4);
  }

  .level-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    border: 1px solid;
    border-radius: 4px;
    padding: 1px 0;
    text-align: center;
    height: fit-content;
  }

  .level-tag[data-level="DEBUG"] {
    color: var(--text-4);
    border-color: var(--text-4);
  }
  .level-tag[data-level="INFO"] {
    color: var(--accent-hi);
    border-color: color-mix(in oklab, var(--accent-hi) 40%, transparent);
  }
  .level-tag[data-level="WARNING"] {
    color: var(--warn);
    border-color: color-mix(in oklab, var(--warn) 45%, transparent);
  }
  .level-tag[data-level="ERROR"] {
    color: var(--err);
    border-color: color-mix(in oklab, var(--err) 45%, transparent);
  }
  .level-tag[data-level="FATAL"] {
    color: var(--err);
    border-color: var(--err);
    font-weight: 700;
  }

  .message {
    text-wrap: pretty;
    word-break: break-word;
    white-space: pre-wrap;
    min-width: 0;
  }

  .empty {
    padding: 20px;
    color: var(--text-4);
    text-align: center;
    font-style: italic;
  }

  /* Compact Mode Styles */
  .log-panel.compact[data-position="bottom"] {
    height: 160px;
    flex: 0 0 160px;
  }

  .log-panel.compact[data-position="bottom"] .header {
    padding: 6px 14px;
  }

  .log-panel.compact[data-position="bottom"] .scroll-area {
    font-size: 11.5px;
    line-height: 1.4;
  }

  .log-panel.compact[data-position="bottom"] .log-line {
    grid-template-columns: 68px 58px 1fr;
    padding: 1px 14px;
  }
</style>
