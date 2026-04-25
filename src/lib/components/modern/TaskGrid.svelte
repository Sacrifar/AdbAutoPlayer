<script lang="ts">
  import { t } from "$lib/i18n/i18n";
  import type { MenuButton } from "$lib/menu/model";

  interface Props {
    buttons: MenuButton[];
    disableActions: boolean;
    categories: string[];
  }

  let { buttons, disableActions, categories }: Props = $props();

  let query = $state("");
  let variant = $state<"cards" | "palette" | "accordion">("cards");

  const filteredButtons = $derived(
    buttons.filter((b) =>
      b.option.label.toLowerCase().includes(query.toLowerCase()),
    ),
  );

  const categorizedButtons = $derived.by(() => {
    const result: Record<string, MenuButton[]> = {};
    for (const button of filteredButtons) {
      const category = button.option.category || "";
      if (!result[category]) {
        result[category] = [];
      }
      result[category].push(button);
    }
    return result;
  });

  const activeCategories = $derived.by(() => {
    const cats = categories.filter(
      (cat) => categorizedButtons[cat]?.length > 0,
    );
    if (categorizedButtons[""]?.length > 0 && !cats.includes("")) {
      cats.push("");
    }
    return cats;
  });

  let openAccordions = $state(new Set<string>());
  let seenCategories = new Set<string>();

  $effect(() => {
    // Only auto-open categories the first time we see them
    const newCats = activeCategories.filter((c) => !seenCategories.has(c));
    if (newCats.length > 0) {
      for (const c of newCats) {
        seenCategories.add(c);
        openAccordions.add(c);
      }
      openAccordions = new Set(openAccordions);
    }
  });

  function toggleAccordion(cat: string) {
    if (openAccordions.has(cat)) {
      openAccordions.delete(cat);
    } else {
      openAccordions.add(cat);
    }
    openAccordions = new Set(openAccordions);
  }
</script>

