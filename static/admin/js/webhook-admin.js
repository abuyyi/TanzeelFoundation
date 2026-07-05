document.addEventListener('DOMContentLoaded', () => {
  const page = document.querySelector('.webhook-admin-page');
  if (!page) return;

  const searchInput = document.getElementById('webhook-live-search');
  const clearSearch = document.getElementById('webhook-clear-search');
  const filterToggle = document.querySelector('[data-filter-toggle]');
  const filterDrawer = document.getElementById('webhook-filter-drawer');
  const refreshButtons = document.querySelectorAll('.webhooks-refresh-btn');
  const exportButtons = document.querySelectorAll('.webhook-export-btn');
  const table = document.querySelector('.webhook-admin-page .results table');
  const rows = table ? Array.from(table.querySelectorAll('tbody tr')) : [];
  const toastContainer = document.querySelector('.webhook-toast-container');
  const jsonViewer = document.getElementById('webhook-json-viewer');
  const jsonSearch = document.getElementById('webhook-json-search');
  const copyJsonButton = document.querySelector('.copy-json-btn');
  const expandJsonButton = document.querySelector('.expand-json-btn');

  const showToast = (message, variant = 'info') => {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `webhook-toast ${variant}`;
    toast.innerHTML = `
      <span>${message}</span>
      <button type="button" class="webhook-toast-close" aria-label="Dismiss notification">×</button>
    `;

    toastContainer.appendChild(toast);
    const closeButton = toast.querySelector('.webhook-toast-close');
    closeButton.addEventListener('click', () => toast.remove());

    window.setTimeout(() => toast.classList.add('is-visible'), 20);
    window.setTimeout(() => toast.remove(), 3200);
  };

  const applyRowFilter = () => {
    if (!rows.length || !searchInput) return;

    const term = searchInput.value.trim().toLowerCase();

    rows.forEach((row) => {
      const rowText = row.textContent.toLowerCase();
      row.classList.toggle('is-hidden', Boolean(term) && !rowText.includes(term));
    });
  };

  if (searchInput) {
    searchInput.addEventListener('input', applyRowFilter);
  }

  if (clearSearch && searchInput) {
    clearSearch.addEventListener('click', () => {
      searchInput.value = '';
      applyRowFilter();
      searchInput.focus();
    });
  }

  if (filterToggle && filterDrawer) {
    filterToggle.addEventListener('click', () => {
      filterDrawer.classList.toggle('is-open');
    });
  }

  refreshButtons.forEach((button) => {
    button.addEventListener('click', () => {
      button.classList.add('is-loading');
      window.setTimeout(() => {
        button.classList.remove('is-loading');
        showToast(button.dataset.toast || 'Dashboard refreshed', 'success');
      }, 700);
    });
  });

  exportButtons.forEach((button) => {
    button.addEventListener('click', () => {
      button.classList.add('is-loading');
      window.setTimeout(() => {
        button.classList.remove('is-loading');
        showToast(button.dataset.toast || 'Export started', 'info');
      }, 700);
    });
  });

  document.querySelectorAll('.webhook-filter-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
      showToast('Filters updated', 'info');
    });
  });

  if (jsonViewer) {
    const payloadScript = document.getElementById('webhook-payload-data');
    if (payloadScript) {
      try {
        const payload = JSON.parse(payloadScript.textContent);
        jsonViewer.textContent = JSON.stringify(payload, null, 2);
      } catch (error) {
        jsonViewer.textContent = payloadScript.textContent;
      }
    }
  }

  if (jsonSearch && jsonViewer) {
    jsonSearch.addEventListener('input', () => {
      const term = jsonSearch.value.trim();
      const source = jsonViewer.textContent;
      if (!term) {
        jsonViewer.innerHTML = source.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return;
      }

      const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const highlighted = source.replace(new RegExp(escaped, 'gi'), (match) => `<mark>${match}</mark>`);
      jsonViewer.innerHTML = highlighted.replace(/</g, '&lt;').replace(/>/g, '&gt;');
    });
  }

  if (copyJsonButton && jsonViewer) {
    copyJsonButton.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(jsonViewer.textContent);
        showToast('Payload copied', 'success');
      } catch (error) {
        showToast('Copy failed', 'error');
      }
    });
  }

  if (expandJsonButton && jsonViewer) {
    expandJsonButton.addEventListener('click', () => {
      jsonViewer.classList.toggle('is-expanded');
      expandJsonButton.textContent = jsonViewer.classList.contains('is-expanded') ? 'Collapse' : 'Expand';
    });
  }

  if (table) {
    table.classList.add('is-loading');
    window.setTimeout(() => {
      table.classList.remove('is-loading');
      showToast('Webhook stream ready', 'success');
    }, 750);
  }
});
