<script lang="ts">
  import { check, Update } from "@tauri-apps/plugin-updater";
  import { Progress } from "@skeletonlabs/skeleton-svelte";
  import { onDestroy, onMount } from "svelte";
  import Download from "$lib/components/icons/lucide/Download.svelte";
  import { Dialog, Portal } from "@skeletonlabs/skeleton-svelte";
  import IconX from "$lib/components/icons/feather/IconX.svelte";
  import { t } from "$lib/i18n/i18n";
  import { emit } from "@tauri-apps/api/event";
  import { appSettings } from "$lib/stores";
  import { get } from "svelte/store";
  import { toaster } from "$lib/toast/toaster-svelte";

  let checkUpdateTimeout: ReturnType<typeof setTimeout> | undefined;
  let update: Update | null = $state(null);

  // Modal
  let isUpdating: boolean = $state(false);
  let isDialogOpen: boolean = $state(true);

  // Download
  let totalSize: number = $state(0);
  let downloaded: number = $state(0);
  let downloadProgress: number = $state(0);

  async function checkUpdate() {
    if (isUpdating) {
      return;
    }
    try {
      const firstUpdateDetected = update === null;
      update = await check({ timeout: 5000 });
      if (update && firstUpdateDetected) {
        isDialogOpen = true;

        const settings = get(appSettings);
        if (settings?.notifications?.desktop_notifications) {
          toaster.info({
            title: get(t)("Update Available"),
            description: get(t)(
              "A new version of AdbAutoPlayer is ready to install.",
            ),
          });
        }
      }
    } catch (e) {
      console.error(e);
    }

    checkUpdateTimeout = setTimeout(checkUpdate, 1000 * 60 * 15); // wait 15 minutes;
  }

  async function startUpdate(): Promise<void> {
    update = (await check({ timeout: 5000 })) ?? update;
    if (!update) {
      return;
    }

    isUpdating = true;

    await update.downloadAndInstall((event) => {
      switch (event.event) {
        case "Started":
          totalSize = event.data.contentLength ?? 0;
          downloaded = 0;
          downloadProgress = 0;
          break;

        case "Progress":
          downloaded += event.data.chunkLength;
          if (totalSize > 0) {
            downloadProgress = (downloaded / totalSize) * 100;
          }
          break;

        case "Finished":
          downloadProgress = 100;
          emit("kill-python")
            .then(() => {
              console.log("Kill signal sent to Python.");
            })
            .catch((err) => {
              console.error("Failed to send kill signal:", err);
            });
          break;
      }
    });
  }

  onMount(() => {
    // Only check for updates if we are running in a Tauri environment
    if ((window as any).__TAURI_INTERNALS__) {
      checkUpdateTimeout = setTimeout(checkUpdate, 500);
    }
  });

  onDestroy(() => {
    clearTimeout(checkUpdateTimeout);
  });
</script>

{#if update}
  <Dialog
    closeOnInteractOutside={false}
    open={isDialogOpen}
    onOpenChange={(details) => (isDialogOpen = details.open)}
  >
    <Dialog.Trigger
      class="fixed top-0 right-8 z-50 m-2 cursor-pointer select-none {isUpdating
        ? 'text-primary-300'
        : ''}"
    >
      <Download size={24} strokeWidth={2} />
    </Dialog.Trigger>
    <Portal>
      <Dialog.Backdrop class="bg-surface-50-950/50 fixed inset-0 z-50" />
      <Dialog.Positioner
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <Dialog.Content
          class="card bg-surface-100-900 w-full max-w-xl translate-y-[100px] space-y-4 p-4 opacity-0 shadow-xl transition transition-discrete data-[state=open]:translate-y-0 data-[state=open]:opacity-100 starting:data-[state=open]:translate-y-[100px] starting:data-[state=open]:opacity-0"
        >
          <header class="mb-4 flex items-center justify-between">
            {#if !isUpdating}
              <Dialog.Title class="text-2xl font-bold"
                >{$t("Update")}</Dialog.Title
              >
            {:else}
              <Dialog.Title class="text-2xl font-bold"
                >{$t("The App will restart automatically.")}</Dialog.Title
              >
            {/if}
            <Dialog.CloseTrigger class="btn-icon hover:preset-tonal">
              <IconX size={16} />
            </Dialog.CloseTrigger>
          </header>

          {#if !isUpdating}
            <div class="space-y-4">
              <p class="text-sm opacity-70">
                {$t(
                  "A new version of AdbAutoPlayer is available. Would you like to download and install it now?",
                )}
              </p>
              <div class="flex items-center gap-2 text-sm font-medium">
                <span class="opacity-50">{$t("Version")}:</span>
                <span class="text-primary-500">{update?.version}</span>
              </div>

              {#if update?.body}
                <div class="rounded-lg bg-black/20 p-4">
                  <div
                    class="mb-2 text-xs font-bold tracking-wider uppercase opacity-50"
                  >
                    {$t("Changelog")}
                  </div>
                  <div
                    class="max-h-48 overflow-y-auto text-sm leading-relaxed whitespace-pre-wrap"
                  >
                    {update.body}
                  </div>
                </div>
              {/if}
            </div>

            <footer class="bg-surface-100-900 sticky bottom-0 mt-4 py-2">
              <button
                class="btn-primary btn preset-filled-primary-100-900 hover:preset-filled-primary-500 w-full p-2"
                onclick={startUpdate}
              >
                {$t("Download and Install")}
              </button>
            </footer>
          {:else}
            <div class="flex items-center justify-center">
              <Progress
                value={Math.round(downloadProgress)}
                max={100}
                class="relative mb-4 flex w-fit justify-center"
              >
                <div class="absolute inset-0 flex items-center justify-center">
                  <Progress.ValueText />
                </div>
                <Progress.Circle>
                  <Progress.CircleTrack />
                  <Progress.CircleRange />
                </Progress.Circle>
              </Progress>
            </div>
          {/if}
        </Dialog.Content>
      </Dialog.Positioner>
    </Portal>
  </Dialog>
{/if}
