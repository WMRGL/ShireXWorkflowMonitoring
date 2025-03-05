let isResizing = false;  // Declare isResizing before using it - MW
document.addEventListener("DOMContentLoaded", function() {
    var dropdowns = document.querySelectorAll('.navbar .dropdown');

    dropdowns.forEach(function(dropdown) {
        dropdown.addEventListener('mouseenter', function() {
            var menu = this.querySelector('.dropdown-menu');
            menu.classList.remove('show'); // Reset the animation - MW
            setTimeout(function() { // Reapply the class after a short delay - MW
                menu.classList.add('show');
            }, 10);
        });

        dropdown.addEventListener('mouseleave', function() {
            this.querySelector('.dropdown-menu').classList.remove('show');
        });
    });



    // Modal logic inside DOMContentLoaded - MW
    var modal = document.getElementById("font-size-modal");
    var btn = document.getElementById("settings-btn");
    var span = document.getElementsByClassName("close")[0];

    // Open the modal when the settings button is clicked - MW
    btn.onclick = function() {
        console.log("Settings button clicked");
        modal.style.display = "block";
    };

    // Close the modal when the 'x' is clicked - MW
    span.onclick = function() {
        modal.style.display = "none";
    };

    // Close the modal if clicked outside - MW
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Function to change font size - MW
    function changeFontSize(size) {
        var body = document.body;
        if(size === 'small') {
            body.style.fontSize = '12px';
        } else if(size === 'medium') {
            body.style.fontSize = '16px'; // This is typically the default size - MW
        } else if(size === 'large') {
            body.style.fontSize = '20px';
        }

        localStorage.setItem('preferredFontSize', size); // Stores the font size in local storage - MW
        modal.style.display = "none"; // Close the modal after selection - MW
    }

    // Function to change font style - MW
    function changeFontStyle(){
        var selectedFont = document.getElementById('font-style-select').value;
        document.documentElement.style.setProperty('--font-family', selectedFont);
        localStorage.setItem('selectedFontStyle', selectedFont);
    }

    // Apply saved font size on page load - MW
    function applySavedFontSize(){
        var savedSize = localStorage.getItem('preferredFontSize');
        if(savedSize){
            changeFontSize(savedSize);
        }
    }
    applySavedFontSize();

    // Apply saved font style on page load - MW
    document.addEventListener('DOMContentLoaded', (event) => {
        var selectedFont = localStorage.getItem('selectedFontStyle');
        if(selectedFont){
            document.documentElement.style.setProperty('--font-family', selectedFont);
            document.getElementById('font-style-select').value = selectedFont;
        }
    });
});

console.log("Modal:", modal); // Should not be null - MW
console.log("Button:", btn);  // Should not be null - MW
console.log("Close button:", span); // Should not be null - MW