<div class="task-grid-container">
  <div class="toolbar">
    <div class="search-box">
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linecap="round"
        stroke-linejoin="round"
        width="14"
        height="14"
        class="search-icon"
        ><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg
      >
      <input
        bind:value={query}
        placeholder={$t("Search tasks...")}
        class="search-input"
      />
      <kbd class="kbd">⌘K</kbd>
    </div>

    <div class="variant-toggle">
      {#each [{ id: "cards", label: $t("Cards"), icon: "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z" }, { id: "palette", label: $t("Palette"), icon: "M8 6h13M8 12h13M8 18h13M4 6h.01M4 12h.01M4 18h.01" }, { id: "accordion", label: $t("Accordion"), icon: "M3 4h18v6H3zM3 14h18v6H3z" }] as v}
        <button
          class="v-btn"
          class:active={variant === v.id}
          onclick={() => (variant = v.id as any)}
          title={v.label}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.7"
            stroke-linecap="round"
            stroke-linejoin="round"
            width="14"
            height="14"
          >
            <path d={v.icon} />
          </svg>
          <span>{v.label}</span>
        </button>
      {/each}
    </div>
  </div>

  <div class="view-content">
    {#if variant === "cards"}
      <div class="cards-view">
        {#each activeCategories as cat}
          <section class="section">
            <div class="section-header">
              <div class="section-title">{$t(cat || "Other")}</div>
              <div class="section-line"></div>
              <div class="section-count">
                {String(categorizedButtons[cat].length).padStart(2, "0")}
              </div>
            </div>
            <div class="grid">
              {#each categorizedButtons[cat] as b}
                <button
                  class="task-card"
                  class:active={b.isProcessRunning}
                  disabled={disableActions &&
                    !b.isProcessRunning &&
                    !b.alwaysEnabled}
                  onclick={b.callback}
                >
                  <div class="card-top">
                    <div class="card-label">{$t(b.option.label)}</div>
                    {#if b.isProcessRunning}
                      <span class="running-tag">● {$t("Run")}</span>
                    {:else}
                      <div class="play-box">
                        <svg
                          viewBox="0 0 24 24"
                          fill="currentColor"
                          width="10"
                          height="10"><path d="M8 5v14l11-7z" /></svg
                        >
                      </div>
                    {/if}
                  </div>
                  {#if b.option.tooltip}
                    <div class="card-hint">{$t(b.option.tooltip)}</div>
                  {/if}
                </button>
              {/each}
            </div>
          </section>
        {/each}
      </div>
    {:else if variant === "palette"}
      <div class="palette-view">
        {#each activeCategories as cat}
          <div class="palette-section">
            <div class="palette-cat">{$t(cat || "Other")}</div>
            {#each categorizedButtons[cat] as b}
              <button
                class="palette-item"
                class:active={b.isProcessRunning}
                disabled={disableActions &&
                  !b.isProcessRunning &&
                  !b.alwaysEnabled}
                onclick={b.callback}
              >
                <span class="item-icon">
                  {#if b.isProcessRunning}
                    <span class="dot"></span>
                  {:else}
                    <svg
                      viewBox="0 0 24 24"
                      fill="currentColor"
                      width="10"
                      height="10"><path d="M8 5v14l11-7z" /></svg
                    >
                  {/if}
                </span>
                <span class="item-label">{$t(b.option.label)}</span>
                {#if b.option.tooltip}
                  <span class="item-hint">— {$t(b.option.tooltip)}</span>
                {/if}
                <div class="spacer"></div>
                {#if b.isProcessRunning}
                  <span class="item-status">{$t("Running")}</span>
                {/if}
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  width="14"
                  height="14"
                  class="chevron"><path d="m9 18 6-6-6-6" /></svg
                >
              </button>
            {/each}
          </div>
        {/each}
      </div>
    {:else}
      <div class="accordion-view">
        {#each activeCategories as cat}
          {@const isOpen = openAccordions.has(cat)}
          <div class="accordion-item">
            <button
              class="accordion-trigger"
              onclick={() => toggleAccordion(cat)}
            >
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
                width="14"
                height="14"
                class="chevron-toggle"
                style="transform: {isOpen ? 'rotate(90deg)' : 'rotate(0)'}"
                ><path d="m9 18 6-6-6-6" /></svg
              >
              <span class="acc-title">{$t(cat || "Other")}</span>
              <div class="spacer"></div>
              <span class="acc-count"
                >{String(categorizedButtons[cat].length).padStart(2, "0")}</span
              >
            </button>
            {#if isOpen}
              <div class="acc-content">
                <div class="grid">
                  {#each categorizedButtons[cat] as b}
                    <button
                      class="task-card"
                      class:active={b.isProcessRunning}
                      disabled={disableActions &&
                        !b.isProcessRunning &&
                        !b.alwaysEnabled}
                      onclick={b.callback}
                    >
                      <div class="card-top">
                        <div class="card-label">{$t(b.option.label)}</div>
                        {#if b.isProcessRunning}
                          <span class="running-tag">● {$t("Run")}</span>
                        {:else}
                          <div class="play-box">
                            <svg
                              viewBox="0 0 24 24"
                              fill="currentColor"
                              width="10"
                              height="10"><path d="M8 5v14l11-7z" /></svg
                            >
                          </div>
                        {/if}
                      </div>
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .task-grid-container {
    display: flex;
    flex-direction: column;
    gap: 18px;
    height: 100%;
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 20px;
    margin-top: 18px;
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    border-radius: 10px;
    flex: 1;
    background: var(--bg-1);
    border: 1px solid var(--line);
  }

  .search-icon {
    color: var(--text-3);
  }

  .search-input {
    flex: 1;
    background: transparent;
    border: 0;
    outline: 0;
    color: var(--text-1);
    font-size: 13px;
    font-family: inherit;
  }

  .kbd {
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--text-3);
    padding: 2px 6px;
    border: 1px solid var(--line);
    border-radius: 4px;
    background: var(--bg-2);
  }

  .variant-toggle {
    display: flex;
    padding: 2px;
    border-radius: 10px;
    background: var(--bg-1);
    border: 1px solid var(--line);
  }

  .v-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    background: transparent;
    color: var(--text-3);
    transition: all var(--dur-1);
  }

  .v-btn.active {
    background: var(--bg-3);
    color: var(--text-1);
  }

  .view-content {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 20px;
  }

  .section {
    padding: 0 20px;
    margin-bottom: 24px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .section-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-3);
  }

  .section-line {
    height: 1px;
    flex: 1;
    background: var(--line-soft);
  }

  .section-count {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-4);
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 10px;
  }

  .task-card {
    position: relative;
    padding: 14px;
    border-radius: 12px;
    background: var(--bg-1);
    border: 1px solid var(--line);
    display: flex;
    flex-direction: column;
    gap: 10px;
    min-height: 80px;
    transition:
      transform var(--dur-1),
      border-color var(--dur-1),
      background var(--dur-1);
    text-align: left;
  }

  .task-card:not(:disabled):hover {
    border-color: color-mix(in oklab, var(--accent) 30%, var(--line));
  }

  .task-card:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .task-card.active {
    background: color-mix(in oklab, var(--accent) 10%, var(--bg-1));
    border-color: color-mix(in oklab, var(--accent) 45%, transparent);
  }

  .card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
  }

  .card-label {
    font-weight: 600;
    font-size: 13.5px;
    letter-spacing: -0.005em;
  }

  .running-tag {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-ghost);
    padding: 3px 6px;
    border-radius: 4px;
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .play-box {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    display: grid;
    place-items: center;
    background: var(--bg-2);
    color: var(--text-3);
  }

  .card-hint {
    font-size: 11.5px;
    color: var(--text-3);
    line-height: 1.45;
  }

  /* Palette View */
  .palette-view {
    padding: 14px 20px;
  }

  .palette-section {
    background: var(--bg-1);
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 20px;
  }

  .palette-cat {
    padding: 8px 14px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-3);
    background: var(--bg-2);
    border-bottom: 1px solid var(--line);
  }

  .palette-item {
    display: flex;
    width: 100%;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-bottom: 1px solid var(--line-soft);
    background: transparent;
    text-align: left;
    transition: background var(--dur-1);
  }

  .palette-item:last-child {
    border-bottom: none;
  }

  .palette-item:not(:disabled):hover {
    background: var(--bg-2);
  }

  .palette-item:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  .palette-item.active {
    background: var(--accent-ghost);
  }

  .item-icon {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    display: grid;
    place-items: center;
    background: var(--bg-3);
    color: var(--text-3);
    flex: 0 0 auto;
  }

  .palette-item.active .item-icon {
    background: var(--accent);
    color: white;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 999px;
    background: white;
  }

  .item-label {
    font-weight: 600;
    font-size: 13px;
  }

  .item-hint {
    font-size: 11px;
    color: var(--text-3);
  }

  .spacer {
    flex: 1;
  }

  .item-status {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    font-family: var(--font-mono);
  }

  .chevron {
    color: var(--text-4);
  }

  /* Accordion View */
  .accordion-view {
    padding: 14px 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .accordion-item {
    background: var(--bg-1);
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
  }

  .accordion-trigger {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    text-align: left;
  }

  .chevron-toggle {
    color: var(--text-3);
    transition: transform var(--dur-1);
  }

  .acc-title {
    font-weight: 600;
    font-size: 13.5px;
  }

  .acc-count {
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text-4);
  }

  .acc-content {
    padding: 0 10px 10px;
  }
</style>
