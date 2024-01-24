document.addEventListener('DOMContentLoaded', function () {

  const drawerButton = document.getElementById('filterDropdownButton');
  const drawerNavigation = document.getElementById('drawerNavigation');
  const closeButton = document.querySelector('[data-drawer-hide="drawer-navigation"]');

  drawerButton.addEventListener('click', function () {
    drawerNavigation.classList.toggle('hidden');
    setTimeout(function () {
      drawerNavigation.classList.toggle('-translate-x-full');
    }, 0);
  });

  closeButton.addEventListener('click', function () {
    drawerNavigation.classList.add('-translate-x-full');
    setTimeout(function () {
      drawerNavigation.classList.add('hidden');
    }, 300); 
  });

    function openModal(modalId) {
      const modal = document.getElementById(modalId);
      modal.classList.remove('fadeOut');
      modal.classList.add('fadeIn');
      modal.style.display = 'flex';
    }

    function closeModal(modalId) {
      const modal = document.getElementById(modalId);

      setTimeout(() => {
        modal.style.display = 'none';
      }, 50);
    }

    document.getElementById('openImport').addEventListener('click', function () {
      openImport('importModal');
      closeModal('exportModal'); 
    });

    document.getElementById('openExport').addEventListener('click', function () {
      openModal('exportModal');
      closeModal('importModal'); 
    });

    
    document.getElementById('cancelImportButton').addEventListener('click', function () {
      closeModal('importModal');
    });
    
    
    document.getElementById('cancelExportButton').addEventListener('click', function () {
      closeModal('exportModal');
    });
    
    document.getElementById('openFilter').addEventListener('click', function () {
    openFilter('filterModal');
    closeModal('exportModal');
  });

      document.getElementById('cancelFilterButton').addEventListener('click', function () {
      closeModal('filterModal');
    });
  });
  

  document.querySelector('#filterDropdownButton').addEventListener('click', function () {
    document.querySelector('#filterDropdown').classList.toggle('hidden');
  });

     $(document).ready(function () {
      function toggleSortDirection($th) {
        $th.toggleClass('asc desc');
      }

      function sortTable($table, columnIndex, direction) {
        const rows = $table.find('tbody tr').get();

        rows.sort(function (a, b) {
          const keyA = $(a).find('td').eq(columnIndex).text();
          const keyB = $(b).find('td').eq(columnIndex).text();

          if (direction === 'asc') {
            return keyA.localeCompare(keyB);
          } else {
            return keyB.localeCompare(keyA);
          }
        });

        $.each(rows, function (index, row) {
          $table.children('tbody').append(row);
        });
      }

      $('.sortable').click(function () {
        const $th = $(this);
        const columnIndex = $th.index();
        const direction = $th.hasClass('asc') ? 'desc' : 'asc';

        toggleSortDirection($th);
        sortTable($th.closest('table'), columnIndex, direction);
      });
    });
  