window.addEventListener('load', function() {
            document.getElementById('txtPageNumber').value = '1';
        })

        document.addEventListener("DOMContentLoaded", function () {
            var indicationDropdown = document.getElementById('ddlCriteriaDiseaseIndication1');

            if (indicationDropdown) {  // Check if the element exists - MW
                indicationDropdown.addEventListener('change', function () {
                    if (IsFormValid()) {
                        document.getElementById('ddlCriteriaReasonForDiseaseIndication1').value = '';
                        document.getElementById('ddlCriteriaReasonForDiseaseIndication2').value = '';
                        document.getElementById('ddlCriteriaReasonForDiseaseIndication3').value = '';
                        DoPostBack();
                    }
                });
            }
        });

        document.addEventListener("DOMContentLoaded", function () {
            var indicationDropdown2 = document.getElementById('ddlCriteriaDiseaseIndication2');

            if (indicationDropdown2) { // ✅ Check if element exists before adding event listener - MW
                indicationDropdown2.addEventListener('change', function () {
                    if (IsFormValid()) {
                        var reason1 = document.getElementById('ddlCriteriaReasonForDiseaseIndication1');
                        var reason2 = document.getElementById('ddlCriteriaReasonForDiseaseIndication2');
                        var reason3 = document.getElementById('ddlCriteriaReasonForDiseaseIndication3');

                        if (reason1) reason1.value = '';
                        if (reason2) reason2.value = '';
                        if (reason3) reason3.value = '';

                        DoPostBack();
                    }
                });
            } else {
                console.warn("⚠️ Element with ID 'ddlCriteriaDiseaseIndication2' not found. Skipping event listener.");
            }
        });



        document.addEventListener("DOMContentLoaded", function () {
            var indicationDropdown3 = document.getElementById('ddlCriteriaDiseaseIndication3');

            if (indicationDropdown3) {  // ✅ Check if element exists before adding event listener - MW
                indicationDropdown3.addEventListener('change', function () {
                    if (IsFormValid()) {
                        var reason1 = document.getElementById('ddlCriteriaReasonForDiseaseIndication1');
                        var reason2 = document.getElementById('ddlCriteriaReasonForDiseaseIndication2');
                        var reason3 = document.getElementById('ddlCriteriaReasonForDiseaseIndication3');

                        if (reason1) reason1.value = '';
                        if (reason2) reason2.value = '';
                        if (reason3) reason3.value = '';

                        DoPostBack();
                    }
                });
            } else {
                console.warn("⚠️ Element with ID 'ddlCriteriaDiseaseIndication3' not found. Skipping event listener.");
            }
        });


        document.addEventListener("DOMContentLoaded", function () {
            var btnPageFirst = document.getElementById('btnPageFirst');
            var btnPagePrevious = document.getElementById('btnPagePrevious');
            var btnPageNext = document.getElementById('btnPageNext');
            var btnPageLast = document.getElementById('btnPageLast');

            if (btnPageFirst) {
                btnPageFirst.addEventListener('click', function () {
                    DoSubmitFirstPage();
                });
            } else {
                console.warn("⚠️ Element with ID 'btnPageFirst' not found. Skipping event listener.");
            }

            if (btnPagePrevious) {
                btnPagePrevious.addEventListener('click', function () {
                    DoSubmitPreviousPage();
                });
            } else {
                console.warn("⚠️ Element with ID 'btnPagePrevious' not found. Skipping event listener.");
            }

            if (btnPageNext) {
                btnPageNext.addEventListener('click', function () {
                    DoSubmitNextPage();
                });
            } else {
                console.warn("⚠️ Element with ID 'btnPageNext' not found. Skipping event listener.");
            }

            if (btnPageLast) {
                btnPageLast.addEventListener('click', function () {
                    DoSubmitLastPage();
                });
            } else {
                console.warn("⚠️ Element with ID 'btnPageLast' not found. Skipping event listener.");
            }
        });


        function DoPostBack() {
            document.getElementById('formSearch').submit();
        }

        function DoSubmitFirstPage() {
            _pageNumber = document.getElementById('txtPageNumber');
            _pageNumber.value = '1';

            document.getElementById('formSearch').submit();
        }

        function DoSubmitPreviousPage() {
            var _pageNumber = document.getElementById('txtPageNumber');
            if (workflowCases != null) {
                if (workflowCases.has_previous) {
                    _pageNumber.value = workflowCases - 1;
                } else {
                    _pageNumber.value = '1';
                    print("Is not Null prev")
                }
            } else {
                _pageNumber.value = '1';
                print("Is Null prev")
            }
            document.getElementById('formSearch').submit();
        }


        function DoSubmitNextPage() {
            var _pageNumber = document.getElementById('txtPageNumber');
            console.log('Current Page:', _pageNumber.value);
            console.log('workflowCases:', workflowCases);

            if (workflowCases != null && workflowCases.has_next) {
                _pageNumber.value = parseInt(_pageNumber.value) + 1;
                console.log('Going to Next Page:', _pageNumber.value);
            } else {
                _pageNumber.value = '1';
                console.log('No Next Page, Resetting to 1');
            }
            document.getElementById('formSearch').submit();
        }



        function DoSubmitLastPage() {
            var _pageNumber = document.getElementById('txtPageNumber');

            if (workflowCases != null) {
                if (workflowCases.has_next) {
                    _pageNumber.value = "10"; // assuming workflowCases.paginator.num_pages is 10 - MW
                } else {
                    _pageNumber.value = '1';
                }
            } else {
                _pageNumber.value = '1';
            }
            document.getElementById('formSearch').submit();
        }

        function IsFormValid() {

            let _retVal = true
            let _errorMessage = ''

            let _indicationDisease1 = Nz(document.getElementById('ddlCriteriaDiseaseIndication1').value,'');
            let _indicationDisease2 = Nz(document.getElementById('ddlCriteriaDiseaseIndication2').value,'');
            let _indicationDisease3 = Nz(document.getElementById('ddlCriteriaDiseaseIndication3').value,'');

            let _reason1 = Nz(document.getElementById('ddlCriteriaReasonForDiseaseIndication1').value,'');
            let _reason2 = Nz(document.getElementById('ddlCriteriaReasonForDiseaseIndication2').value,'');
            let _reason3 = Nz(document.getElementById('ddlCriteriaReasonForDiseaseIndication3').value,'');

            if (_indicationDisease2 != '' && _indicationDisease1 == '')
            {
                _errorMessage = _errorMessage + 'You must enter the indication search criteria in order \n';
            }
            else
            {
                if (_indicationDisease3 != '' && _indicationDisease1 == '')
                {
                    _errorMessage = _errorMessage + 'You must enter the indication search criteria in order \n';
                }
                else
                {
                    if (_indicationDisease3 != '' && _indicationDisease2 == '')
                    {
                        _errorMessage = _errorMessage + 'You must enter the indication search criteria in order \n';
                    }
                }
            }

            if (_reason2 != '' && _reason1 == '')
            {
                _errorMessage = _errorMessage + 'You must enter the reason search criteria in order \n';
            }
            else
            {
                if (_reason3 != '' && _reason1 == '')
                {
                    _errorMessage = _errorMessage + 'You must enter the reason search criteria in order \n';
                }
                else
                {
                    if (_reason3 != '' && _reason2 == '')
                    {
                        _errorMessage = _errorMessage + 'You must enter the reason search criteria in order \n';
                    }
                }
            }

            if (_errorMessage != '') {
                _retVal = false;
                window.alert(_errorMessage);
            }

            return _retVal;
        }

        function Nz (_object, _defaultValue) {
            if (_object == null || _object == undefined)
            {
                _object = _defaultValue;
            }
            return _object
        }


        document.addEventListener("DOMContentLoaded", function ()
        {
            document.body.addEventListener("click", function (event)
            {
                if (event.target.classList.contains("claim-btn"))
                {
                    console.log("Claim button clicked:", event.target);

                    let labno = event.target.dataset.labno;
                    let workflowName = event.target.dataset.workflow;

                    console.log("Lab Number:", labno);
                    console.log("Workflow Name:", workflowName);

                    if (!labno || !workflowName)
                    {
                        alert("Error: Missing lab number or workflow name.");
                        return;
                    }

                    let url = `/Molecular/Allocate/${encodeURIComponent(labno)}/${encodeURIComponent(workflowName)}/`;

                    console.log("Navigating to URL:", url);
                    window.location.href = url;
                }
            });
        });



        function SortTable(n){
            //Doing it this way means it can only sort what's on the screen, but it'll reduce the SQL sproc calls - MW
           var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
           table = document.getElementById("ResultsTable");
           switching=true;
           dir = "asc";
           while(switching){
               switching = false;
               rows = table.rows;
               for (i=1; i < rows.length-1; i++){
                   shouldSwitch = false;
                   x = rows[i].getElementsByTagName("TD")[n];
                   y = rows[i+1].getElementsByTagName("TD")[n];
                   if (dir == "asc"){
                       if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()){
                           shouldSwitch = true;
                           break;
                       }
                   }else if (dir="desc"){
                       if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()){
                           shouldSwitch = true;
                           break;
                       }
                   }
               }
               if(shouldSwitch){
                   rows[i].parentNode.insertBefore(rows[i+1], rows[i]);
                   switching = true;
                   switchcount++;
               }else{
                   if(switchcount==0 && dir == "asc"){
                       dir = "desc";
                       switching = true;
                   }
               }
           }
        }

        document.addEventListener("DOMContentLoaded", function() {
        var dropdowns = document.querySelectorAll('.navbar .dropdown');

        dropdowns.forEach(function(dropdown) {
            dropdown.addEventListener('mouseenter', function() {
                var menu = this.querySelector('.dropdown-menu');
                menu.classList.remove('show'); // Reset the animation - MW
                setTimeout(function() { // Reapply the class after a short delay - MW
                    menu.classList.add('show');
                }, 10);
            });

            dropdown.addEventListener('mouseleave', function() {
                this.querySelector('.dropdown-menu').classList.remove('show');
            });
        });

    });


    // Get the modal - MW
    var modal = document.getElementById("font-size-modal");

    // Get the button that opens the modal - MW
    var btn = document.getElementById("settings-btn");

    // Get the <span> element that closes the modal - MW
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks the button, open the modal - MW
    btn.onclick = function() {
        console.log("Settings button clicked");
      modal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal - MW
    span.onclick = function() {
      modal.style.display = "none";
    }

    // When the user clicks anywhere outside the modal, close it - MW
    window.onclick = function(event) {
        console.log("Close button clicked")
      if (event.target == modal) {
        modal.style.display = "none";
      }
    }

    // Function to change font size - MW
    function changeFontSize(size) {
      var body = document.body;
      if(size === 'small') {
        body.style.fontSize = '12px';
      } else if(size === 'medium') {
        body.style.fontSize = '16px'; // This is typically the default size - MW
      } else if(size === 'large') {
        body.style.fontSize = '20px';
      }

      localStorage.setItem('preferredFontSize', size); // Stores the font size in local storage - MW
      modal.style.display = "none"; // Close the modal after selection - MW
    }

    function changeFontStyle(){
        // Selects the font from the list - MW
        var selectedFont = document.getElementById('font-style-select').value;
        document.documentElement.style.setProperty('--font-family', selectedFont);
        localStorage.setItem('selectedFontStyle', selectedFont);

        var isDyslexiaAidChecked = document.getElementById('dyslexia-checkbox').checked;

        if(isDyslexiaAidChecked) {
            document.body.style.letterSpacing = "5px";
            document.body.style.wordSpacing = "35px";
            document.body.classList.add('dyslexic');
        }else{
            document.body.classList.remove('dyslexic');
        }
        localStorage.setItem('isDyslexiaAidChecked', isDyslexiaAidChecked);
    }

    function applySavedFontSize(){
        // Applies these fonts to the page - MW
        var savedSize = localStorage.getItem('preferredFontSize');
        if(savedSize){
            changeFontSize(savedSize);
        }
    }
    // Call applySavedFontSize when the page loads - MW
    document.addEventListener('DOMContentLoaded', applySavedFontSize);
    document.addEventListener('DOMContentLoaded', (event) => {
        var selectedFont = localStorage.getItem('selectedFontStyle');
        if(selectedFont){
            document.documentElement.style.setProperty('--font-family', selectedFont);
            document.getElementById('font-style-select').value = selectedFont;
        }

        var isDyslexiaAidChecked = localStorage.getItem('isDyslexiaAidChecked') === 'true';
        if (isDyslexiaAidChecked) {
            document.body.classList.add('dyslexic');
        } else {
            document.body.classList.remove('dyslexic');
        }
        document.addEventListener("DOMContentLoaded", function () {
            let checkbox = document.getElementById("dyslexia-checkbox");
            if (checkbox) {
                checkbox.checked = localStorage.getItem("isDyslexiaAidChecked") === "true";
            } else {
                console.warn("⚠️ Element with ID 'dyslexia-checkbox' not found.");
            }
        });
    })

    // This closes the settings window - MW
    document.addEventListener("DOMContentLoaded", function () {
        const table = document.getElementById('ResultsTable');

        if (!table) {
            console.warn("⚠️ Element with ID 'ResultsTable' not found. Skipping table resizing.");
            return;  // Stop execution if table is missing - MW
        }

        let isResizing = false;
        let lastX = 0;
        let currentTh = null;

        table.querySelectorAll('th').forEach(th => {
            const div = document.createElement('div');
            div.classList.add('resize-handle');
            th.appendChild(div);

            div.addEventListener('mousedown', (e) => {
                isResizing = true;
                lastX = e.clientX;
                currentTh = th;
                document.body.style.cursor = 'col-resize';
            });
        });
    });


      document.addEventListener('mousemove', (e) => {
        let isResizing = false; // Define it before using it - MW
        document.addEventListener("mousemove", (e) => {
            if (isResizing) {
                console.log("Resizing in progress...");
            }
        });
      });

      document.addEventListener('mouseup', () => {
        if (isResizing) {
          isResizing = false;
          document.body.style.cursor = 'default';
        }
    });



    function CloseForm()
    {
            window.close();
    }


    function submitPage(pageNumber){
        if(pageNumber < 1){
            pageNumber = 1; // Ensures the page number doesn't go below 1 - MW
        }
        document.getElementById('txtPageNumber').value = pageNumber;
        document.getElementById('formSearch').submit(); // Submit the form to the server - MW
    }


    // Get the number of columns in the <thead> - MW
    var columnCount = document.querySelectorAll('#ResultsTable thead th').length;
    console.log('Number of columns in <thead>: ', columnCount);

    // Get all rows in the <tbody> - MW
    var rows = document.querySelectorAll('#ResultsTable tbody tr');

    // Check each row's column count - MW
    rows.forEach(function(row, index) {
        var cellCount = row.querySelectorAll('td').length;
        console.log('Row ' + (index + 1) + ' column count: ', cellCount);

        if (cellCount !== columnCount) {
            console.warn('Row ' + (index + 1) + ' has a mismatch! Expected: ' + columnCount + ', Found: ' + cellCount);
        }
    });


    window.onload = function() {
        // Get today's date - MW
        var today = new Date();

        // Calculate the date 5 months ago - MW
        var fiveMonthsAgo = new Date();
        fiveMonthsAgo.setMonth(today.getMonth() - 5);

        // Adjust for months where the date exceeds the valid range (i.e., if subtracting months causes invalid dates) - MW
        if (today.getDate() !== fiveMonthsAgo.getDate()) {
            fiveMonthsAgo.setDate(0); // Set to the last day of the previous month in case of overflow - MW
        }

        // Format the dates as YYYY-MM-DD - MW
        var day = ("0" + today.getDate()).slice(-2);
        var month = ("0" + (today.getMonth() + 1)).slice(-2);
        var formattedToday = today.getFullYear() + "-" + month + "-" + day;

        var dayFiveMonthsAgo = ("0" + fiveMonthsAgo.getDate()).slice(-2);
        var monthFiveMonthsAgo = ("0" + (fiveMonthsAgo.getMonth() + 1)).slice(-2);
        var formattedFiveMonthsAgo = fiveMonthsAgo.getFullYear() + "-" + monthFiveMonthsAgo + "-" + dayFiveMonthsAgo;

        // Set the value of the date input fields - MW
        document.getElementById('txtCriteriaDateFrom').value = formattedFiveMonthsAgo;
        document.getElementById('txtCriteriaDateTo').value = formattedToday;
    };

    let debounceTimer;
    function throttleSubmitPage(pageNumber) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => submitPage(pageNumber), 200);
    }
