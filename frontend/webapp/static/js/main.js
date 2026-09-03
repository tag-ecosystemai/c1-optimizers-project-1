document.addEventListener("DOMContentLoaded", () => {
  initSidebarToggle();
  initFlashDismiss();
  initUploadForm();
  initClassifyForm();
  initQueueSelect();
});

/** Desktop: collapse the sidebar to an icon rail (persisted). Mobile: open/close it as a drawer. */
function initSidebarToggle() {
  const body = document.body;
  const desktopToggle = document.getElementById("sidebarToggle");
  const mobileToggle = document.getElementById("sidebarToggleMobile");
  const backdrop = document.getElementById("sidebarBackdrop");

  const collapsed = localStorage.getItem("sidebar-collapsed") === "true";
  body.classList.toggle("sidebar-collapsed", collapsed);
  if (desktopToggle) desktopToggle.setAttribute("aria-expanded", String(!collapsed));

  desktopToggle?.addEventListener("click", () => {
    const isCollapsed = body.classList.toggle("sidebar-collapsed");
    localStorage.setItem("sidebar-collapsed", String(isCollapsed));
    desktopToggle.setAttribute("aria-expanded", String(!isCollapsed));
  });

  function closeMobileDrawer() {
    body.classList.remove("sidebar-open");
    mobileToggle?.setAttribute("aria-expanded", "false");
  }

  mobileToggle?.addEventListener("click", () => {
    const isOpen = body.classList.toggle("sidebar-open");
    mobileToggle.setAttribute("aria-expanded", String(isOpen));
  });

  backdrop?.addEventListener("click", closeMobileDrawer);
}

/** Dismiss buttons on flash message alerts. */
function initFlashDismiss() {
  document.querySelectorAll(".alert-dismiss").forEach((btn) => {
    btn.addEventListener("click", () => btn.closest(".alert")?.remove());
  });
}

/** Bulk upload: show the chosen filename, enable submit, support drag-and-drop. */
function initUploadForm() {
  const input = document.getElementById("csvFile");
  const submit = document.getElementById("uploadSubmit");
  const filenameEl = document.getElementById("dropzoneFilename");
  const dropzone = document.getElementById("dropzone");
  if (!input || !submit) return;

  function updateFromFiles(files) {
    if (files && files.length > 0) {
      filenameEl.textContent = files[0].name;
      filenameEl.hidden = false;
      submit.disabled = false;
    } else {
      filenameEl.hidden = true;
      submit.disabled = true;
    }
  }

  input.addEventListener("change", () => updateFromFiles(input.files));

  if (dropzone) {
    ["dragenter", "dragover"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.add("dropzone-active");
      });
    });

    ["dragleave", "drop"].forEach((evt) => {
      dropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        dropzone.classList.remove("dropzone-active");
      });
    });

    dropzone.addEventListener("drop", (e) => {
      const files = e.dataTransfer && e.dataTransfer.files;
      if (files && files.length > 0) {
        input.files = files;
        updateFromFiles(files);
      }
    });
  }
}

/** Classify: keep the button disabled until there's a message to send. */
function initClassifyForm() {
  const textarea = document.getElementById("messageInput");
  const submit = document.getElementById("classifySubmit");
  if (!textarea || !submit) return;

  const toggle = () => {
    submit.disabled = textarea.value.trim().length === 0;
  };
  textarea.addEventListener("input", toggle);
  toggle();
}

/** Team queues: switching the dropdown reloads the page with ?queue=... */
function initQueueSelect() {
  const select = document.getElementById("queueSelect");
  const form = document.getElementById("queueForm");
  if (!select || !form) return;

  select.addEventListener("change", () => form.submit());
}
